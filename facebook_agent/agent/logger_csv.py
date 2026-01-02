from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path
from typing import Optional

LOG_HEADER = [
    "timestamp_iso",
    "client_id",
    "slot_id",
    "campaign",
    "platform",
    "page_id",
    "post_id",
    "status",
    "error",
]


def ensure_log_file(log_path: Path) -> None:
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if not log_path.exists():
            with log_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(LOG_HEADER)
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Cannot create or write log file at {log_path}: {exc}") from exc


def append_log(
    log_path: Path,
    timestamp: datetime,
    client_id: str,
    slot_id: str,
    campaign: str,
    platform: str,
    page_id: Optional[str],
    post_id: Optional[str],
    status: str,
    error: Optional[str] = None,
) -> None:
    ensure_log_file(log_path)
    with log_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                timestamp.isoformat(),
                client_id,
                slot_id,
                campaign,
                platform,
                page_id or "",
                post_id or "",
                status,
                error or "",
            ]
        )


def has_success_for_slot(
    log_path: Path, day: date, client_id: str, slot_id: str, platform: str
) -> bool:
    if not log_path.exists():
        return False
    with log_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = row.get("timestamp_iso", "")
            if not ts:
                continue
            try:
                ts_dt = datetime.fromisoformat(ts)
            except Exception:
                continue
            if ts_dt.date() != day:
                continue
            if (
                row.get("client_id") == client_id
                and row.get("slot_id") == slot_id
                and row.get("platform") == platform
                and row.get("status") == "success"
            ):
                return True
    return False


def count_success_for_day(
    log_path: Path, day: date, client_id: str, platform: str
) -> int:
    if not log_path.exists():
        return 0
    count = 0
    with log_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = row.get("timestamp_iso", "")
            if not ts:
                continue
            try:
                ts_dt = datetime.fromisoformat(ts)
            except Exception:
                continue
            if ts_dt.date() != day:
                continue
            if (
                row.get("client_id") == client_id
                and row.get("platform") == platform
                and row.get("status") == "success"
            ):
                count += 1
    return count

