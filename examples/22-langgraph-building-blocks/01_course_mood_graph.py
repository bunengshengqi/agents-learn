"""Day22 示例 1：课程里的核心构建模块。

这个文件复现 Hugging Face 课程中的最小图：

START -> node_1 -> node_2 or node_3 -> END

为了让输出稳定，这里不用 random，而是根据输入文本决定分支。
"""

from typing import Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    graph_state: str


def node_1(state: State) -> dict:
    print("---Node 1---")
    return {"graph_state": state["graph_state"] + " I am"}


def node_2(state: State) -> dict:
    print("---Node 2---")
    return {"graph_state": state["graph_state"] + " happy!"}


def node_3(state: State) -> dict:
    print("---Node 3---")
    return {"graph_state": state["graph_state"] + " sad!"}


def decide_mood(state: State) -> Literal["node_2", "node_3"]:
    """根据当前 State 决定下一步去哪。

    真实项目里通常根据分类结果、置信度、工具结果等字段路由。
    """
    user_input = state["graph_state"].lower()

    if "sad" in user_input or "bad" in user_input:
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

    examples = [
        {"graph_state": "Hi, this is Lance."},
        {"graph_state": "Today feels bad."},
    ]

    for item in examples:
        print("=" * 60)
        result = graph.invoke(item)
        print(result)
