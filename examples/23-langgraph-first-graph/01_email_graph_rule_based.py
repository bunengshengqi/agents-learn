"""Day23 示例 1：不依赖 LLM 的邮件处理 LangGraph。

这个文件复现课程里的第一个 LangGraph 工作流，但用规则函数模拟 LLM。
好处是：不需要 API Key，也能先理解图是怎么跑起来的。
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
    """Alfred 读取并记录邮件。"""
    email = state["email"]
    print(
        "Alfred is processing an email from "
        f"{email['sender']} with subject: {email['subject']}"
    )
    return {}


def classify_email(state: EmailState) -> dict:
    """用规则模拟 LLM 分类：判断是否垃圾邮件，并给出类别。"""
    email = state["email"]
    text = f"{email['sender']} {email['subject']} {email['body']}".lower()

    spam_keywords = ["lottery", "winner", "bank details", "$5,000,000", "processing fee"]
    is_spam = any(keyword in text for keyword in spam_keywords)

    if is_spam:
        return {
            "is_spam": True,
            "spam_reason": "Detected lottery scam / money request pattern.",
            "email_category": None,
            "messages": state.get("messages", [])
            + [
                {
                    "role": "assistant",
                    "content": "Classification: spam. Reason: lottery scam pattern.",
                }
            ],
        }

    category = "general"
    if "question" in text or "interested" in text or "schedule" in text:
        category = "inquiry"
    elif "complaint" in text or "angry" in text:
        category = "complaint"
    elif "thank" in text:
        category = "thank you"

    return {
        "is_spam": False,
        "spam_reason": None,
        "email_category": category,
        "messages": state.get("messages", [])
        + [
            {
                "role": "assistant",
                "content": f"Classification: legitimate. Category: {category}.",
            }
        ],
    }


def route_email(state: EmailState) -> Literal["spam", "legitimate"]:
    """根据分类结果决定下一步。"""
    if state["is_spam"]:
        return "spam"
    return "legitimate"


def handle_spam(state: EmailState) -> dict:
    """处理垃圾邮件。"""
    print(f"Alfred has marked the email as spam. Reason: {state['spam_reason']}")
    print("The email has been moved to the spam folder.")
    return {}


def draft_response(state: EmailState) -> dict:
    """为合法邮件起草回复。"""
    email = state["email"]
    category = state.get("email_category") or "general"

    response = (
        f"Dear {email['sender']},\n\n"
        f"Thank you for your {category} email. "
        "Mr. Hugg has received your message and will review it shortly.\n\n"
        "Best regards,\nAlfred"
    )

    return {
        "draft_response": response,
        "messages": state.get("messages", [])
        + [{"role": "assistant", "content": response}],
    }


def notify_mr_hugg(state: EmailState) -> dict:
    """通知主人查看合法邮件和回复草稿。"""
    email = state["email"]
    print("\n" + "=" * 60)
    print(f"Sir, you've received an email from {email['sender']}.")
    print(f"Subject: {email['subject']}")
    print(f"Category: {state['email_category']}")
    print("\nI've prepared a draft response for your review:")
    print("-" * 60)
    print(state["draft_response"])
    print("=" * 60 + "\n")
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


def initial_state(email: dict[str, Any]) -> EmailState:
    return {
        "email": email,
        "is_spam": False,
        "spam_reason": None,
        "email_category": None,
        "draft_response": None,
        "messages": [],
    }


if __name__ == "__main__":
    graph = build_graph()

    legitimate_email = {
        "sender": "john.smith@example.com",
        "subject": "Question about your services",
        "body": (
            "Dear Mr. Hugg, I was referred to you by a colleague and I'm interested "
            "in learning more about your consulting services. Could we schedule a call next week?"
        ),
    }

    spam_email = {
        "sender": "winner@lottery-intl.com",
        "subject": "YOU HAVE WON $5,000,000!!!",
        "body": (
            "CONGRATULATIONS! You have been selected as the winner of our international lottery! "
            "To claim your prize, please send us your bank details and a processing fee of $100."
        ),
    }

    print("\nProcessing legitimate email...")
    legitimate_result = graph.invoke(initial_state(legitimate_email))
    print("Final legitimate state:")
    print(legitimate_result)

    print("\nProcessing spam email...")
    spam_result = graph.invoke(initial_state(spam_email))
    print("Final spam state:")
    print(spam_result)
