"""
第19天代码 03：使用 QueryEngineTool 创建 Agentic RAG 智能体

这个脚本对应课程里的 QueryEngineTool 示例。

运行：
python 03_query_engine_tool_agent.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.agent.workflow import AgentWorkflow

from model_config import build_llm
from rag_tools import build_persona_query_tool


async def main() -> None:
    """让 Agent 自主决定调用 RAG 工具。"""
    llm = build_llm(function_calling=False)
    query_engine_tool = build_persona_query_tool(llm)

    agent = AgentWorkflow.from_tools_or_functions(
        [query_engine_tool],
        llm=llm,
        system_prompt=(
            "你是 Alfred 的学习助手。"
            "如果用户询问 Wayne Manor、人物偏好、晚宴策划或 LlamaIndex 课程资料，"
            "必须调用 alfred_persona_database 工具查询本地资料后再回答。"
        ),
        verbose=True,
    )

    question = "根据本地资料，Diana 和 Selina 的晚宴偏好分别是什么？"
    response = await agent.run(question)

    print("\nFinal Answer:")
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
