import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL")


def validate_config() -> None:
    """检查环境变量是否配置完整。"""
    missing = []

    if not api_key:
        missing.append("OPENAI_API_KEY")
    if not base_url:
        missing.append("OPENAI_BASE_URL")
    if not model:
        missing.append("OPENAI_MODEL")

    if missing:
        raise ValueError("缺少环境变量：" + ", ".join(missing))


def call_llm(messages: list[dict[str, str]]) -> str:
    """根据完整 messages 调用大模型。"""
    validate_config()

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3,
        )

        return response.choices[0].message.content or "模型没有返回内容。"

    except Exception as exc:
        return (
            "模型调用失败\n"
            f"异常类型：{type(exc).__name__}\n"
            f"异常信息：{exc}"
        )


def trim_messages(
    messages: list[dict[str, str]],
    max_rounds: int = 5,
) -> list[dict[str, str]]:
    """
    限制 messages 长度。

    保留第一条 system 消息。
    只保留最近 max_rounds 轮 user/assistant 对话。

    一轮对话通常包含：
    - 一条 user
    - 一条 assistant
    """

    if not messages:
        return messages

    system_message = messages[0]
    history_messages = messages[1:]

    max_history_count = max_rounds * 2
    trimmed_history = history_messages[-max_history_count:]

    return [system_message] + trimmed_history


def print_messages_summary(messages: list[dict[str, str]]) -> None:
    """打印当前 messages 的简要情况，帮助理解上下文。"""

    print("\n当前 messages 概览：")
    print(f"messages 总数量：{len(messages)}")

    for index, message in enumerate(messages, start=1):
        role = message["role"]
        content = message["content"].replace("\n", " ")

        if len(content) > 40:
            content = content[:40] + "..."

        print(f"{index}. role={role}, content={content}")

    print("-" * 60)


def main() -> None:
    """多轮对话示例。"""

    messages = [
        {
            "role": "system",
            "content": (
                "你是一名 AI Agent 学习助手。"
                "请使用中文回答。"
                "回答要清晰、准确，适合初学者理解。"
                "当用户让你结合银行 RPA 经历举例时，请尽量用银行自动化场景解释。"
            ),
        }
    ]

    print("Day 2：Messages 多轮对话练习")
    print("输入 exit / quit / q 退出程序")
    print("-" * 60)

    while True:
        user_input = input("用户：").strip()

        if user_input.lower() in {"exit", "quit", "q"}:
            print("程序已退出。")
            break

        if not user_input:
            print("输入不能为空。")
            continue

        # 1. 把用户这次输入加入 messages
        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        # 2. 限制历史长度，避免 messages 无限增长
        messages = trim_messages(messages, max_rounds=5)

        # 3. 把完整 messages 发给模型
        answer = call_llm(messages)

        # 4. 把模型回答也加入 messages
        messages.append(
            {
                "role": "assistant",
                "content": answer,
            }
        )

        print("\n助手：")
        print(answer)
        print("-" * 60)

        # 5. 打印 messages 概览，帮助你理解上下文是怎么保存的
        print_messages_summary(messages)


if __name__ == "__main__":
    main()
