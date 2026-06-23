"""Naive baseline: reads ALL scrapy .py files and sends them to LLM in one shot."""

from __future__ import annotations

import textwrap
from pathlib import Path

from hw4.shared.config import get_config
from hw4.shared.gatekeeper import get_gatekeeper

SYSTEM = (
    "You are a Python bug finder. Analyze the provided codebase and find any bug"
    " related to None handling in allowed_domains."
)

USER_TEMPLATE = (
    "Here is the full scrapy codebase ({file_count} files, {total_lines} lines):\n\n"
    "{code}\n\n"
    "Find the bug related to `allowed_domains` and `None` values."
    " Report: file, class, method, root cause, fix."
)

MAX_CHARS = 80_000


def collect_source(source_root: str | Path) -> tuple[str, int, int]:
    """Collect all .py files content up to MAX_CHARS total."""
    root = Path(source_root)
    parts: list[str] = []
    total_lines = 0
    file_count = 0
    for py_file in sorted(root.rglob("*.py")):
        try:
            content = py_file.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        header = f"\n\n# === {py_file.relative_to(root)} ===\n"
        parts.append(header + content)
        total_lines += content.count("\n")
        file_count += 1
    combined = "".join(parts)
    return combined[:MAX_CHARS], file_count, total_lines


def run_naive() -> dict:
    """Run the naive baseline and return result dict with token counts."""
    cfg = get_config()
    gk = get_gatekeeper()
    gk.reset_counts()

    code, file_count, total_lines = collect_source(cfg.scrapy_source)
    user_msg = USER_TEMPLATE.format(
        file_count=file_count,
        total_lines=total_lines,
        code=textwrap.shorten(code, width=MAX_CHARS, placeholder="...[truncated]"),
    )

    response = gk.chat_complete(
        messages=[{"role": "user", "content": user_msg}],
        model=cfg.baseline_model,
        max_tokens=cfg.baseline_max_tokens,
        system=SYSTEM,
    )

    return {
        "response": response,
        "file_count": file_count,
        "total_lines": total_lines,
        **gk.token_summary(),
    }


if __name__ == "__main__":
    result = run_naive()
    print("=== NAIVE AGENT RESULT ===")
    print(result["response"])
    print(f"\nTokens: {result['total_tokens']:,}")
