from __future__ import annotations

import os
from datetime import datetime

from openai import OpenAI

from .models import AgentPersona, Campaign, ClientConfig, LLMConfig


class LLMClient:
    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required")
        self.client = OpenAI(api_key=api_key)

    def generate_post_text(
        self, persona: AgentPersona, client: ClientConfig, campaign: Campaign, now: datetime
    ) -> str:
        prompt = (
            "You are a concise social media copywriter.\n"
            f"Brand: {client.display_name}\n"
            f"Niche: {client.business.niche}\n"
            f"City: {client.business.city}\n"
            f"Language: {persona.language}\n"
            f"Tone: {persona.tone}\n"
            f"Style notes: {persona.style_notes}\n"
            f"Content mix: {persona.content_mix or 'short updates'}\n"
            f"Campaign: {campaign.objective}. Notes: {campaign.notes or 'n/a'}\n"
            f"Date/time: {now.isoformat()}\n"
            f"Max characters: {persona.max_chars}\n"
            "Write ONE post message only. No hashtags unless critical. No emojis unless implied by tone.\n"
        )

        completion = self.client.chat.completions.create(
            model=self.cfg.model,
            max_tokens=self.cfg.max_tokens,
            temperature=self.cfg.temperature,
            messages=[
                {"role": "system", "content": "You write short, on-brand Facebook posts."},
                {"role": "user", "content": prompt},
            ],
        )
        text = completion.choices[0].message.content.strip()
        if len(text) > persona.max_chars:
            text = text[: persona.max_chars - 1].rstrip() + "…"
        return text

