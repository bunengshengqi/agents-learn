"""
02: Branch router practice.

Goal:
- A classifier step returns different Event types.
- Different Event types trigger different downstream steps.

Run:
python 02_branch_router.py
"""

import asyncio

from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step


class PricingEvent(Event):
    question: str


class BugEvent(Event):
    question: str


class DocsEvent(Event):
    question: str


class FallbackEvent(Event):
    question: str


class SupportRouterWorkflow(Workflow):
    @step
    async def route(self, ctx: Context, ev: StartEvent) -> PricingEvent | BugEvent | DocsEvent | FallbackEvent:
        question = ev.get("question", "")
        lowered = question.lower()

        if any(word in question for word in ["价格", "套餐", "收费"]) or "price" in lowered:
            route_name = "pricing"
            event = PricingEvent(question=question)
        elif any(word in question for word in ["报错", "失败", "bug", "错误"]):
            route_name = "bug"
            event = BugEvent(question=question)
        elif any(word in question for word in ["文档", "怎么用", "教程", "workflow"]):
            route_name = "docs"
            event = DocsEvent(question=question)
        else:
            route_name = "fallback"
            event = FallbackEvent(question=question)

        await ctx.store.set("route_name", route_name)
        print(f"[route] selected route: {route_name}")
        return event

    @step
    async def answer_pricing(self, ctx: Context, ev: PricingEvent) -> StopEvent:
        route_name = await ctx.store.get("route_name")
        return StopEvent(result=f"[{route_name}] 这是价格问题，应该查询套餐表后回答：{ev.question}")

    @step
    async def answer_bug(self, ctx: Context, ev: BugEvent) -> StopEvent:
        route_name = await ctx.store.get("route_name")
        return StopEvent(result=f"[{route_name}] 这是故障问题，应该收集错误信息和复现步骤：{ev.question}")

    @step
    async def answer_docs(self, ctx: Context, ev: DocsEvent) -> StopEvent:
        route_name = await ctx.store.get("route_name")
        return StopEvent(result=f"[{route_name}] 这是文档问题，应该检索课程或 README：{ev.question}")

    @step
    async def answer_fallback(self, ctx: Context, ev: FallbackEvent) -> StopEvent:
        route_name = await ctx.store.get("route_name")
        return StopEvent(result=f"[{route_name}] 暂时无法分类，先追问用户更多上下文：{ev.question}")


async def run_case(question: str) -> None:
    print("\n" + "=" * 80)
    print(question)
    print("=" * 80)
    workflow = SupportRouterWorkflow(timeout=10, verbose=True)
    result = await workflow.run(question=question)
    print("Final result:")
    print(result)


async def main() -> None:
    questions = [
        "996tokens 的套餐价格是多少？",
        "我调用 API 一直报错失败，怎么办？",
        "LlamaIndex Workflow 怎么用？",
        "我想做一个学习计划。",
    ]
    for question in questions:
        await run_case(question)


if __name__ == "__main__":
    asyncio.run(main())
