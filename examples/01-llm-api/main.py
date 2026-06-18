import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL")


def validate_config() -> None:
    """检查必要配置。"""
    missing = []

    if not api_key:
        missing.append("OPENAI_API_KEY")
    if not base_url:
        missing.append("OPENAI_BASE_URL")
    if not model:
        missing.append("OPENAI_MODEL")

    if missing:
        raise ValueError(
            "缺少环境变量：" + ", ".join(missing)
        )


def chat(question: str) -> str:
    """调用大模型并返回回答。"""
    validate_config()

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一名AI Agent学习助手，请使用中文回答。",
                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
            temperature=0.3,
        )

        return response.choices[0].message.content or "模型没有返回内容。"

    except Exception as exc:
        return (
            f"模型调用失败\n"
            f"异常类型：{type(exc).__name__}\n"
            f"异常信息：{exc}"
        )


def main() -> None:
    question = input("请输入你的问题：").strip()

    if not question:
        print("问题不能为空。")
        return

    print("-" * 60)
    print(chat(question))


if __name__ == "__main__":
    main()
