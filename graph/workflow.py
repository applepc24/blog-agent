from typing import TypedDict, Annotated, Literal
import operator
from langgraph.graph import StateGraph, END
from agents import researcher, writer, seo

class BlogState(TypedDict):
    topic: str
    raw_material: str
    keywords: list[str]
    draft: str
    seo: dict
    messages: Annotated[list, operator.add]
    next: str
    low_traffic_warning: bool

AGENTS = ["researcher", "writer", "seo", "FINISH"]

def supervisor_node(state: BlogState) -> BlogState:
    topic = state.get("topic", "")
    keywords = state.get("keywords", [])
    draft = state.get("draft", "")
    seo = state.get("seo", {})

    if not keywords:
        next_agent = "researcher"
    elif not draft:
        next_agent ="writer"
    elif not seo:
        next_agent = "seo"
    else:
        next_agent = "FINISH"
    
    return {**state, "next": next_agent}


def researcher_node(state: BlogState) -> dict:  # type: ignore[override]
    return researcher.run(state)

def writer_node(state: BlogState) -> dict:  # type: ignore[override]
    return writer.run(state)

def seo_node(state: BlogState) -> dict:  # type: ignore[override]
    return seo.run(state)

def build_graph():
    graph = StateGraph(BlogState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("seo", seo_node)

    graph.set_entry_point("supervisor")

    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "researcher": "researcher",
            "writer": "writer",
            "seo": "seo",
            "FINISH": END,

        }
    )

    graph.add_edge("researcher", "supervisor")
    graph.add_edge("writer", "supervisor")
    graph.add_edge("seo", "supervisor")

    return graph.compile()

app = build_graph()