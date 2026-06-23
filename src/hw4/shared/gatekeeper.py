"""API Gatekeeper — all LLM calls pass through here."""

from __future__ import annotations

import os
import time
from collections.abc import Sequence
from typing import Any

import anthropic

from hw4.shared.config import get_config


class ApiGatekeeper:
    """Centralized manager for Anthropic API calls with rate limiting & retry."""

    def __init__(self) -> None:
        cfg = get_config()
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self._client = anthropic.Anthropic(api_key=api_key)
        self._max_retries = cfg.max_retries
        self._base_delay = cfg.retry_base_delay
        self._max_delay = cfg.retry_max_delay
        self._rpm_limit = cfg.rpm_limit
        self._call_timestamps: list[float] = []
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    def _throttle(self) -> None:
        """Block if we are at the RPM limit."""
        now = time.monotonic()
        self._call_timestamps = [t for t in self._call_timestamps if now - t < 60]
        if len(self._call_timestamps) >= self._rpm_limit:
            sleep_for = 60 - (now - self._call_timestamps[0]) + 0.1
            time.sleep(max(0, sleep_for))

    def chat_complete(
        self,
        messages: Sequence[dict[str, str]],
        model: str,
        max_tokens: int,
        system: str = "",
    ) -> str:
        """Send a chat request and return the text response."""
        delay = self._base_delay
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                self._throttle()
                kwargs: dict[str, Any] = {
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": list(messages),
                }
                if system:
                    kwargs["system"] = system
                response = self._client.messages.create(**kwargs)
                self._call_timestamps.append(time.monotonic())
                self.total_prompt_tokens += response.usage.input_tokens
                self.total_completion_tokens += response.usage.output_tokens
                return response.content[0].text
            except anthropic.RateLimitError as exc:
                last_exc = exc
                time.sleep(min(delay, self._max_delay))
                delay *= 2
            except anthropic.APIError as exc:
                last_exc = exc
                if attempt == self._max_retries:
                    break
                time.sleep(min(delay, self._max_delay))
                delay *= 2
        raise RuntimeError(f"Gatekeeper failed after {self._max_retries} retries") from last_exc

    def token_summary(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
        }

    def reset_counts(self) -> None:
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0


_gatekeeper: ApiGatekeeper | None = None


def get_gatekeeper() -> ApiGatekeeper:
    """Return the module-level ApiGatekeeper singleton."""
    global _gatekeeper
    if _gatekeeper is None:
        _gatekeeper = ApiGatekeeper()
    return _gatekeeper
