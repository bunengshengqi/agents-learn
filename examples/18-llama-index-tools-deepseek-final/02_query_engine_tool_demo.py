"""
第18天代码 02：QueryEngineTool 示例

QueryEngineTool:
把第17天学到的 QueryEngine 包装成 Agent 可以调用的工具。

运行：
python 02_query_engine_tool_demo.py
"""

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.tools import QueryEngineTool

from model_config import init_models


def build_query_engine():
    init_models()

    documents = SimpleDirectoryReader(input_dir="./data").load_data()
    index = VectorStoreIndex.from_documents(documents)

    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        similarity_top_k=3,
    )

    return query_engine


def main() -> None:
    query_engine = build_query_engine()

    notes_tool = QueryEngineTool.from_defaults(
        query_engine=query_engine,
        name="agent_course_notes_tool",
        description=(
            "查询第18天 LlamaIndex Tools 学习笔记，"
            "适合回答 FunctionTool、QueryEngineTool、ToolSpecs、Utility Tools 的区别和使用场景。"
        ),
    )

    question = "FunctionTool 和 QueryEngineTool 分别适合什么场景？"

    print("====== QueryEngineTool 元数据 ======")
    print(f"name: {notes_tool.metadata.name}")
    print(f"description: {notes_tool.metadata.description}")

    print("\n====== 调用 QueryEngineTool ======")
    response = notes_tool.call(question)
    print(response)


if __name__ == "__main__":
    main()
