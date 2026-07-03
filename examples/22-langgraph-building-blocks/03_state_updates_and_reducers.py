"""Day22 示例 3：State 更新和 reducer。

默认情况下，节点返回的同名字段会覆盖旧值。
如果希望列表被追加，可以使用 Annotated + reducer。
"""

from operator import add
from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class OverwriteState(TypedDict):
    graph_state: str
    history: list[str]


def overwrite_node_1(state: OverwriteState) -> dict:
    return {
        "graph_state": state["graph_state"] + " -> node_1",
        "history": ["node_1"],
    }


def overwrite_node_2(state: OverwriteState) -> dict:
    return {
        "graph_state": state["graph_state"] + " -> node_2",
        "history": ["node_2"],
    }


class ReducerState(TypedDict):
    graph_state: str
    history: Annotated[list[str], add]


def reducer_node_1(state: ReducerState) -> dict:
    return {
        "graph_state": state["graph_state"] + " -> node_1",
        "history": ["node_1"],
    }


def reducer_node_2(state: ReducerState) -> dict:
    return {
        "graph_state": state["graph_state"] + " -> node_2",
        "history": ["node_2"],
    }


def build_overwrite_graph():
    builder = StateGraph(OverwriteState)
    builder.add_node("node_1", overwrite_node_1)
    builder.add_node("node_2", overwrite_node_2)
    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", "node_2")
    builder.add_edge("node_2", END)
    return builder.compile()


def build_reducer_graph():
    builder = StateGraph(ReducerState)
    builder.add_node("node_1", reducer_node_1)
    builder.add_node("node_2", reducer_node_2)
    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", "node_2")
    builder.add_edge("node_2", END)
    return builder.compile()


if __name__ == "__main__":
    overwrite_graph = build_overwrite_graph()
    reducer_graph = build_reducer_graph()

    print("默认覆盖更新：")
    print(overwrite_graph.invoke({"graph_state": "start", "history": []}))
    print()

    print("Reducer 追加更新：")
    print(reducer_graph.invoke({"graph_state": "start", "history": []}))
