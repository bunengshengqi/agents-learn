"""
Day 20 code 02: multiple steps communicate through typed Events.

Run:
python 02_multi_step_events.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step


class ParsedQueryEvent(Event):
    original_query: str
    normalized_query: str


class RetrievedNotesEvent(Event):
    query: str
    notes: list[str]


class MultiStepWorkflow(Workflow):
    """StartEvent -> ParsedQueryEvent -> RetrievedNotesEvent -> StopEvent."""

    @step
    async def parse_query(self, ev: StartEvent) -> ParsedQueryEvent:
        query = ev.get("query", "")
        normalized = query.strip().lower()
        print(f"[parse_query] 原始问题：{query}")
        return ParsedQueryEvent(original_query=query, normalized_query=normalized)

    @step
    async def retrieve_notes(self, ev: ParsedQueryEvent) -> RetrievedNotesEvent:
        print(f"[retrieve_notes] 收到 ParsedQueryEvent：{ev.normalized_query}")
        notes = [
            "Workflow 用 Event 驱动 Step。",
            "Step 的类型提示决定事件如何流动。",
            "StopEvent 会结束整个工作流。",
        ]
        return RetrievedNotesEvent(query=ev.original_query, notes=notes)

    @step
    async def synthesize(self, ev: RetrievedNotesEvent) -> StopEvent:
        print("[synthesize] 收到 RetrievedNotesEvent，开始汇总。")
        answer = "\n".join(f"- {note}" for note in ev.notes)
        return StopEvent(result=f"问题：{ev.query}\n\n检索到的笔记：\n{answer}")


async def main() -> None:
    workflow = MultiStepWorkflow(timeout=10, verbose=True)
    result = await workflow.run(query=" LlamaIndex Workflow 是什么？ ")
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
