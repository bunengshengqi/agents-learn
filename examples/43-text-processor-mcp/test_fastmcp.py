"""通过官方 MCP Client 验证本地 FastMCP stdio Server。"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_FILE = Path(__file__).with_name("server.py")


async def main() -> None:
    """验证初始化、能力发现、Tool 调用、Resource 和 Prompt。"""
    parameters = StdioServerParameters(command=sys.executable, args=[str(SERVER_FILE)])

    async with stdio_client(parameters) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            expected = {
                "analyze_text",
                "extract_keywords",
                "check_reading_level",
                "check_writing_basics",
                "summarize_text",
                "reverse_text",
            }
            assert expected == tool_names

            result = await session.call_tool("analyze_text", {"text": "Hello MCP."})
            assert not result.isError
            assert '"total_words": 2' in result.content[0].text

            resources = await session.list_resources()
            assert "text-processor://guide" in {
                str(resource.uri) for resource in resources.resources
            }

            prompts = await session.list_prompts()
            assert "review_text_workflow" in {prompt.name for prompt in prompts.prompts}

    print("✅ Day43 FastMCP stdio 端到端测试通过")


if __name__ == "__main__":
    asyncio.run(main())
