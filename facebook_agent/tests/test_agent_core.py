import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

import facebook_agent.agent.agent_core as agent_core_module
from facebook_agent.agent.models import PostResult


class FakeLLM:
    def __init__(self, cfg):
        self.cfg = cfg

    def generate_post_text(self, persona, client, campaign, now):
        return f"{client.display_name}-{campaign.objective}"


class FakeMCP:
    def __init__(self, cfg):
        self.cfg = cfg
        self.called = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def post_text(self, page_id: str, message: str):
        self.called.append((page_id, message))
        return PostResult(success=True, post_id="p123", page_id=page_id, error=None)


def _write_configs(base: Path, log_path: Path):
    (base / "config" / "clients").mkdir(parents=True)
    global_cfg = {
        "timezone": "Europe/Bucharest",
        "llm": {"provider": "openai", "model": "gpt", "max_tokens": 10, "temperature": 0.1},
        "scheduler": {"tick_minutes": 30, "tolerance_minutes": 15},
        "facebook_mcp": {"command": "echo", "args": ["ok"]},
        "logging": {"type": "csv", "file": str(log_path)},
    }
    (base / "config" / "global.json").write_text(json.dumps(global_cfg), encoding="utf-8")
    (base / "config" / "agents.json").write_text(
        json.dumps(
            {"agents": {"a1": {"name": "A", "language": "ro", "tone": "calm", "style_notes": "s", "content_mix": "mix", "max_chars": 200}}}
        ),
        encoding="utf-8",
    )
    client_cfg = {
        "client_id": "c1",
        "display_name": "Test",
        "agent_id": "a1",
        "business": {"niche": "n", "city": "c", "language": "ro"},
        "platforms": {"facebook": {"enabled": True, "page_id": "p1"}, "instagram": {"enabled": False, "ig_business_id": None}},
        "schedule": {
            "timezone": "Europe/Bucharest",
            "slots": [{"id": "s1", "days_of_week": [1, 2, 3, 4, 5, 6, 7], "time": "09:00", "platforms": ["facebook"], "campaign": "camp"}],
        },
        "campaigns": {"camp": {"objective": "o", "notes": "n"}},
        "guardrails": {"max_posts_per_day": 5},
    }
    (base / "config" / "clients" / "c1.json").write_text(json.dumps(client_cfg), encoding="utf-8")


def test_agent_run_cycle(monkeypatch, tmp_path: Path):
    base = tmp_path / "facebook_agent"
    log_path = base / "log.csv"
    _write_configs(base, log_path)

    # patch LLM and MCP
    monkeypatch.setattr(agent_core_module, "LLMClient", FakeLLM)
    fake_mcp_instance = FakeMCP(cfg=None)

    async def fake_mcp_factory(cfg):
        return fake_mcp_instance

    class FakeMCPContext:
        def __init__(self, cfg):
            self.cfg = cfg
            self.inner = fake_mcp_instance

        async def __aenter__(self):
            return self.inner

        async def __aexit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(agent_core_module, "MCPClient", FakeMCPContext)

    agent = agent_core_module.SocialMediaAgent(base_dir=base)
    now = datetime(2026, 1, 2, 7, 5, tzinfo=timezone.utc)

    asyncio.run(agent.run_cycle_once(now))

    assert log_path.exists()
    content = log_path.read_text(encoding="utf-8")
    assert "c1" in content
    assert "s1" in content

