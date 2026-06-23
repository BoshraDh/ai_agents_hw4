"""Token counting utilities for comparing agent runs."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NodeRecord:
    node_name: str
    prompt_tokens: int
    completion_tokens: int

    @property
    def total(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class TokenCounter:
    """Accumulates token usage records across one agent run."""

    records: list[NodeRecord] = field(default_factory=list)

    def add(self, node_name: str, prompt_tokens: int, completion_tokens: int) -> None:
        self.records.append(NodeRecord(node_name, prompt_tokens, completion_tokens))

    @property
    def total_prompt(self) -> int:
        return sum(r.prompt_tokens for r in self.records)

    @property
    def total_completion(self) -> int:
        return sum(r.completion_tokens for r in self.records)

    @property
    def total(self) -> int:
        return self.total_prompt + self.total_completion

    @property
    def files_read(self) -> int:
        return sum(1 for r in self.records if "code_reader" in r.node_name)

    def summary(self) -> dict[str, int]:
        return {
            "prompt_tokens": self.total_prompt,
            "completion_tokens": self.total_completion,
            "total_tokens": self.total,
            "files_read": self.files_read,
            "node_count": len(self.records),
        }
