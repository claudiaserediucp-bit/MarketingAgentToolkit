from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from .agent_core import run_once


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    now = datetime.now(timezone.utc)
    asyncio.run(run_once(base_dir, now))


if __name__ == "__main__":
    main()

