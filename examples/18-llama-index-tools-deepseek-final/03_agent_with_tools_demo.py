"""
第18天代码 03：Agent 同时使用 FunctionTool + QueryEngineTool

注意：
新版 LlamaIndex 的 FunctionAgent 是异步工作流。
所以这里必须使用 async main + await agent.run() + asyncio.run(main())。

运行：
python 03_agent_with_tools_demo.py
"""

import asyncio
from datetime import datetime

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.core.tools import FunctionTool, QueryEngineTool

from model_config import init_models


def is_workday(date: str) -> str:
    """判断给定日期是否为工作日。date 格式为 YYYY-MM-DD。"""
    dt = datetime.strptime(date, "%Y-%m-%d")
    if dt.weekday() < 5:
        return f"{date} 是周一到周五，按普通规则属于工作日。"
    return f"{date} 是周六或周日，按普通规则不属于工作日。"


def build_notes_tool() -> QueryEngineTool:
    documents = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        similarity_top_k=3,
    )

    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name="notes_query_tool",
        description=(
            "查询本地课程笔记和银行知识库，"
            "适合回答 LlamaIndex Tools、RAG、Agent 工具选择、银行知识库等问题。"
        ),
    )


async def main() -> None:
    init_models()

    workday_tool = FunctionTool.from_defaults(
        fn=is_workday,
        name="is_workday_tool",
        description="判断某个日期是否为工作日，输入格式为 YYYY-MM-DD。",
    )

    notes_tool = build_notes_tool()

    agent = FunctionAgent(
        tools=[workday_tool, notes_tool],
        system_prompt=(
            "你是一个学习助手。"
            "如果用户问日期判断，使用 is_workday_tool。"
            "如果用户问课程笔记、RAG、LlamaIndex 工具类型，使用 notes_query_tool。"
            "回答要简洁清楚。"
        ),
    )

    print("====== 示例 1：需要调用 FunctionTool ======")
    response1 = await agent.run("2026-07-01 是工作日吗？")
    print(response1)

    print("\n====== 示例 2：需要调用 QueryEngineTool ======")
    response2 = await agent.run("第18天的 QueryEngineTool 适合什么场景？")
    print(response2)


if __name__ == "__main__":
    asyncio.run(main())
