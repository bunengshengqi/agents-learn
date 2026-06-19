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
    """根据 messages 调用大模型。"""
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


def main() -> None:
    """单轮 messages 调用示例。"""

    user_input = input("请输入你的问题：").strip()

    if not user_input:
        print("问题不能为空。")
        return

    messages = [
        {
            "role": "system",
            "content": (
                "你是一名 AI Agent 学习助手。"
                "请使用中文回答，解释要清晰，适合初学者理解。"
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    print("\n当前发送给模型的 messages：")
    print(messages)
    print("-" * 60)

    answer = call_llm(messages)

    print("助手回答：")
    print(answer)


if __name__ == "__main__":
    main()
