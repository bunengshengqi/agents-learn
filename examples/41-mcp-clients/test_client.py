"""用官方 MCP Client 完成真实的 stdio 连接、发现和调用测试。"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_FILE = Path(__file__).with_name("local_server.py")


async def main() -> None:
    """启动 Server，并验证 Tool、Resource 与 Prompt。"""
    server = StdioServerParameters(command=sys.executable, args=[str(SERVER_FILE)])

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            assert {"add", "make_study_plan"}.issubset(tool_names)

            add_result = await session.call_tool("add", {"a": 18, "b": 24})
            assert not add_result.isError
            assert add_result.structuredContent == {"result": 42.0}

            plan_result = await session.call_tool(
                "make_study_plan",
                {"topic": "MCP Client", "days": 3},
            )
            assert not plan_result.isError
            assert len(plan_result.structuredContent["result"]) == 3

            resources = await session.list_resources()
            resource_uris = {str(resource.uri) for resource in resources.resources}
            assert "course://day41/summary" in resource_uris

            prompts = await session.list_prompts()
            prompt_names = {prompt.name for prompt in prompts.prompts}
            assert "explain_for_beginner" in prompt_names

    print("✅ Day41 MCP Client 连接、发现与调用测试通过")


if __name__ == "__main__":
    asyncio.run(main())
