"""
LangGraph orchestration - the state machine that coordinates all 5 agents.

This file defines the graph structure, nodes, edges, and conditional routing.
"""

from langgraph.graph import StateGraph, END
from pipeline.state import ASQAState
from pipeline.agents.code_reader import code_reader_node
from pipeline.agents.test_generator import test_generator_node
from pipeline.agents.runner import runner_node
from pipeline.agents.bug_reporter import bug_reporter_node
from pipeline.agents.fix_suggester import fix_suggester_node


def decide_after_runner(state: ASQAState) -> str:
    """
    Routing function called after Runner node.

    Decides whether to:
    - "retry": Route back to Test Generator for another attempt (execution error + retries left)
    - "continue": Route forward to Bug Reporter (normal flow)

    Args:
        state: Current ASQAState dict

    Returns:
        "retry" or "continue"
    """
    if state.get("execution_error") and state.get("retry_count", 0) < 2:
        return "retry"
    return "continue"


def build_graph():
    """
    Build and compile the ASQA LangGraph state machine.

    Returns:
        Compiled LangGraph graph
    """
    graph = StateGraph(ASQAState)

    # Add all nodes
    graph.add_node("code_reader", code_reader_node)
    graph.add_node("test_generator", test_generator_node)
    graph.add_node("runner", runner_node)
    graph.add_node("bug_reporter", bug_reporter_node)
    graph.add_node("fix_suggester", fix_suggester_node)

    # Set entry point
    graph.set_entry_point("code_reader")

    # Linear edges
    graph.add_edge("code_reader", "test_generator")
    graph.add_edge("test_generator", "runner")
    graph.add_edge("bug_reporter", "fix_suggester")
    graph.add_edge("fix_suggester", END)

    # Conditional edge from runner - retry or continue
    graph.add_conditional_edges(
        "runner",
        decide_after_runner,
        {
            "retry": "test_generator",
            "continue": "bug_reporter",
        }
    )

    return graph.compile()
