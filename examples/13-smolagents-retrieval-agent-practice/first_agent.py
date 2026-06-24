"""
Day13: first_agent.py

这是第 13 天的真实 Agent 练习代码。

今天重点是：
1. 把本地知识库封装成检索工具。
2. 让 CodeAgent 自己决定检索关键词。
3. 观察工具返回的 observation 如何进入下一轮推理。
4. 理解传统 RAG 和 Agentic RAG 的差异。

运行：

python first_agent.py
"""

from __future__ import annotations

from smolagents import CodeAgent

from model_config import build_model
from tools import get_retrieval_tools


def build_retrieval_agent() -> CodeAgent:
    """
    创建一个只包含本地知识库检索工具的 CodeAgent。

    CodeAgent 会生成 Python 代码调用 local_knowledge_retriever，
    检索结果会作为 observation 返回给 Agent。
    """
    return CodeAgent(
        tools=get_retrieval_tools(),
        model=build_model(),
        max_steps=8,
    )


def run_basic_retrieval_demo(agent: CodeAgent) -> None:
    """
    练习 1：基础检索问答。
    """
    task = """
请基于本地知识库回答：
豪华超级英雄主题派对应该如何设计装饰、餐饮和娱乐？

要求：
1. 先调用检索工具查资料。
2. 回答时说明你参考了哪些资料来源。
3. 不要凭空编造知识库外的细节。
"""

    print("=" * 80)
    print("练习 1：本地知识库检索")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def run_agentic_rag_demo(agent: CodeAgent) -> None:
    """
    练习 2：Agentic RAG 多步检索。
    """
    task = """
请为 Alfred 设计一份豪华超级英雄主题派对方案。

请不要只检索一次。你需要自己把问题拆成至少三个检索方向：
- 装饰
- 餐饮
- 娱乐

每个方向都调用一次 local_knowledge_retriever。
最后综合 observation，用中文输出一个结构化方案。
请严格基于检索 observation 中出现的信息，不要补充资料中没有出现的具体菜品、活动或装饰。
"""

    print("\n" + "=" * 80)
    print("练习 2：Agentic RAG 多步检索")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def run_project_rag_demo(agent: CodeAgent) -> None:
    """
    练习 3：迁移到自己的项目。
    """
    task = """
请基于本地知识库，回答下面两个问题：
1. Obsidian 学习笔记如何做成 RAG？
2. 996tokens 客服知识库适合检索哪些资料？

要求：
- 分别检索 Obsidian 和 996tokens 相关资料。
- 用中文分点输出。
"""

    print("\n" + "=" * 80)
    print("练习 3：迁移到自己的项目")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def main() -> None:
    agent = build_retrieval_agent()

    run_basic_retrieval_demo(agent)
    run_agentic_rag_demo(agent)
    run_project_rag_demo(agent)


if __name__ == "__main__":
    main()
