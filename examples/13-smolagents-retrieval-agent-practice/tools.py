"""
Day13: tools.py

这个文件把本地知识库检索能力封装成 smolagents 工具。

Agentic RAG 的关键是：检索不是固定流程，而是智能体可以自己决定
是否检索、检索什么关键词、是否需要多次检索。
"""

from __future__ import annotations

from smolagents import Tool

from knowledge_base import format_retrieval_results, search_knowledge_base


class LocalKnowledgeRetrieverTool(Tool):
    """
    本地知识库检索工具。

    这个工具模拟课程中的自定义知识库工具：
    用户给一个 query，工具返回最相关的文档片段作为 observation。
    """

    name = "local_knowledge_retriever"
    description = (
        "从本地知识库检索与派对策划、Agentic RAG、Obsidian 笔记、996tokens 客服相关的资料。"
        "适合在回答前先查资料。"
    )
    inputs = {
        "query": {
            "type": "string",
            "description": "检索查询词，应尽量具体，比如“豪华 超级英雄 派对 餐饮 娱乐 装饰”。",
        },
        "top_k": {
            "type": "integer",
            "description": "返回前几个最相关文档，建议 2 到 5。",
            "nullable": True,
        },
    }
    output_type = "string"

    def forward(self, query: str, top_k: int | None = 3) -> str:
        """执行本地知识库检索，并返回格式化后的检索结果。"""
        if not isinstance(query, str):
            raise TypeError("query 必须是字符串。")

        safe_top_k = top_k if isinstance(top_k, int) and top_k > 0 else 3
        results = search_knowledge_base(query=query, top_k=safe_top_k)
        return format_retrieval_results(results)


def get_retrieval_tools() -> list:
    """返回 Day13 的检索工具列表。"""
    return [LocalKnowledgeRetrieverTool()]

