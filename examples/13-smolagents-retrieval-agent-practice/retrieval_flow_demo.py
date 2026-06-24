"""
Day13: retrieval_flow_demo.py

这个脚本不调用真实大模型。
它用确定性的代码演示：

1. 传统 RAG：用户问题 -> 检索一次 -> 组合答案。
2. Agentic RAG：拆成多个查询 -> 多次检索 -> 综合答案。

运行：

python retrieval_flow_demo.py
"""

from __future__ import annotations

from knowledge_base import format_retrieval_results, search_knowledge_base


def run_traditional_rag_demo() -> None:
    """演示传统 RAG 的单次检索流程。"""
    question = "帮我设计一个豪华超级英雄主题派对，包括装饰、餐饮和娱乐。"

    print("=" * 80)
    print("传统 RAG：检索一次")
    print("=" * 80)
    print(f"用户问题：{question}")

    results = search_knowledge_base(question, top_k=3)
    print(format_retrieval_results(results))

    print("\n传统 RAG 的特点：查询词固定，通常只检索一次。")


def run_agentic_rag_demo() -> None:
    """演示 Agentic RAG 的多步检索思路。"""
    planned_queries = [
        "豪华 超级英雄 派对 装饰 Gotham 金色 天鹅绒",
        "超级英雄 主题 餐饮 Hulk Iron Man 甜点",
        "超级英雄 派对 娱乐 DJ VR 互动 解谜",
    ]

    print("\n" + "=" * 80)
    print("Agentic RAG：拆问题，多次检索")
    print("=" * 80)

    for index, query in enumerate(planned_queries, start=1):
        print(f"\n子查询 {index}: {query}")
        results = search_knowledge_base(query, top_k=2)
        print(format_retrieval_results(results))

    print("\nAgentic RAG 的特点：智能体可以改写查询、多次检索，并综合多个 observation。")


def main() -> None:
    run_traditional_rag_demo()
    run_agentic_rag_demo()


if __name__ == "__main__":
    main()

