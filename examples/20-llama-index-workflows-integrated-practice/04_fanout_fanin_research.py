"""
04: Fan-out / fan-in research practice.

Goal:
- One step returns a list of Events.
- Several workers process the events.
- A final step receives list[ResultEvent] and summarizes everything.

Run:
python 04_fanout_fanin_research.py
"""

import asyncio

from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step


SOURCES = {
    "obsidian": "Obsidian notes say Workflow = Event + Step + Context.",
    "course": "The course explains Workflows through events, loops, branches, and RAG.",
    "code": "The code examples import from llama_index.core.workflow.",
}


class SourceSearchEvent(Event):
    source_name: str
    query: str


class SourceResultEvent(Event):
    source_name: str
    result: str


class FanoutFaninWorkflow(Workflow):
    @step
    async def split_query(self, ev: StartEvent) -> list[SourceSearchEvent]:
        query = ev.get("query", "Workflow")
        print("[split_query] fan-out to three sources")
        return [
            SourceSearchEvent(source_name="obsidian", query=query),
            SourceSearchEvent(source_name="course", query=query),
            SourceSearchEvent(source_name="code", query=query),
        ]

    @step
    async def search_source(self, ev: SourceSearchEvent) -> SourceResultEvent:
        print(f"[search_source] searching {ev.source_name}")
        return SourceResultEvent(
            source_name=ev.source_name,
            result=f"{SOURCES[ev.source_name]} Query: {ev.query}",
        )

    @step
    async def summarize(self, events: list[SourceResultEvent]) -> StopEvent:
        print("[summarize] fan-in completed")
        lines = [f"- {ev.source_name}: {ev.result}" for ev in events]
        return StopEvent(result="Research summary:\n" + "\n".join(lines))


async def main() -> None:
    workflow = FanoutFaninWorkflow(timeout=10, verbose=True)
    result = await workflow.run(query="How does Workflow support RAG?")
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
