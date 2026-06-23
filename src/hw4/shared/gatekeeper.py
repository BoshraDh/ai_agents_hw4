"""API Gatekeeper — all LLM calls pass through here. Uses OpenAI SDK."""

from __future__ import annotations

import os
import time
from collections.abc import Sequence

import openai

from hw4.shared.config import get_config


class ApiGatekeeper:
    """Centralized manager for OpenAI API calls with rate limiting & retry."""

    def __init__(self) -> None:
        cfg = get_config()
        api_key = os.environ.get("OPENAI_API_KEY", "")
        self._client = openai.OpenAI(api_key=api_key)
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
        all_messages: list[dict[str, str]] = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(list(messages))

        for attempt in range(self._max_retries + 1):
            try:
                self._throttle()
                response = self._client.chat.completions.create(
                    model=model,
                    messages=all_messages,  # type: ignore[arg-type]
                    max_tokens=max_tokens,
                )
                self._call_timestamps.append(time.monotonic())
                usage = response.usage
                if usage:
                    self.total_prompt_tokens += usage.prompt_tokens
                    self.total_completion_tokens += usage.completion_tokens
                return response.choices[0].message.content or ""
            except openai.RateLimitError as exc:
                last_exc = exc
                time.sleep(min(delay, self._max_delay))
                delay *= 2
            except openai.APIError as exc:
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
