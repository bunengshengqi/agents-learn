"""
06: AgentWorkflow with tools and shared state.

Goal:
- Connect Day19 AgentWorkflow with Day20 Context state.
- Tools update state through ctx.store.

Run:
python 06_agentworkflow_state.py
"""

import argparse
import asyncio

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context

from model_config import build_llm


KNOWLEDGE = {
    "Workflow": "Workflow 是事件驱动的流程编排容器。",
    "Event": "Event 是 Step 之间传递的数据包。",
    "Context": "Context 用来在一次运行中共享状态。",
    "AgentWorkflow": "AgentWorkflow 让多个工具或智能体协作完成任务。",
}


async def add(ctx: Context, a: int, b: int) -> int:
    """Add two integers."""
    state = await ctx.store.get("state")
    state["tool_calls"] += 1
    state["last_tool"] = "add"
    await ctx.store.set("state", state)
    return a + b


async def multiply(ctx: Context, a: int, b: int) -> int:
    """Multiply two integers."""
    state = await ctx.store.get("state")
    state["tool_calls"] += 1
    state["last_tool"] = "multiply"
    await ctx.store.set("state", state)
    return a * b


async def lookup_workflow_term(ctx: Context, term: str) -> str:
    """Look up a short explanation for a LlamaIndex Workflow term."""
    state = await ctx.store.get("state")
    state["tool_calls"] += 1
    state["last_tool"] = "lookup_workflow_term"
    await ctx.store.set("state", state)
    return KNOWLEDGE.get(term, f"没有找到 {term}，请换成 Workflow、Event、Context 或 AgentWorkflow。")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--question",
        default="请先计算 8 乘以 7，再解释 Context 是什么。",
    )
    args = parser.parse_args()

    llm = build_llm(function_calling=False)
    workflow = AgentWorkflow.from_tools_or_functions(
        [add, multiply, lookup_workflow_term],
        llm=llm,
        system_prompt=(
            "你是 Day20 LlamaIndex Workflow 练习助手。"
            "遇到加法必须调用 add，遇到乘法必须调用 multiply，"
            "遇到 Workflow 概念解释必须调用 lookup_workflow_term。"
            "最终用中文简洁回答。"
        ),
        initial_state={"tool_calls": 0, "last_tool": None},
        state_prompt="当前共享状态：{state}\n用户问题：{msg}",
        timeout=120,
        verbose=True,
    )

    ctx = Context(workflow)
    response = await workflow.run(user_msg=args.question, ctx=ctx)
    state = await ctx.store.get("state")

    print("\nFinal answer:")
    print(response)
    print("\nShared state:")
    print(state)


if __name__ == "__main__":
    asyncio.run(main())
