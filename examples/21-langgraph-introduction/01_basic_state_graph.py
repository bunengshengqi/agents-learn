"""Day21 示例 1：最小 LangGraph。

目标：
1. 理解 State 是什么。
2. 理解 Node 是什么。
3. 理解 Edge 如何把节点连接起来。

这个示例不调用 LLM，也不需要 API Key。
"""

from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class DemoState(TypedDict, total=False):
    user_input: str
    normalized_input: str
    answer: str


def normalize_input(state: DemoState) -> dict:
    """节点 1：清洗用户输入。"""
    text = state["user_input"].strip()
    return {"normalized_input": text}


def build_answer(state: DemoState) -> dict:
    """节点 2：根据清洗后的输入生成回复。"""
    answer = f"我收到的问题是：{state['normalized_input']}"
    return {"answer": answer}


def build_graph():
    builder = StateGraph(DemoState)

    builder.add_node("normalize_input", normalize_input)
    builder.add_node("build_answer", build_answer)

    builder.add_edge(START, "normalize_input")
    builder.add_edge("normalize_input", "build_answer")
    builder.add_edge("build_answer", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    result = graph.invoke({"user_input": "  LangGraph 是什么？  "})

    print("最终状态：")
    print(result)
