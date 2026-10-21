"""Lecture de la configuration NON sensible (config/settings.ini).

Les secrets ne sont jamais lus par le code applicatif : ils sont injectés en
variables d'environnement par le déploiement (voir auth.load_keyring_from_env).
"""

from __future__ import annotations

import configparser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS = _REPO_ROOT / "config" / "settings.ini"


@dataclass(frozen=True)
class Settings:
    environment: str
    log_level: str
    max_records_per_request: int
    jira_base_url: str
    jira_read_only: bool


def load_settings(path: Optional[Path] = None) -> Settings:
    parser = configparser.ConfigParser()
    read = parser.read(path or DEFAULT_SETTINGS, encoding="utf-8")
    if not read:
        raise FileNotFoundError(path or DEFAULT_SETTINGS)
    return Settings(
        environment=parser.get("app", "environment"),
        log_level=parser.get("app", "log_level", fallback="INFO"),
        max_records_per_request=parser.getint("api", "max_records_per_request"),
        jira_base_url=parser.get("jira", "base_url"),
        jira_read_only=parser.getboolean("jira", "read_only", fallback=True),
    )
