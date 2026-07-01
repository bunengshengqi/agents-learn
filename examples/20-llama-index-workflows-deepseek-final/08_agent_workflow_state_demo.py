"""
Day 20 code 08: AgentWorkflow can also keep shared state.

This connects Day 19 AgentWorkflow with Day 20 Context/state.

Run:
python 08_agent_workflow_state_demo.py
"""

import asyncio

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context

from model_config import build_llm


async def add(ctx: Context, a: int, b: int) -> int:
    """Add two integers and count this tool call in workflow state."""
    state = await ctx.store.get("state")
    state["num_fn_calls"] += 1
    await ctx.store.set("state", state)
    return a + b


async def multiply(ctx: Context, a: int, b: int) -> int:
    """Multiply two integers and count this tool call in workflow state."""
    state = await ctx.store.get("state")
    state["num_fn_calls"] += 1
    await ctx.store.set("state", state)
    return a * b


async def main() -> None:
    llm = build_llm(function_calling=False)
    workflow = AgentWorkflow.from_tools_or_functions(
        [add, multiply],
        llm=llm,
        system_prompt=(
            "你是一个计算助手。遇到加法必须调用 add，遇到乘法必须调用 multiply。"
            "回答时用中文，并说明最终数字。"
        ),
        initial_state={"num_fn_calls": 0},
        state_prompt="当前共享状态：{state}\n用户问题：{msg}",
        timeout=120,
        verbose=True,
    )

    ctx = Context(workflow)
    response = await workflow.run(user_msg="请计算 6 乘以 7，然后再加 8。", ctx=ctx)
    state = await ctx.store.get("state")

    print("\nFinal answer:")
    print(response)
    print("\nShared state:")
    print(state)


if __name__ == "__main__":
    asyncio.run(main())
