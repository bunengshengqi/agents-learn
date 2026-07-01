"""
Day 20 code 05: share state across steps with Context.

Run:
python 05_context_state_workflow.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.workflow import Context, Event, StartEvent, StopEvent, Workflow, step


class QueryReadyEvent(Event):
    query: str


class ToolDecisionEvent(Event):
    query: str
    tool_name: str


async def add_trace(ctx: Context, text: str) -> None:
    trace = await ctx.store.get("trace", default=[])
    trace.append(text)
    await ctx.store.set("trace", trace)


class ContextStateWorkflow(Workflow):
    """Use ctx.store to remember values that multiple steps need."""

    @step
    async def receive(self, ctx: Context, ev: StartEvent) -> QueryReadyEvent:
        query = ev.get("query", "")
        await ctx.store.set("original_query", query)
        await ctx.store.set("retry_count", 0)
        await add_trace(ctx, "receive: 保存 original_query 和 retry_count")
        return QueryReadyEvent(query=query.strip())

    @step
    async def decide_tool(self, ctx: Context, ev: QueryReadyEvent) -> ToolDecisionEvent:
        if "知识库" in ev.query or "文档" in ev.query:
            tool_name = "query_engine"
        else:
            tool_name = "direct_llm"

        await ctx.store.set("selected_tool", tool_name)
        await add_trace(ctx, f"decide_tool: 选择 {tool_name}")
        return ToolDecisionEvent(query=ev.query, tool_name=tool_name)

    @step
    async def finish(self, ctx: Context, ev: ToolDecisionEvent) -> StopEvent:
        original_query = await ctx.store.get("original_query")
        selected_tool = await ctx.store.get("selected_tool")
        retry_count = await ctx.store.get("retry_count")
        trace = await ctx.store.get("trace")

        return StopEvent(
            result={
                "original_query": original_query,
                "selected_tool": selected_tool,
                "retry_count": retry_count,
                "trace": trace,
                "answer": f"当前问题会交给 {ev.tool_name} 处理：{ev.query}",
            }
        )


async def main() -> None:
    workflow = ContextStateWorkflow(timeout=10, verbose=True)
    result = await workflow.run(query="请根据知识库解释 Workflow 的状态管理")
    print("\nFinal result:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
