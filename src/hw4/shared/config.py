"""Loads and exposes typed configuration from config/ JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from hw4.shared.constants import RATE_LIMITS_JSON, SETUP_JSON


class Config:
    """Singleton configuration manager. No hardcoded values allowed elsewhere."""

    _instance: Config | None = None

    def __init__(self, base_dir: str | Path = ".") -> None:
        root = Path(base_dir)
        self._setup: dict[str, Any] = json.loads((root / SETUP_JSON).read_text())
        self._rate: dict[str, Any] = json.loads((root / RATE_LIMITS_JSON).read_text())

    # ── setup.json accessors ──────────────────────────────────────────────────

    @property
    def agent_model(self) -> str:
        return self._setup["agent"]["model"]

    @property
    def baseline_model(self) -> str:
        return self._setup["baseline"]["model"]

    @property
    def agent_max_tokens(self) -> int:
        return int(self._setup["agent"]["max_tokens_per_node"])

    @property
    def baseline_max_tokens(self) -> int:
        return int(self._setup["baseline"]["max_tokens"])

    @property
    def top_k_hot_nodes(self) -> int:
        return int(self._setup["agent"]["top_k_hot_nodes"])

    @property
    def scrapy_source(self) -> str:
        return self._setup["paths"]["scrapy_source"]

    @property
    def artifacts_dir(self) -> str:
        return self._setup["paths"]["artifacts_dir"]

    @property
    def obsidian_dir(self) -> str:
        return self._setup["paths"]["obsidian_dir"]

    @property
    def skip_graphify_if_exists(self) -> bool:
        return bool(self._setup["graphify"]["skip_if_exists"])

    # ── rate_limits.json accessors ────────────────────────────────────────────

    @property
    def rpm_limit(self) -> int:
        return int(self._rate["anthropic"]["requests_per_minute"])

    @property
    def retry_base_delay(self) -> float:
        return float(self._rate["anthropic"]["retry_base_delay_seconds"])

    @property
    def retry_max_delay(self) -> float:
        return float(self._rate["anthropic"]["retry_max_delay_seconds"])

    @property
    def max_retries(self) -> int:
        return int(self._rate["anthropic"]["max_retries"])


_config: Config | None = None


def get_config(base_dir: str | Path = ".") -> Config:
    """Return the module-level Config singleton."""
    global _config
    if _config is None:
        _config = Config(base_dir)
    return _config
