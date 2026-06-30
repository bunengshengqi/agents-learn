"""
第19天代码 02：Context 记忆演示

默认 agent.run 是无状态的。传入同一个 Context 后，Agent 可以记住之前轮次。

运行：
python 02_context_memory_demo.py
"""

from __future__ import annotations

import asyncio

from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.workflow import Context

from model_config import build_llm


async def main() -> None:
    """演示 Context 如何保存多轮会话状态。"""
    llm = build_llm(function_calling=False)

    agent = AgentWorkflow.from_tools_or_functions(
        [],
        llm=llm,
        system_prompt="你是一个简洁的中文助手。请记住同一 Context 里的用户信息。",
    )

    ctx = Context(agent)

    print("====== 第一轮：写入记忆 ======")
    response1 = await agent.run("我的名字叫 Bob，我正在学习 LlamaIndex Agent。", ctx=ctx)
    print(response1)

    print("\n====== 第二轮：读取记忆 ======")
    response2 = await agent.run("我刚才说我的名字是什么？我在学习什么？", ctx=ctx)
    print(response2)


if __name__ == "__main__":
    asyncio.run(main())
