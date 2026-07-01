"""
Day 20 code 04: loop by returning an Event that triggers a previous step.

Run:
python 04_loop_workflow.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step


CORPUS = [
    "LlamaIndex Workflow uses Event and Step to build maintainable RAG pipelines.",
    "Context stores shared state such as query, retry_count, documents, and traces.",
    "A RAG loop can retrieve, check quality, rewrite the query, and retrieve again.",
]


class RetrieveEvent(Event):
    query: str
    attempt: int
    max_attempts: int


class CheckEvent(Event):
    query: str
    attempt: int
    max_attempts: int
    snippets: list[str]


class LoopWorkflow(Workflow):
    """Retrieve -> check -> maybe rewrite -> retrieve again."""

    @step
    async def start(self, ev: StartEvent) -> RetrieveEvent:
        query = ev.get("query", "复杂流程怎么做")
        return RetrieveEvent(query=query, attempt=1, max_attempts=3)

    @step
    async def retrieve(self, ev: RetrieveEvent) -> CheckEvent:
        print(f"[retrieve] 第 {ev.attempt} 次检索，query={ev.query}")
        terms = [term.lower() for term in ev.query.split()]
        snippets = [
            text
            for text in CORPUS
            if any(term in text.lower() for term in terms)
        ]
        return CheckEvent(
            query=ev.query,
            attempt=ev.attempt,
            max_attempts=ev.max_attempts,
            snippets=snippets,
        )

    @step
    async def check_quality(self, ev: CheckEvent) -> RetrieveEvent | StopEvent:
        if ev.snippets:
            return StopEvent(
                result=(
                    f"第 {ev.attempt} 次检索成功。\n"
                    f"最终 query：{ev.query}\n"
                    "命中的资料：\n"
                    + "\n".join(f"- {item}" for item in ev.snippets)
                )
            )

        if ev.attempt >= ev.max_attempts:
            return StopEvent(
                result=(
                    f"已经尝试 {ev.attempt} 次，仍然没有找到足够资料。\n"
                    "真实项目里这里可以转人工、扩大检索范围或返回澄清问题。"
                )
            )

        rewritten_query = f"{ev.query} LlamaIndex Workflow Event Step Context"
        print(f"[check_quality] 资料不足，改写 query：{rewritten_query}")
        return RetrieveEvent(
            query=rewritten_query,
            attempt=ev.attempt + 1,
            max_attempts=ev.max_attempts,
        )


async def main() -> None:
    workflow = LoopWorkflow(timeout=10, verbose=True)
    result = await workflow.run(query="复杂流程怎么做")
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
