"""
Day 20 code 01: the smallest runnable Workflow.

Run:
python 01_minimal_workflow.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.workflow import StartEvent, StopEvent, Workflow, step


class HelloWorkflow(Workflow):
    """StartEvent -> greet -> StopEvent."""

    @step
    async def greet(self, ev: StartEvent) -> StopEvent:
        name = ev.get("name", "Alfred")
        return StopEvent(
            result=f"你好，{name}。这是最小 Workflow：StartEvent -> greet -> StopEvent。"
        )


async def main() -> None:
    workflow = HelloWorkflow(timeout=10, verbose=True)
    result = await workflow.run(name="Alfred")
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
