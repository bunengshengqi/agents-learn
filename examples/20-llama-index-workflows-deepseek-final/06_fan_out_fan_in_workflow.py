"""
Day 20 code 06: fan-out and fan-in with collection Events.

Run:
python 06_fan_out_fan_in_workflow.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step


SOURCE_DATABASE = {
    "obsidian": "Obsidian 笔记里记录：Workflow = Event 驱动 Step。",
    "course": "课程资料里强调：RAG 可以用 Workflow 拆成加载、检索、生成、评估。",
    "code": "代码库里最常见的骨架是 Workflow + @step + StartEvent + StopEvent。",
}


class SourceQueryEvent(Event):
    source: str
    query: str


class SourceResultEvent(Event):
    source: str
    text: str


class FanOutFanInWorkflow(Workflow):
    """Split one query into several source searches, then collect all results."""

    @step
    async def fan_out(self, ev: StartEvent) -> list[SourceQueryEvent]:
        query = ev.get("query", "Workflow")
        print("[fan_out] 同时生成 3 个检索任务。")
        return [
            SourceQueryEvent(source="obsidian", query=query),
            SourceQueryEvent(source="course", query=query),
            SourceQueryEvent(source="code", query=query),
        ]

    @step
    async def search_one_source(self, ev: SourceQueryEvent) -> SourceResultEvent:
        print(f"[search_one_source] 查询 {ev.source}")
        text = SOURCE_DATABASE[ev.source]
        return SourceResultEvent(source=ev.source, text=text)

    @step
    async def summarize(self, events: list[SourceResultEvent]) -> StopEvent:
        print("[summarize] 三个来源都返回了，开始汇总。")
        lines = [f"- {ev.source}: {ev.text}" for ev in events]
        return StopEvent(result="汇总结果：\n" + "\n".join(lines))


async def main() -> None:
    workflow = FanOutFanInWorkflow(timeout=10, verbose=True)
    result = await workflow.run(query="Workflow 和 RAG")
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
