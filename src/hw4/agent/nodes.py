"""LangGraph node functions. Each node reads context, calls gatekeeper, updates state."""

from __future__ import annotations

from typing import TypedDict

from hw4.agent import prompts, tools
from hw4.graphify.runner import GraphifyRunner
from hw4.shared.config import get_config
from hw4.shared.gatekeeper import get_gatekeeper


class AgentState(TypedDict):
    graph_summary: str
    obsidian_context: str
    target_code: str
    bug_report: str
    patch: str
    token_log: list[dict]


def graph_reader_node(state: AgentState) -> AgentState:
    """Load graph.json and ask LLM for top suspicious modules."""
    cfg = get_config()
    runner = GraphifyRunner()
    runner.load_graph()
    summary = tools.summarize_graph_for_prompt(runner, k=15)

    gk = get_gatekeeper()
    before = gk.token_summary()
    response = gk.chat_complete(
        messages=[{"role": "user", "content": prompts.GRAPH_READER_USER.format(top_nodes=summary)}],
        model=cfg.agent_model,
        max_tokens=cfg.agent_max_tokens,
        system=prompts.GRAPH_READER_SYSTEM,
    )
    after = gk.token_summary()

    log = state.get("token_log", [])
    log.append({"node": "graph_reader", "tokens": after["total_tokens"] - before["total_tokens"]})
    return {**state, "graph_summary": response, "token_log": log}


def obsidian_reader_node(state: AgentState) -> AgentState:
    """Read hot.md + index.md and ask LLM which file to investigate."""
    cfg = get_config()
    index_txt = tools.read_obsidian_page("index")
    hot_txt = tools.read_obsidian_page("hot")

    gk = get_gatekeeper()
    before = gk.token_summary()
    response = gk.chat_complete(
        messages=[{
            "role": "user",
            "content": prompts.OBSIDIAN_READER_USER.format(
                index_content=index_txt[:2000],
                hot_content=hot_txt[:2000],
            ),
        }],
        model=cfg.agent_model,
        max_tokens=cfg.agent_max_tokens,
        system=prompts.OBSIDIAN_READER_SYSTEM,
    )
    after = gk.token_summary()

    log = state.get("token_log", [])
    delta = after["total_tokens"] - before["total_tokens"]
    log.append({"node": "obsidian_reader", "tokens": delta})
    return {**state, "obsidian_context": response, "token_log": log}


def targeted_code_reader_node(state: AgentState) -> AgentState:
    """Read ≤ 3 targeted source files and ask LLM to identify the bug."""
    cfg = get_config()
    offsite_code = tools.read_source_file("scrapy/downloadermiddlewares/offsite.py")

    gk = get_gatekeeper()
    before = gk.token_summary()
    response = gk.chat_complete(
        messages=[{
            "role": "user",
            "content": prompts.TARGETED_CODE_READER_USER.format(
                code_content=offsite_code[:3000],
                obsidian_context=state.get("obsidian_context", "")[:500],
            ),
        }],
        model=cfg.agent_model,
        max_tokens=cfg.agent_max_tokens,
        system=prompts.TARGETED_CODE_READER_SYSTEM,
    )
    after = gk.token_summary()

    log = state.get("token_log", [])
    delta = after["total_tokens"] - before["total_tokens"]
    log.append({"node": "targeted_code_reader", "tokens": delta})
    return {**state, "target_code": offsite_code, "obsidian_context": response, "token_log": log}


def bug_identifier_node(state: AgentState) -> AgentState:
    """Produce a structured bug report from the code analysis."""
    cfg = get_config()
    gk = get_gatekeeper()
    before = gk.token_summary()
    response = gk.chat_complete(
        messages=[{
            "role": "user",
            "content": prompts.BUG_IDENTIFIER_USER.format(
                analysis=state.get("obsidian_context", "")
            ),
        }],
        model=cfg.agent_model,
        max_tokens=cfg.agent_max_tokens,
        system=prompts.BUG_IDENTIFIER_SYSTEM,
    )
    after = gk.token_summary()

    log = state.get("token_log", [])
    log.append({"node": "bug_identifier", "tokens": after["total_tokens"] - before["total_tokens"]})
    return {**state, "bug_report": response, "token_log": log}


def fixer_node(state: AgentState) -> AgentState:
    """Generate the minimal patch for the identified bug."""
    cfg = get_config()
    gk = get_gatekeeper()
    before = gk.token_summary()
    response = gk.chat_complete(
        messages=[{
            "role": "user",
            "content": prompts.FIXER_USER.format(
                bug_report=state.get("bug_report", ""),
                target_code=state.get("target_code", "")[:2000],
            ),
        }],
        model=cfg.agent_model,
        max_tokens=cfg.agent_max_tokens,
        system=prompts.FIXER_SYSTEM,
    )
    after = gk.token_summary()

    log = state.get("token_log", [])
    log.append({"node": "fixer", "tokens": after["total_tokens"] - before["total_tokens"]})
    return {**state, "patch": response, "token_log": log}
