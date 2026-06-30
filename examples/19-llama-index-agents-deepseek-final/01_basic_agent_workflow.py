"""
第19天代码 01：基础 AgentWorkflow + FunctionTool

这个脚本对应课程里的 multiply 示例。

运行：
python 01_basic_agent_workflow.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.tools import FunctionTool

from model_config import build_llm


def multiply(a: int, b: int) -> int:
    """Multiplies two integers and returns the resulting integer."""
    return a * b


async def main() -> None:
    """创建一个带 multiply 工具的 AgentWorkflow。"""
    llm = build_llm(function_calling=False)

    multiply_tool = FunctionTool.from_defaults(
        fn=multiply,
        name="multiply",
        description="用于计算两个整数的乘积。参数 a 和 b 都是整数。",
    )

    agent = AgentWorkflow.from_tools_or_functions(
        [multiply_tool],
        llm=llm,
        system_prompt=(
            "你是一个会调用工具的计算助手。"
            "遇到乘法时必须调用 multiply 工具，不要自己心算。"
            "最后用中文简洁回答。"
        ),
        verbose=True,
    )

    response = await agent.run("请计算 7 乘以 8。")
    print("\nFinal Answer:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
