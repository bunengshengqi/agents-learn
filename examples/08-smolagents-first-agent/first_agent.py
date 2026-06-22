"""
Day 8: First Agent with smolagents

学习目标：
1. 使用 smolagents 创建第一个 CodeAgent。
2. 使用 OpenAI 兼容接口接入自己的中转站。
3. 通过 @tool 给 Agent 添加工具能力。

运行前准备：
1. 安装依赖：
   pip install -r examples/08-smolagents-first-agent/requirements.txt

2. 在项目根目录创建 .env：
   OPENAI_API_KEY=你的 key
   OPENAI_BASE_URL=你的中转站地址，例如 https://xxx.com/v1
   OPENAI_MODEL=你的模型名
"""

import argparse
from typing import Any

from smolagents import CodeAgent

from model_config import build_model
from tools import get_current_time_in_timezone, multiply_numbers


def build_tools() -> list[Any]:
    """
    Register tools for the agent.

    Day 8 的重点是：
    - 工具负责干活；
    - 模型负责判断什么时候调用工具；
    - smolagents 负责调度循环。
    """
    tools: list[Any] = [
        get_current_time_in_timezone,
        multiply_numbers,
    ]

    try:
        from smolagents import FinalAnswerTool

        tools.append(FinalAnswerTool())
    except ImportError:
        pass

    return tools


def build_agent() -> CodeAgent:
    """Create a teaching-oriented CodeAgent."""
    return CodeAgent(
        model=build_model(),
        tools=build_tools(),
        max_steps=6,
        verbosity_level=1,
        instructions=(
            "你是一个教学用智能体。"
            "优先使用工具获得可验证结果。"
            "回答时用中文，简洁说明你调用了什么工具以及最终答案。"
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Day 8 smolagents first agent demo")
    parser.add_argument(
        "question",
        nargs="?",
        default="现在 Asia/Shanghai 是几点？顺便计算 7 乘以 8。",
        help="要交给 Agent 处理的问题",
    )
    args = parser.parse_args()

    agent = build_agent()
    result = agent.run(args.question)
    print(result)


if __name__ == "__main__":
    main()

