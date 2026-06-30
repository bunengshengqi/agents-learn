"""
第19天代码 04：多智能体 AgentWorkflow

这个脚本创建两个 ReActAgent：
- calculator：负责计算
- info_lookup：负责查询本地 RAG 知识库

运行：
python 04_multi_agent_workflow.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.agent.workflow import AgentWorkflow, ReActAgent

from model_config import build_llm
from rag_tools import build_persona_query_tool


def add(a: int, b: int) -> int:
    """Add two numbers and return the result."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract b from a and return the result."""
    return a - b


async def run_question(agent: AgentWorkflow, question: str) -> None:
    """运行一个问题并打印结果。"""
    print("\n" + "=" * 80)
    print(f"问题：{question}")
    print("=" * 80)
    response = await agent.run(user_msg=question)
    print("\nFinal Answer:")
    print(response)


async def main() -> None:
    """创建并运行多智能体 workflow。"""
    llm = build_llm(function_calling=False)
    query_engine_tool = build_persona_query_tool(llm)

    calculator_agent = ReActAgent(
        name="calculator",
        description="负责基础加减法计算。遇到算术加法或减法任务时使用。",
        system_prompt=(
            "你是 calculator，只负责基础加减法。"
            "遇到计算问题必须调用 add 或 subtract 工具。"
            "如果问题是资料查询或晚宴偏好，请交接给 info_lookup。"
        ),
        tools=[add, subtract],
        can_handoff_to=["info_lookup"],
        llm=llm,
        verbose=True,
    )

    query_agent = ReActAgent(
        name="info_lookup",
        description="负责查询 Wayne Manor、Alfred、晚宴偏好和 LlamaIndex 课程资料。",
        system_prompt=(
            "你是 info_lookup，只负责资料查询。"
            "遇到人物偏好、晚宴策划或课程资料问题，必须使用 alfred_persona_database。"
            "如果问题是纯加减法，请交接给 calculator。"
        ),
        tools=[query_engine_tool],
        can_handoff_to=["calculator"],
        llm=llm,
        verbose=True,
    )

    workflow = AgentWorkflow(
        agents=[calculator_agent, query_agent],
        root_agent="calculator",
        timeout=120,
    )

    await run_question(workflow, "请计算 5 加 3。")
    await run_question(workflow, "根据本地资料，Clark 的晚宴偏好是什么？")


if __name__ == "__main__":
    asyncio.run(main())
