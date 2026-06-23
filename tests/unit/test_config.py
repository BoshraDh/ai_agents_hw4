"""Unit tests for Config singleton."""

from __future__ import annotations

import hw4.shared.config as cfg_mod
from hw4.shared.config import Config, get_config


def test_config_loads_model(tmp_config):
    cfg_mod._config = None
    cfg = get_config()
    assert cfg.agent_model == "claude-haiku-4-5-20251001"


def test_config_loads_rate_limits(tmp_config):
    cfg_mod._config = None
    cfg = get_config()
    assert cfg.rpm_limit == 10
    assert cfg.max_retries == 1


def test_config_singleton(tmp_config):
    cfg_mod._config = None
    c1 = get_config()
    c2 = get_config()
    assert c1 is c2


def test_config_top_k(tmp_config):
    cfg_mod._config = None
    cfg = get_config()
    assert cfg.top_k_hot_nodes == 3
