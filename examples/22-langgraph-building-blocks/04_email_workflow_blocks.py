"""Day22 示例 4：把四个构建模块组合成一个小型邮件工作流。

这个例子不调用真实 LLM。
它用规则函数模拟 LLM 分类，重点展示：
- State 如何保存跨节点数据
- Node 如何读写 State
- Edge 如何控制流程
- StateGraph 如何组织完整工作流
"""

from typing import Literal

from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class Classification(TypedDict):
    intent: Literal["question", "bug", "billing", "other"]
    urgency: Literal["low", "medium", "high"]
    topic: str


class EmailState(TypedDict, total=False):
    email_content: str
    classification: Classification
    search_results: list[str]
    ticket_id: str
    draft_response: str
    final_status: str


def classify_email(state: EmailState) -> dict:
    text = state["email_content"].lower()

    if "charged twice" in text or "billing" in text:
        classification: Classification = {
            "intent": "billing",
            "urgency": "high",
            "topic": "payment",
        }
    elif "crash" in text or "bug" in text:
        classification = {
            "intent": "bug",
            "urgency": "medium",
            "topic": "product issue",
        }
    elif "password" in text:
        classification = {
            "intent": "question",
            "urgency": "low",
            "topic": "account access",
        }
    else:
        classification = {
            "intent": "other",
            "urgency": "low",
            "topic": "general",
        }

    return {"classification": classification}


def route_by_classification(
    state: EmailState,
) -> Literal["search_docs", "create_ticket", "human_review", "draft_reply"]:
    classification = state["classification"]

    if classification["intent"] == "billing" or classification["urgency"] == "high":
        return "human_review"
    if classification["intent"] == "bug":
        return "create_ticket"
    if classification["intent"] == "question":
        return "search_docs"
    return "draft_reply"


def search_docs(state: EmailState) -> dict:
    return {
        "search_results": [
            "Open Settings.",
            "Choose Security.",
            "Click Change Password.",
        ]
    }


def create_ticket(state: EmailState) -> dict:
    return {"ticket_id": "BUG-2201"}


def human_review(state: EmailState) -> dict:
    return {
        "draft_response": "This billing case needs human review before sending.",
        "final_status": "paused_for_human_review",
    }


def draft_reply(state: EmailState) -> dict:
    classification = state["classification"]

    if classification["intent"] == "question":
        docs = " ".join(state.get("search_results", []))
        draft = f"Here is how to solve it: {docs}"
    elif classification["intent"] == "bug":
        draft = f"We created a bug ticket for you: {state['ticket_id']}."
    else:
        draft = "Thanks for your email. We will get back to you soon."

    return {"draft_response": draft}


def send_reply(state: EmailState) -> dict:
    return {"final_status": f"sent: {state['draft_response']}"}


def build_graph():
    builder = StateGraph(EmailState)

    builder.add_node("classify_email", classify_email)
    builder.add_node("search_docs", search_docs)
    builder.add_node("create_ticket", create_ticket)
    builder.add_node("human_review", human_review)
    builder.add_node("draft_reply", draft_reply)
    builder.add_node("send_reply", send_reply)

    builder.add_edge(START, "classify_email")
    builder.add_conditional_edges(
        "classify_email",
        route_by_classification,
        {
            "search_docs": "search_docs",
            "create_ticket": "create_ticket",
            "human_review": "human_review",
            "draft_reply": "draft_reply",
        },
    )
    builder.add_edge("search_docs", "draft_reply")
    builder.add_edge("create_ticket", "draft_reply")
    builder.add_edge("draft_reply", "send_reply")
    builder.add_edge("send_reply", END)
    builder.add_edge("human_review", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()

    test_cases = [
        {"email_content": "How do I reset my password?"},
        {"email_content": "The export feature crashes when I choose PDF."},
        {"email_content": "I was charged twice for my subscription."},
    ]

    for case in test_cases:
        print("=" * 60)
        result = graph.invoke(case)
        print("input:", case["email_content"])
        print("classification:", result["classification"])
        print("draft:", result.get("draft_response"))
        print("status:", result["final_status"])
