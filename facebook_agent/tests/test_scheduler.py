from datetime import datetime, timezone
from pathlib import Path

from facebook_agent.agent.logger_csv import append_log
from facebook_agent.agent.models import ClientConfig
from facebook_agent.agent.scheduler import get_due_slots_for_client


def _sample_client():
    return ClientConfig.model_validate(
        {
            "client_id": "c1",
            "display_name": "Brand",
            "agent_id": "a1",
            "business": {"niche": "n", "city": "c", "language": "ro"},
            "platforms": {"facebook": {"enabled": True, "page_id": "p1"}, "instagram": {"enabled": False}},
            "schedule": {
                "timezone": "Europe/Bucharest",
                "slots": [
                    {
                        "id": "slot1",
                        "days_of_week": [1, 2, 3, 4, 5, 6, 7],
                        "time": "09:00",
                        "platforms": ["facebook"],
                        "campaign": "camp1",
                    }
                ],
            },
            "campaigns": {"camp1": {"objective": "o"}},
            "guardrails": {"max_posts_per_day": 2},
        }
    )


def test_due_slot_within_tolerance(tmp_path: Path):
    client = _sample_client()
    log_path = tmp_path / "log.csv"
    now = datetime(2026, 1, 2, 7, 10, tzinfo=timezone.utc)  # 09:10 in Europe/Bucharest
    due = get_due_slots_for_client(client, now, log_path=log_path, tolerance_minutes=15, platform="facebook")
    assert len(due) == 1


def test_duplicate_prevents_run(tmp_path: Path):
    client = _sample_client()
    log_path = tmp_path / "log.csv"
    now = datetime(2026, 1, 2, 7, 10, tzinfo=timezone.utc)

    append_log(
        log_path,
        timestamp=datetime(2026, 1, 2, 7, 0, tzinfo=timezone.utc),
        client_id="c1",
        slot_id="slot1",
        campaign="camp1",
        platform="facebook",
        page_id="p1",
        post_id="x",
        status="success",
        error=None,
    )

    due = get_due_slots_for_client(client, now, log_path=log_path, tolerance_minutes=15, platform="facebook")
    assert due == []

