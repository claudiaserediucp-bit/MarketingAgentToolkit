from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

from .models import AgentsConfig, ClientConfig, ClientsRoot, GlobalConfig


def load_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_global_config(base_dir: Path) -> GlobalConfig:
    cfg_path = base_dir / "config" / "global.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing global config at {cfg_path}")
    return GlobalConfig.model_validate(load_json(cfg_path))


def load_agents_config(base_dir: Path) -> AgentsConfig:
    cfg_path = base_dir / "config" / "agents.json"
    if not cfg_path.exists():
        raise FileNotFoundError(f"Missing agents config at {cfg_path}")
    return AgentsConfig.model_validate(load_json(cfg_path))


def load_clients(base_dir: Path) -> Tuple[ClientConfig, ...]:
    clients_dir = base_dir / "config" / "clients"
    if not clients_dir.exists():
        raise FileNotFoundError(f"Missing clients directory at {clients_dir}")

    clients: list[ClientConfig] = []
    for path in sorted(clients_dir.glob("*.json")):
        clients.append(ClientConfig.model_validate(load_json(path)))
    return tuple(clients)


