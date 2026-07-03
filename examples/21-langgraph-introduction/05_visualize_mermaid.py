"""Day21 示例 5：输出 Mermaid 图。

LangGraph 的流程本质是图，所以可以被可视化。
这里直接输出 Mermaid 源码，你可以粘贴到 Obsidian 或 Mermaid Live Editor 查看图。
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class RouteState(TypedDict, total=False):
    task_type: str
    result: str


def classify_task(state: RouteState) -> dict:
    return {"task_type": state.get("task_type", "question")}


def route_task(state: RouteState) -> Literal["answer", "review"]:
    if state["task_type"] == "high_risk":
        return "review"
    return "answer"


def answer(state: RouteState) -> dict:
    return {"result": "自动回答完成"}


def review(state: RouteState) -> dict:
    return {"result": "进入人工审核"}


def build_graph():
    builder = StateGraph(RouteState)

    builder.add_node("classify_task", classify_task)
    builder.add_node("answer", answer)
    builder.add_node("review", review)

    builder.add_edge(START, "classify_task")
    builder.add_conditional_edges(
        "classify_task",
        route_task,
        {
            "answer": "answer",
            "review": "review",
        },
    )
    builder.add_edge("answer", END)
    builder.add_edge("review", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    print(graph.get_graph().draw_mermaid())
