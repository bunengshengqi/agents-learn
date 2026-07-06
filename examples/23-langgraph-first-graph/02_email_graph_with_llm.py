"""Day23 示例 2：调用 LLM 的邮件处理 LangGraph。

运行前需要在项目根目录配置 .env：

OPENAI_API_KEY=你的真实key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash

这个版本贴近课程：分类和起草回复都由 LLM 完成。
"""

from __future__ import annotations

import json
import os
from typing import Any, Literal

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph


class EmailState(TypedDict, total=False):
    email: dict[str, Any]
    is_spam: bool
    spam_reason: str | None
    email_category: str | None
    draft_response: str | None
    messages: list[dict[str, str]]


def build_model() -> ChatOpenAI:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model_name = os.getenv("OPENAI_MODEL")

    missing = [
        name
        for name, value in {
            "OPENAI_API_KEY": api_key,
            "OPENAI_BASE_URL": base_url,
            "OPENAI_MODEL": model_name,
        }.items()
        if not value
    ]

    if missing:
        raise ValueError("缺少环境变量：" + ", ".join(missing))

    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=0,
    )


MODEL: ChatOpenAI | None = None


def get_model() -> ChatOpenAI:
    """Lazy-load model so importing this file does not require .env immediately."""
    global MODEL
    if MODEL is None:
        MODEL = build_model()
    return MODEL


def extract_json(text: str) -> dict[str, Any]:
    """从模型回复中提取 JSON。

    教学项目里保留这个小函数，避免模型偶尔在 JSON 外面加解释文字。
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start == -1 or end == 0:
            raise
        return json.loads(text[start:end])


def read_email(state: EmailState) -> dict:
    email = state["email"]
    print(
        "Alfred is processing an email from "
        f"{email['sender']} with subject: {email['subject']}"
    )
    return {}


def classify_email(state: EmailState) -> dict:
    email = state["email"]

    prompt = f"""
You are Alfred, a careful butler.
Analyze this email and determine if it is spam or legitimate.

Email:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Return strict JSON only. Do not use Markdown.

Schema:
{{
  "is_spam": true or false,
  "spam_reason": string or null,
  "email_category": "inquiry" | "complaint" | "thank you" | "request" | "information" | "general" | null
}}
"""

    response = get_model().invoke([HumanMessage(content=prompt)])
    parsed = extract_json(str(response.content))

    return {
        "is_spam": bool(parsed["is_spam"]),
        "spam_reason": parsed.get("spam_reason"),
        "email_category": parsed.get("email_category"),
        "messages": state.get("messages", [])
        + [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": str(response.content)},
        ],
    }


def route_email(state: EmailState) -> Literal["spam", "legitimate"]:
    if state["is_spam"]:
        return "spam"
    return "legitimate"


def handle_spam(state: EmailState) -> dict:
    print(f"Alfred has marked the email as spam. Reason: {state['spam_reason']}")
    print("The email has been moved to the spam folder.")
    return {}


def draft_response(state: EmailState) -> dict:
    email = state["email"]
    category = state.get("email_category") or "general"

    prompt = f"""
You are Alfred, a polite and concise butler.
Draft a brief professional response that Mr. Hugg can review before sending.

Email:
From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Email category: {category}

Return only the response body. Do not use Markdown.
"""

    response = get_model().invoke([HumanMessage(content=prompt)])

    return {
        "draft_response": str(response.content),
        "messages": state.get("messages", [])
        + [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": str(response.content)},
        ],
    }


def notify_mr_hugg(state: EmailState) -> dict:
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

    print("\nProcessing legitimate email with LLM...")
    legitimate_result = graph.invoke(initial_state(legitimate_email))
    print("Final legitimate state:")
    print(legitimate_result)

    print("\nProcessing spam email with LLM...")
    spam_result = graph.invoke(initial_state(spam_email))
    print("Final spam state:")
    print(spam_result)
