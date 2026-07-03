"""Day21 示例 3：邮件分拣工作流。

这个示例模拟课程里的 Alfred 邮件分拣管家。

重点：
1. 用状态保存邮件内容、分类结果、检索结果、草稿回复。
2. 用条件边把不同类型邮件路由到不同节点。
3. 高风险邮件进入人工审核分支。
"""

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class EmailState(TypedDict, total=False):
    email: str
    intent: str
    urgency: str
    search_results: list[str]
    ticket_id: str
    draft_reply: str
    final_status: str


def classify_email(state: EmailState) -> dict:
    email = state["email"].lower()

    if "charged twice" in email or "账单" in email or "扣款" in email:
        return {"intent": "billing", "urgency": "high"}
    if "bug" in email or "crash" in email or "报错" in email:
        return {"intent": "bug", "urgency": "medium"}
    if "password" in email or "密码" in email:
        return {"intent": "question", "urgency": "low"}

    return {"intent": "general", "urgency": "low"}


def route_by_intent(state: EmailState) -> Literal["search_docs", "bug_tracking", "draft_reply"]:
    if state["intent"] == "question":
        return "search_docs"
    if state["intent"] == "bug":
        return "bug_tracking"
    return "draft_reply"


def search_docs(state: EmailState) -> dict:
    return {
        "search_results": [
            "重置密码路径：Settings > Security > Change Password",
            "密码至少 12 位，并包含大小写字母、数字和符号。",
        ]
    }


def bug_tracking(state: EmailState) -> dict:
    return {
        "ticket_id": "BUG-2026-0703",
        "search_results": ["已创建 Bug 工单，工程团队会继续排查。"],
    }


def draft_reply(state: EmailState) -> dict:
    intent = state["intent"]

    if intent == "question":
        docs = "\n".join(f"- {item}" for item in state.get("search_results", []))
        reply = f"您好，关于您的问题，可以参考以下步骤：\n{docs}"
    elif intent == "bug":
        reply = f"您好，我们已记录该问题，工单号是 {state['ticket_id']}。"
    elif intent == "billing":
        reply = "您好，账单问题涉及账户安全，我们会转交人工客服进一步核查。"
    else:
        reply = "您好，我们已收到您的邮件，会尽快处理。"

    return {"draft_reply": reply}


def route_after_draft(state: EmailState) -> Literal["human_review", "send_reply"]:
    if state["urgency"] in {"high", "critical"} or state["intent"] == "billing":
        return "human_review"
    return "send_reply"


def human_review(state: EmailState) -> dict:
    return {
        "final_status": (
            "需要人工审核：该邮件涉及高风险或账单问题，"
            "系统不会自动发送回复。"
        )
    }


def send_reply(state: EmailState) -> dict:
    return {"final_status": f"已自动发送回复：{state['draft_reply']}"}


def build_graph():
    builder = StateGraph(EmailState)

    builder.add_node("classify_email", classify_email)
    builder.add_node("search_docs", search_docs)
    builder.add_node("bug_tracking", bug_tracking)
    builder.add_node("draft_reply", draft_reply)
    builder.add_node("human_review", human_review)
    builder.add_node("send_reply", send_reply)

    builder.add_edge(START, "classify_email")
    builder.add_conditional_edges(
        "classify_email",
        route_by_intent,
        {
            "search_docs": "search_docs",
            "bug_tracking": "bug_tracking",
            "draft_reply": "draft_reply",
        },
    )
    builder.add_edge("search_docs", "draft_reply")
    builder.add_edge("bug_tracking", "draft_reply")
    builder.add_conditional_edges(
        "draft_reply",
        route_after_draft,
        {
            "human_review": "human_review",
            "send_reply": "send_reply",
        },
    )
    builder.add_edge("human_review", END)
    builder.add_edge("send_reply", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()

    test_cases = [
        {"email": "How do I reset my password?"},
        {"email": "The export feature crashes when I select PDF format."},
        {"email": "I was charged twice for my subscription!"},
    ]

    for case in test_cases:
        print("=" * 60)
        result = graph.invoke(case)
        print("邮件：", case["email"])
        print("分类：", result["intent"], result["urgency"])
        print("结果：", result["final_status"])
