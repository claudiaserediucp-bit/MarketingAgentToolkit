from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from .config_loader import load_agents_config, load_clients, load_global_config
from .llm import LLMClient
from .logger_csv import append_log, count_success_for_day
from .mcp_client import MCPClient
from .models import AgentPersona, Campaign, ClientConfig, GlobalConfig
from .scheduler import get_due_slots_for_client

logger = logging.getLogger(__name__)


class SocialMediaAgent:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.global_cfg: GlobalConfig = load_global_config(base_dir)
        self.agents_cfg = load_agents_config(base_dir)
        self.clients = load_clients(base_dir)
        self.llm_client = LLMClient(self.global_cfg.llm)
        self.log_path = Path(self.global_cfg.logging.file)

    def _get_persona(self, agent_id: str) -> AgentPersona:
        if agent_id not in self.agents_cfg.agents:
            raise KeyError(f"Agent persona '{agent_id}' not found in agents.json")
        return self.agents_cfg.agents[agent_id]

    def _get_campaign(self, client: ClientConfig, campaign_name: str) -> Campaign:
        if campaign_name not in client.campaigns:
            raise KeyError(f"Campaign '{campaign_name}' not found for client {client.client_id}")
        return client.campaigns[campaign_name]

    async def run_cycle_once(self, now: datetime) -> None:
        mcp_cfg = self.global_cfg.facebook_mcp
        async with MCPClient(mcp_cfg) as mcp:
            for client in self.clients:
                persona = self._get_persona(client.agent_id)
                tz = ZoneInfo(client.tz_name)
                local_now = now.astimezone(tz)

                due_slots = get_due_slots_for_client(
                    client,
                    now,
                    log_path=self.log_path,
                    tolerance_minutes=self.global_cfg.scheduler.tolerance_minutes,
                    platform="facebook",
                )

                for slot, platform in due_slots:
                    todays_posts = count_success_for_day(self.log_path, local_now.date(), client.client_id, platform)
                    if todays_posts >= client.guardrails.max_posts_per_day:
                        logger.info(
                            "Guardrail reached for client %s: %s posts on %s",
                            client.client_id,
                            todays_posts,
                            local_now.date(),
                        )
                        continue

                    campaign = self._get_campaign(client, slot.campaign)
                    try:
                        message = self.llm_client.generate_post_text(persona, client, campaign, local_now)
                        result = await mcp.post_text(
                            page_id=client.platforms.facebook.page_id or "",
                            message=message,
                        )
                        status = "success" if result.success else "failed"
                        append_log(
                            self.log_path,
                            timestamp=result.timestamp,
                            client_id=client.client_id,
                            slot_id=slot.id,
                            campaign=slot.campaign,
                            platform=platform,
                            page_id=result.page_id,
                            post_id=result.post_id,
                            status=status,
                            error=result.error,
                        )
                    except Exception as exc:  # noqa: BLE001
                        logger.exception("Failed to post for client %s slot %s", client.client_id, slot.id)
                        append_log(
                            self.log_path,
                            timestamp=datetime.utcnow(),
                            client_id=client.client_id,
                            slot_id=slot.id,
                            campaign=slot.campaign,
                            platform=platform,
                            page_id=client.platforms.facebook.page_id or "",
                            post_id=None,
                            status="failed",
                            error=str(exc),
                        )


async def run_once(base_dir: Path, now: datetime) -> None:
    agent = SocialMediaAgent(base_dir=base_dir)
    await agent.run_cycle_once(now)

