"""Day23 示例 3：输出邮件处理图的 Mermaid。

运行：

python examples/23-langgraph-first-graph/03_mermaid_visualization.py

把输出复制到 Obsidian 的 Mermaid 代码块中即可查看图。
"""

from typing import Any, Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class EmailState(TypedDict, total=False):
    email: dict[str, Any]
    is_spam: bool
    spam_reason: str | None
    email_category: str | None
    draft_response: str | None
    messages: list[dict[str, str]]


def read_email(state: EmailState) -> dict:
    return {}


def classify_email(state: EmailState) -> dict:
    return {"is_spam": False}


def route_email(state: EmailState) -> Literal["spam", "legitimate"]:
    if state["is_spam"]:
        return "spam"
    return "legitimate"


def handle_spam(state: EmailState) -> dict:
    return {}


def draft_response(state: EmailState) -> dict:
    return {"draft_response": "Draft response"}


def notify_mr_hugg(state: EmailState) -> dict:
    return {}


def build_graph():
    builder = StateGraph(EmailState)
    builder.add_node("read_email", read_email)
    builder.add_node("classify_email", classify_email)
    builder.add_node("handle_spam", handle_spam)
    builder.add_node("draft_response", draft_response)
    builder.add_node("notify_mr_hugg", notify_mr_hugg)

    builder.add_edge(START, "read_email")
    builder.add_edge("read_email", "classify_email")
    builder.add_conditional_edges(
        "classify_email",
        route_email,
        {
            "spam": "handle_spam",
            "legitimate": "draft_response",
        },
    )
    builder.add_edge("handle_spam", END)
    builder.add_edge("draft_response", "notify_mr_hugg")
    builder.add_edge("notify_mr_hugg", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    print(graph.get_graph().draw_mermaid())
