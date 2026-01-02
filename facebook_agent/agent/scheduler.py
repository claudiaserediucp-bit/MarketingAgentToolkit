from __future__ import annotations

from datetime import datetime, time
from typing import List, Tuple
from zoneinfo import ZoneInfo

from .logger_csv import has_success_for_slot
from .models import ClientConfig, Slot


def _slot_datetime(slot: Slot, tz: ZoneInfo, base_date) -> datetime:
    hh, mm = map(int, slot.time.split(":"))
    return datetime.combine(base_date, time(hour=hh, minute=mm), tzinfo=tz)


def get_due_slots_for_client(
    client: ClientConfig,
    now: datetime,
    log_path,
    tolerance_minutes: int = 15,
    platform: str = "facebook",
) -> List[Tuple[Slot, str]]:
    """
    Return list of (slot, platform) that are due for the given client at "now".
    Avoid duplicates by checking the CSV log for same client_id+slot_id+date+platform with success status.
    """
    tz = ZoneInfo(client.tz_name)
    local_now = now.astimezone(tz)
    today = local_now.date()
    due: List[Tuple[Slot, str]] = []

    for slot in client.slots:
        if platform not in slot.platforms:
            continue
        if local_now.isoweekday() not in slot.days_of_week:
            continue
        slot_dt = _slot_datetime(slot, tz, today)
        delta_min = abs((local_now - slot_dt).total_seconds()) / 60.0
        if delta_min > tolerance_minutes:
            continue
        if has_success_for_slot(log_path, today, client.client_id, slot.id, platform):
            continue
        due.append((slot, platform))
    return due

