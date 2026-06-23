"""Defines the LangGraph state machine for the graph-guided bug-finding agent."""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from hw4.agent.nodes import (
    AgentState,
    bug_identifier_node,
    fixer_node,
    graph_reader_node,
    obsidian_reader_node,
    targeted_code_reader_node,
)


def build_graph() -> StateGraph:
    """Construct and compile the LangGraph workflow."""
    graph = StateGraph(AgentState)

    graph.add_node("graph_reader", graph_reader_node)
    graph.add_node("obsidian_reader", obsidian_reader_node)
    graph.add_node("targeted_code_reader", targeted_code_reader_node)
    graph.add_node("bug_identifier", bug_identifier_node)
    graph.add_node("fixer", fixer_node)

    graph.set_entry_point("graph_reader")
    graph.add_edge("graph_reader", "obsidian_reader")
    graph.add_edge("obsidian_reader", "targeted_code_reader")
    graph.add_edge("targeted_code_reader", "bug_identifier")
    graph.add_edge("bug_identifier", "fixer")
    graph.add_edge("fixer", END)

    return graph.compile()


def run_agent_workflow() -> AgentState:
    """Run the full agent pipeline and return the final state."""
    app = build_graph()
    initial: AgentState = {
        "graph_summary": "",
        "obsidian_context": "",
        "target_code": "",
        "bug_report": "",
        "patch": "",
        "token_log": [],
    }
    return app.invoke(initial)
