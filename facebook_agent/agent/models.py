from __future__ import annotations

from datetime import datetime, time
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, RootModel, field_validator


class LLMConfig(BaseModel):
    provider: str = Field(default="openai")
    model: str
    max_tokens: int = Field(default=300)
    temperature: float = Field(default=0.7)


class SchedulerConfig(BaseModel):
    tick_minutes: int = Field(default=30)
    tolerance_minutes: int = Field(default=15)


class FacebookMCPConfig(BaseModel):
    command: str
    args: List[str] = Field(default_factory=list)


class LoggingConfig(BaseModel):
    type: str = Field(default="csv")
    file: str


class GlobalConfig(BaseModel):
    timezone: str = Field(default="Europe/Bucharest")
    llm: LLMConfig
    scheduler: SchedulerConfig
    facebook_mcp: FacebookMCPConfig
    logging: LoggingConfig


class AgentPersona(BaseModel):
    name: str
    language: str
    tone: str
    style_notes: str
    content_mix: Optional[str] = None
    max_chars: int = Field(default=280)


class AgentsConfig(BaseModel):
    agents: Dict[str, AgentPersona]


class BusinessConfig(BaseModel):
    niche: str
    city: str
    language: str


class PlatformConfig(BaseModel):
    enabled: bool = Field(default=False)
    page_id: Optional[str] = None
    ig_business_id: Optional[str] = None  # kept for future IG support


class PlatformsConfig(BaseModel):
    facebook: PlatformConfig
    instagram: Optional[PlatformConfig] = None


class Slot(BaseModel):
    id: str
    days_of_week: List[int]
    time: str  # "HH:MM"
    platforms: List[str]
    campaign: str

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, value: List[int]) -> List[int]:
        for d in value:
            if d < 1 or d > 7:
                raise ValueError("days_of_week must be between 1 and 7 (ISO, Mon=1)")
        return value


class Campaign(BaseModel):
    objective: str
    notes: Optional[str] = None


class Guardrails(BaseModel):
    max_posts_per_day: int = Field(default=10)


class ClientConfig(BaseModel):
    client_id: str
    display_name: str
    agent_id: str
    business: BusinessConfig
    platforms: PlatformsConfig
    schedule: Dict[str, object]  # raw to allow validation below
    campaigns: Dict[str, Campaign]
    guardrails: Guardrails = Field(default_factory=Guardrails)
    timezone: Optional[str] = None

    slots: List[Slot] = Field(default_factory=list)

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, value: Dict[str, object]) -> Dict[str, object]:
        # accept raw schedule; parsed in model_post_init
        return value

    def model_post_init(self, __context) -> None:
        slots_raw = self.schedule.get("slots", [])
        self.slots = [Slot.model_validate(s) for s in slots_raw]

    @property
    def tz_name(self) -> str:
        return self.schedule.get("timezone") or self.timezone or "Europe/Bucharest"


class ClientsRoot(RootModel[List[ClientConfig]]):
    root: List[ClientConfig]


class PostResult(BaseModel):
    success: bool
    post_id: Optional[str] = None
    error: Optional[str] = None
    platform: str = "facebook"
    page_id: Optional[str] = None
    client_id: Optional[str] = None
    slot_id: Optional[str] = None
    campaign: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


