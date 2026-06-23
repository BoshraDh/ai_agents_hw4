"""SDK entry point. All external code must call through this module only."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from hw4.agent.workflow import run_agent_workflow
from hw4.analysis.comparator import Comparator
from hw4.analysis.token_counter import TokenCounter
from hw4.baseline.naive_agent import run_naive
from hw4.graphify.obsidian_builder import ObsidianBuilder
from hw4.graphify.runner import GraphifyRunner
from hw4.shared.config import get_config
from hw4.shared.gatekeeper import get_gatekeeper
from hw4.shared.version import VERSION


def setup() -> None:
    """Load .env and initialize singletons."""
    load_dotenv()


def run_graphify_pipeline() -> None:
    """Run Graphify on scrapy and build Obsidian vault."""
    runner = GraphifyRunner()
    runner.run()
    builder = ObsidianBuilder(runner=runner)
    builder.build_all()
    builder.write_architecture_blocks()
    builder.write_oop_summary()


def run_graph_agent() -> dict:
    """Run the LangGraph graph-guided agent. Returns final state dict."""
    gk = get_gatekeeper()
    gk.reset_counts()
    state = run_agent_workflow()

    counter = TokenCounter()
    for record in state.get("token_log", []):
        counter.add(record["node"], record["tokens"] // 2, record["tokens"] // 2)

    return {"state": state, "counter": counter, "token_summary": gk.token_summary()}


def run_baseline_agent() -> dict:
    """Run the naive baseline agent. Returns result + token counter."""
    result = run_naive()
    counter = TokenCounter()
    counter.add("naive_single_call", result["prompt_tokens"], result["completion_tokens"])
    return {"result": result, "counter": counter}


def run_comparison(output_path: str | Path | None = None) -> str:
    """Run both agents and write token comparison report. Returns report text."""
    graph_result = run_graph_agent()
    naive_result = run_baseline_agent()

    report = Comparator(graph_result["counter"], naive_result["counter"])
    return report.write_report(output_path)


def main() -> None:
    """Full pipeline: graphify → obsidian → agent → comparison."""
    setup()
    cfg = get_config()
    print(f"hw4 v{VERSION} — {cfg.agent_model}")
    print("Step 1: Running Graphify...")
    run_graphify_pipeline()
    print("Step 2: Running graph-guided agent...")
    agent_out = run_graph_agent()
    print("\n=== PATCH ===")
    print(agent_out["state"].get("patch", ""))
    print("\nStep 3: Running naive baseline...")
    run_baseline_agent()
    print("Step 4: Writing comparison report...")
    report = run_comparison()
    print(report)


if __name__ == "__main__":
    main()
