"""
01: Event pipeline practice.

Goal:
- Understand StartEvent, custom Event, @step, Context, and StopEvent.

Run:
python 01_event_pipeline.py
"""

import asyncio

from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step


class CleanRequestEvent(Event):
    original_task: str
    clean_task: str


class PlanEvent(Event):
    clean_task: str
    plan: list[str]


class DraftEvent(Event):
    clean_task: str
    plan: list[str]
    draft: str


async def add_trace(ctx: Context, message: str) -> None:
    trace = await ctx.store.get("trace", default=[])
    trace.append(message)
    await ctx.store.set("trace", trace)


class EventPipelineWorkflow(Workflow):
    @step
    async def receive_request(self, ctx: Context, ev: StartEvent) -> CleanRequestEvent:
        task = ev.get("task", "整理 Day20 Workflow 知识点")
        clean_task = " ".join(task.strip().split())
        await ctx.store.set("original_task", task)
        await add_trace(ctx, "receive_request: cleaned user task")
        return CleanRequestEvent(original_task=task, clean_task=clean_task)

    @step
    async def make_plan(self, ctx: Context, ev: CleanRequestEvent) -> PlanEvent:
        plan = [
            "识别任务目标",
            "拆分成多个 Step",
            "定义 Step 之间传递的 Event",
            "返回最终 StopEvent",
        ]
        await ctx.store.set("plan_size", len(plan))
        await add_trace(ctx, "make_plan: created a four-step learning plan")
        return PlanEvent(clean_task=ev.clean_task, plan=plan)

    @step
    async def write_draft(self, ctx: Context, ev: PlanEvent) -> DraftEvent:
        draft = "\n".join(f"{idx}. {item}" for idx, item in enumerate(ev.plan, start=1))
        await add_trace(ctx, "write_draft: converted plan into markdown text")
        return DraftEvent(clean_task=ev.clean_task, plan=ev.plan, draft=draft)

    @step
    async def finish(self, ctx: Context, ev: DraftEvent) -> StopEvent:
        original_task = await ctx.store.get("original_task")
        plan_size = await ctx.store.get("plan_size")
        trace = await ctx.store.get("trace")
        return StopEvent(
            result={
                "original_task": original_task,
                "clean_task": ev.clean_task,
                "plan_size": plan_size,
                "draft": ev.draft,
                "trace": trace,
            }
        )


async def main() -> None:
    workflow = EventPipelineWorkflow(timeout=10, verbose=True)
    result = await workflow.run(task="  帮我把 Day20 Workflow 知识点整理成练习路线  ")
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
