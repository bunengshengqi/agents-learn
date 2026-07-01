"""
03: Looping Agentic RAG practice.

Goal:
- Retrieve context.
- Evaluate whether context is enough.
- If not enough, rewrite query and retrieve again.
- Stop when enough context is found or max retries is reached.

Run:
python 03_loop_agentic_rag.py
"""

import asyncio

from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step


DOCUMENTS = [
    "Workflow 使用 Event 驱动 Step，适合把复杂 Agent 应用拆成清楚的步骤。",
    "Context 可以在一次 Workflow 运行中保存状态，比如 retry_count、trace、retrieved_docs。",
    "RAG 流程通常包括加载资料、检索资料、构造 prompt、调用 LLM 和评估答案。",
    "Loop 循环可以用于 Agentic RAG：检索不足时改写 query，再次检索。",
]


class RetrieveEvent(Event):
    query: str
    attempt: int
    max_attempts: int


class RetrievedEvent(Event):
    query: str
    attempt: int
    max_attempts: int
    docs: list[str]


def search_docs(query: str) -> list[str]:
    terms = [term.lower() for term in query.split()]
    return [
        doc for doc in DOCUMENTS if any(term in doc.lower() for term in terms)
    ]


class LoopingRAGWorkflow(Workflow):
    @step
    async def start(self, ctx: Context, ev: StartEvent) -> RetrieveEvent:
        query = ev.get("query", "资料不够时怎么办")
        await ctx.store.set("original_query", query)
        await ctx.store.set("trace", [])
        return RetrieveEvent(query=query, attempt=1, max_attempts=3)

    @step
    async def retrieve(self, ctx: Context, ev: RetrieveEvent) -> RetrievedEvent:
        docs = search_docs(ev.query)
        trace = await ctx.store.get("trace")
        trace.append(f"attempt={ev.attempt}, query={ev.query}, hits={len(docs)}")
        await ctx.store.set("trace", trace)
        print(f"[retrieve] attempt={ev.attempt}, hits={len(docs)}")
        return RetrievedEvent(
            query=ev.query,
            attempt=ev.attempt,
            max_attempts=ev.max_attempts,
            docs=docs,
        )

    @step
    async def evaluate(self, ctx: Context, ev: RetrievedEvent) -> RetrieveEvent | StopEvent:
        if len(ev.docs) >= 2:
            trace = await ctx.store.get("trace")
            return StopEvent(
                result={
                    "status": "enough_context",
                    "final_query": ev.query,
                    "docs": ev.docs,
                    "trace": trace,
                }
            )

        if ev.attempt >= ev.max_attempts:
            trace = await ctx.store.get("trace")
            return StopEvent(
                result={
                    "status": "max_attempts_reached",
                    "final_query": ev.query,
                    "docs": ev.docs,
                    "trace": trace,
                }
            )

        rewritten = f"{ev.query} Workflow Context RAG Loop"
        print(f"[evaluate] context not enough, rewrite query: {rewritten}")
        return RetrieveEvent(
            query=rewritten,
            attempt=ev.attempt + 1,
            max_attempts=ev.max_attempts,
        )


async def main() -> None:
    workflow = LoopingRAGWorkflow(timeout=10, verbose=True)
    result = await workflow.run(query="资料不够时怎么办")
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
