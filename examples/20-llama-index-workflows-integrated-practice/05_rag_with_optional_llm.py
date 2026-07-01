"""
05: RAG workflow with optional LLM.

Goal:
- Load local markdown knowledge.
- Retrieve relevant chunks.
- Generate an answer locally or with an LLM.

Run without API:
python 05_rag_with_optional_llm.py

Run with API:
python 05_rag_with_optional_llm.py --use-llm
"""

import argparse
import asyncio
import re
from pathlib import Path

from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step

from model_config import build_llm


DATA_PATH = Path(__file__).resolve().parent / "data" / "workflow_reference.md"


class NormalizedQueryEvent(Event):
    query: str
    use_llm: bool


class RetrievedContextEvent(Event):
    query: str
    use_llm: bool
    context: str
    sources: list[str]


def load_sections() -> list[tuple[str, str]]:
    text = DATA_PATH.read_text(encoding="utf-8")
    sections: list[tuple[str, str]] = []
    for part in text.split("## "):
        part = part.strip()
        if not part or part.startswith("#"):
            continue
        title, _, body = part.partition("\n")
        sections.append((title.strip(), body.strip()))
    return sections


def retrieve(query: str, top_k: int = 3) -> list[tuple[str, str, int]]:
    terms = [item.lower() for item in re.findall(r"[A-Za-z0-9_-]+|[\u4e00-\u9fff]+", query)]
    ranked: list[tuple[str, str, int]] = []

    for title, body in load_sections():
        haystack = f"{title}\n{body}".lower()
        score = sum(1 for term in terms if term.lower() in haystack)
        if score:
            ranked.append((title, body, score))

    ranked.sort(key=lambda item: item[2], reverse=True)
    if ranked:
        return ranked[:top_k]
    return [(title, body, 0) for title, body in load_sections()[:top_k]]


class OptionalLLMRAGWorkflow(Workflow):
    @step
    async def normalize_query(self, ctx: Context, ev: StartEvent) -> NormalizedQueryEvent:
        query = ev.get("query", "Workflow 如何实现 RAG？")
        use_llm = ev.get("use_llm", False)
        await ctx.store.set("original_query", query)
        return NormalizedQueryEvent(query=query.strip(), use_llm=use_llm)

    @step
    async def retrieve_context(self, ctx: Context, ev: NormalizedQueryEvent) -> RetrievedContextEvent:
        ranked = retrieve(ev.query)
        sources = [title for title, _, _ in ranked]
        context = "\n\n".join(f"[{title}]\n{body}" for title, body, _ in ranked)
        await ctx.store.set("sources", sources)
        print(f"[retrieve_context] sources={sources}")
        return RetrievedContextEvent(
            query=ev.query,
            use_llm=ev.use_llm,
            context=context,
            sources=sources,
        )

    @step
    async def answer(self, ctx: Context, ev: RetrievedContextEvent) -> StopEvent:
        if not ev.use_llm:
            return StopEvent(
                result=(
                    "Local answer without LLM:\n"
                    f"Question: {ev.query}\n"
                    f"Sources: {', '.join(ev.sources)}\n\n"
                    f"{ev.context}"
                )
            )

        llm = build_llm(max_tokens=800)
        prompt = f"""你是 LlamaIndex Workflow 学习助教。
请只根据给定资料回答问题。先给结论，再解释流程。不要编造资料外的 API。

Question:
{ev.query}

Context:
{ev.context}
"""
        response = await llm.acomplete(prompt)
        sources = await ctx.store.get("sources")
        return StopEvent(result=f"Sources: {', '.join(sources)}\n\n{response.text.strip()}")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", default="Workflow 如何实现 RAG？")
    parser.add_argument("--use-llm", action="store_true")
    args = parser.parse_args()

    workflow = OptionalLLMRAGWorkflow(timeout=60, verbose=True)
    result = await workflow.run(query=args.query, use_llm=args.use_llm)
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
