"""
Day 4: ReAct Prompt Demo

这个脚本用于对比：
1. 直接回答
2. 加入“先分析/规划，再回答”的 ReAct 风格提示

运行前需要在项目根目录准备 .env：

OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=你的中转站地址
OPENAI_MODEL=你的模型名
"""

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


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """调用 OpenAI 兼容接口。"""
    validate_config()

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content or ""


def main() -> None:
    """对比普通提示和 ReAct 风格提示。"""
    question = input("请输入要测试的问题：").strip()

    if not question:
        question = "一个客户有 16 条交易记录，其中一半是大额交易，大额交易里一半是跨境交易。跨境大额交易有几条？"

    direct_system_prompt = "你是一个中文助手，请直接回答用户问题。"

    react_system_prompt = """
你是一个擅长分析和规划的中文助手。

回答前请先做简短分析，但不要输出冗长的隐藏推理。
请按照下面格式输出：

Plan:
- 用 2 到 4 条列出解题步骤

Final Answer:
给出最终答案
"""

    print("\n问题：")
    print(question)
    print("=" * 60)

    print("普通提示输出：")
    direct_answer = call_llm(direct_system_prompt, question)
    print(direct_answer)
    print("=" * 60)

    print("ReAct / 逐步思考风格提示输出：")
    react_answer = call_llm(react_system_prompt, question)
    print(react_answer)
    print("=" * 60)

    print("观察重点：")
    print("1. 普通提示是否直接给答案？")
    print("2. ReAct 风格提示是否先拆步骤？")
    print("3. 哪一种更容易发现中间逻辑？")


if __name__ == "__main__":
    main()


