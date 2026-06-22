"""
Day 7: Serverless API with OpenAI-Compatible Endpoint

这个脚本对应 Hugging Face 课程里的“无服务器 API（Serverless API）”部分。

但是这里不使用 Hugging Face 的 InferenceClient。
我们使用你自己的 OpenAI 兼容中转站：

OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=你的中转站地址
OPENAI_MODEL=你的模型名

对应知识点：
- Day 1：LLM 可以根据输入生成文本。
- Day 2：messages 是聊天模型的标准输入结构。
- Day 2：chat template 会把 messages 转换成模型真正理解的 prompt。
- Day 7：Serverless API 的本质是“不自己部署模型，直接通过 API 调用模型”。
- Day 7：工程上推荐使用 chat/messages，而不是自己手写特殊 token。
"""

import os

from dotenv import load_dotenv
from openai import OpenAI


# 读取项目根目录中的 .env 文件。
# 对应知识点：
# - 不要把 API Key 写死在代码里。
# - 使用环境变量管理密钥，更安全，也更方便切换模型和中转站。
load_dotenv()


def build_client() -> tuple[OpenAI, str]:
    """
    创建 OpenAI 兼容客户端。

    对应 Hugging Face 课程中的 Serverless API：
    - Hugging Face 示例使用 InferenceClient 调用远程模型。
    - 这里使用 OpenAI 客户端调用你自己的中转站。

    本质一样：
    Python 代码 -> API 服务 -> 远程模型 -> 返回结果
    """
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL")

    missing = []

    if not api_key:
        missing.append("OPENAI_API_KEY")
    if not base_url:
        missing.append("OPENAI_BASE_URL")
    if not model:
        missing.append("OPENAI_MODEL")

    if missing:
        raise ValueError("缺少环境变量：" + ", ".join(missing))

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
    )

    return client, model


def text_like_generation(client: OpenAI, model: str) -> str:
    """
    模拟课程里的 text_generation 思路。

    Hugging Face 原课程中直接传入：
    "The capital of France is"

    这更像“文本续写”：
    - 模型看到一段没写完的话；
    - 然后继续往后补。

    注意：
    OpenAI 兼容 chat 接口通常没有真正的 text_generation 方法。
    所以这里用 user message 模拟“只给一句未完成文本”的效果。

    对应知识点：
    - 如果只是给模型一段文本，模型可能把它当作续写任务。
    - 这就是为什么聊天模型需要 messages 和 chat template。
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "The capital of France is",
            }
        ],
        max_tokens=100,
        temperature=0.1,
    )

    return response.choices[0].message.content or ""


def chat_generation(client: OpenAI, model: str) -> str:
    """
    使用推荐的 chat/messages 方式调用模型。

    对应 Hugging Face 课程里推荐的 chat 方法：
    - 不手写特殊 token；
    - 不手写 chat template；
    - 只传标准 messages；
    - API 或模型服务负责把 messages 转成模型需要的底层格式。

    对应 Day 2 知识点：
    messages = [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."}
    ]

    system：
    - 定义模型身份和回答规则。

    user：
    - 用户当前问题。
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "你是一个简洁准确的问答助手。请只回答问题本身，不要重复题目。",
            },
            {
                "role": "user",
                "content": "法国的首都是哪里？",
            },
        ],
        max_tokens=100,
        temperature=0.1,
    )

    return response.choices[0].message.content or ""


def agent_style_generation(client: OpenAI, model: str) -> str:
    """
    演示 Agent 风格的 system prompt。

    这个函数不是完整 Agent，只是说明：
    - Serverless API 负责调用模型；
    - system prompt 可以规定 Agent 的行为；
    - 后面 Dummy Agent 会在这个基础上加入工具、Action、Observation。

    对应知识点：
    - Day 3：Agent Loop
    - Day 4：Thought
    - Day 5：Action
    - Day 6：Observation
    - Day 7：把这些封装成 Agent
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个教学用 Agent。"
                    "回答时请用两行：第一行写 Plan，第二行写 Final Answer。"
                    "Plan 只写简短步骤，不要展开隐藏推理。"
                ),
            },
            {
                "role": "user",
                "content": "如果我要做一个天气查询 Agent，最小流程是什么？",
            },
        ],
        max_tokens=300,
        temperature=0.1,
    )

    return response.choices[0].message.content or ""


def main() -> None:
    """
    主入口。

    这个脚本的学习目标：
    1. 证明你自己的 API 可以替代 Hugging Face Serverless API。
    2. 理解“直接文本生成”和“chat/messages 调用”的区别。
    3. 为后面的 Dummy Agent 做准备。
    """
    client, model = build_client()

    print("Day 7: Serverless API with OpenAI-Compatible Endpoint")
    print("=" * 60)

    print("1. 模拟 text_generation：只给模型一段未完成文本")
    print("-" * 60)
    text_output = text_like_generation(client, model)
    print(text_output)
    print("=" * 60)

    print("2. 推荐 chat/messages：让模型按聊天格式回答")
    print("-" * 60)
    chat_output = chat_generation(client, model)
    print(chat_output)
    print("=" * 60)

    print("3. Agent 风格 system prompt：为 Dummy Agent 做铺垫")
    print("-" * 60)
    agent_output = agent_style_generation(client, model)
    print(agent_output)
    print("=" * 60)

    print("学习结论：")
    print("Serverless API 的本质是远程调用模型，不需要自己部署。")
    print("工程上优先使用 chat/messages，让 API 自动处理聊天模板。")
    print("Dummy Agent 会在 chat/messages 基础上继续加入工具、Action 和 Observation。")


if __name__ == "__main__":
    main()


