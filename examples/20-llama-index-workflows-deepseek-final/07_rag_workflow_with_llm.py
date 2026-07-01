"""
Day 20 code 07: a runnable RAG-style Workflow.

This script keeps the RAG mechanics visible:
1. StartEvent carries the user query.
2. retrieve_docs searches local markdown chunks.
3. generate_answer either calls the configured LLM or prints a no-LLM answer.

Run without API call:
python 07_rag_workflow_with_llm.py --no-llm

Run with your OpenAI-compatible API from .env:
python 07_rag_workflow_with_llm.py
"""

from __future__ import annotations

import argparse
import asyncio
import re
from pathlib import Path

from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step

from model_config import build_llm


DATA_PATH = Path(__file__).resolve().parent / "data" / "workflow_knowledge.md"
IMPORTANT_TERMS = [
    "workflow",
    "工作流",
    "event",
    "事件",
    "step",
    "步骤",
    "context",
    "状态",
    "branch",
    "分支",
    "loop",
    "循环",
    "rag",
    "检索",
    "fan-out",
    "fan-in",
    "agentworkflow",
    "智能体",
]


class QueryEvent(Event):
    query: str
    use_llm: bool


class RetrievedDocsEvent(Event):
    query: str
    use_llm: bool
    context_text: str
    sources: list[str]


def load_chunks() -> list[tuple[str, str]]:
    """Load local markdown sections as small searchable chunks."""
    text = DATA_PATH.read_text(encoding="utf-8")
    chunks: list[tuple[str, str]] = []
    for raw_section in text.split("### "):
        section = raw_section.strip()
        if not section:
            continue
        first_line, _, body = section.partition("\n")
        title = first_line.strip()
        chunks.append((title, body.strip()))
    return chunks


def extract_terms(query: str) -> list[str]:
    terms = [term.lower() for term in re.findall(r"[A-Za-z0-9_-]+", query)]
    terms.extend(term for term in IMPORTANT_TERMS if term.lower() in query.lower())
    return sorted(set(terms), key=len, reverse=True)


def rank_chunks(query: str, top_k: int = 3) -> list[tuple[str, str, int]]:
    terms = extract_terms(query)
    ranked: list[tuple[str, str, int]] = []
    for title, body in load_chunks():
        haystack = f"{title}\n{body}".lower()
        score = sum(1 for term in terms if term.lower() in haystack)
        if score:
            ranked.append((title, body, score))

    ranked.sort(key=lambda item: item[2], reverse=True)
    if ranked:
        return ranked[:top_k]

    return [(title, body, 0) for title, body in load_chunks()[:top_k]]


class LocalRAGWorkflow(Workflow):
    """A small RAG pipeline implemented as a Workflow."""

    @step
    async def prepare_query(self, ctx: Context, ev: StartEvent) -> QueryEvent:
        query = ev.get("query", "LlamaIndex Workflow 是什么？")
        use_llm = ev.get("use_llm", True)
        await ctx.store.set("original_query", query)
        await ctx.store.set("use_llm", use_llm)
        print(f"[prepare_query] query={query}, use_llm={use_llm}")
        return QueryEvent(query=query, use_llm=use_llm)

    @step
    async def retrieve_docs(self, ctx: Context, ev: QueryEvent) -> RetrievedDocsEvent:
        ranked = rank_chunks(ev.query, top_k=3)
        sources = [title for title, _, _ in ranked]
        context_text = "\n\n".join(
            f"[{title}]\n{body}" for title, body, _ in ranked
        )
        await ctx.store.set("retrieved_sources", sources)
        print(f"[retrieve_docs] 命中来源：{', '.join(sources)}")
        return RetrievedDocsEvent(
            query=ev.query,
            use_llm=ev.use_llm,
            context_text=context_text,
            sources=sources,
        )

    @step
    async def generate_answer(self, ctx: Context, ev: RetrievedDocsEvent) -> StopEvent:
        if not ev.use_llm:
            return StopEvent(
                result=(
                    "未调用 LLM，只展示检索上下文。\n\n"
                    f"问题：{ev.query}\n"
                    f"来源：{', '.join(ev.sources)}\n\n"
                    f"{ev.context_text}"
                )
            )

        llm = build_llm(max_tokens=800)
        prompt = f"""你是一个帮助用户学习 LlamaIndex 的中文助教。
请只根据下面的本地资料回答问题。回答要适合初学者，先给结论，再解释流程。
如果需要输出代码，必须使用资料中的当前导入路径，不要编造旧路径。

用户问题：
{ev.query}

本地资料：
{ev.context_text}
"""
        response = await llm.acomplete(prompt)
        sources = await ctx.store.get("retrieved_sources")
        return StopEvent(
            result=(
                f"资料来源：{', '.join(sources)}\n\n"
                f"{response.text.strip()}"
            )
        )


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        default="LlamaIndex Workflow 怎么实现 RAG？",
        help="要提问的问题",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="只跑检索流程，不调用 API",
    )
    args = parser.parse_args()

    workflow = LocalRAGWorkflow(timeout=60, verbose=True)
    result = await workflow.run(query=args.query, use_llm=not args.no_llm)
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
