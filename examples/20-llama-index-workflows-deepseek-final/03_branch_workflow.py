"""
Day 20 code 03: branch by returning different Event types.

Run:
python 03_branch_workflow.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step


class RAGEvent(Event):
    query: str


class DirectAnswerEvent(Event):
    query: str


class BranchWorkflow(Workflow):
    """One classifier step decides which downstream step should run."""

    @step
    async def classify(self, ctx: Context, ev: StartEvent) -> RAGEvent | DirectAnswerEvent:
        query = ev.get("query", "")
        await ctx.store.set("original_query", query)

        needs_rag = any(keyword in query for keyword in ["根据文档", "知识库", "笔记", "资料"])
        if needs_rag:
            print("[classify] 判断：需要查资料，走 RAGEvent。")
            return RAGEvent(query=query)

        print("[classify] 判断：普通问题，走 DirectAnswerEvent。")
        return DirectAnswerEvent(query=query)

    @step
    async def rag_answer(self, ctx: Context, ev: RAGEvent) -> StopEvent:
        original_query = await ctx.store.get("original_query")
        return StopEvent(
            result=(
                "走 RAG 分支。\n"
                f"原始问题：{original_query}\n"
                f"模拟答案：我会先检索本地知识库，再回答：{ev.query}"
            )
        )

    @step
    async def direct_answer(self, ev: DirectAnswerEvent) -> StopEvent:
        return StopEvent(
            result=(
                "走直接回答分支。\n"
                f"模拟答案：这是一个不需要检索资料的问题：{ev.query}"
            )
        )


async def run_case(query: str) -> None:
    print("\n" + "=" * 80)
    print(f"输入：{query}")
    print("=" * 80)
    workflow = BranchWorkflow(timeout=10, verbose=True)
    result = await workflow.run(query=query)
    print("\nFinal result:")
    print(result)


async def main() -> None:
    await run_case("根据文档解释 LlamaIndex Workflow")
    await run_case("今天怎么安排学习计划？")


if __name__ == "__main__":
    asyncio.run(main())
