"""
第19天 RAG 工具构建函数

这里用 SummaryIndex 构建一个轻量版 QueryEngine：
- 好处：不需要额外 embedding 模型，安装后就能跑。
- 课程里的 VectorStoreIndex + similarity_top_k=3 适合正式向量检索版。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from llama_index.core import SimpleDirectoryReader, SummaryIndex
from llama_index.core.tools import QueryEngineTool


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def build_query_engine(llm: Any):
    """读取 data/ 目录并创建 QueryEngine。"""
    documents = SimpleDirectoryReader(input_dir=str(DATA_DIR)).load_data()
    index = SummaryIndex.from_documents(documents)

    return index.as_query_engine(
        llm=llm,
        response_mode="tree_summarize",
    )


def build_persona_query_tool(llm: Any) -> QueryEngineTool:
    """把本地资料 QueryEngine 包装成 QueryEngineTool。"""
    query_engine = build_query_engine(llm)

    return QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name="alfred_persona_database",
        description=(
            "查询 Wayne Manor / Alfred 相关本地资料库。"
            "当用户询问人物偏好、晚宴策划、Day17/Day18/Day19 课程关系、"
            "QueryEngineTool 或 Agentic RAG 时使用。"
        ),
        return_direct=False,
    )
