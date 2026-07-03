"""Day22 示例 5：输出 Mermaid 图。

运行后把输出复制到 Obsidian 的 Mermaid 代码块中即可查看图。
"""

from typing import Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    graph_state: str


def node_1(state: State) -> dict:
    return {"graph_state": state["graph_state"] + " I am"}


def node_2(state: State) -> dict:
    return {"graph_state": state["graph_state"] + " happy!"}


def node_3(state: State) -> dict:
    return {"graph_state": state["graph_state"] + " sad!"}


def decide_mood(state: State) -> Literal["node_2", "node_3"]:
    if "sad" in state["graph_state"].lower():
        return "node_3"
    return "node_2"


def build_graph():
    builder = StateGraph(State)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_node("node_3", node_3)

    builder.add_edge(START, "node_1")
    builder.add_conditional_edges(
        "node_1",
        decide_mood,
        {
            "node_2": "node_2",
            "node_3": "node_3",
        },
    )
    builder.add_edge("node_2", END)
    builder.add_edge("node_3", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    print(graph.get_graph().draw_mermaid())
