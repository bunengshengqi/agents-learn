"""验证已运行的 Gradio Streamable HTTP MCP endpoint。"""

from __future__ import annotations

import argparse
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def verify(url: str) -> None:
    """连接远程 endpoint，检查六个 Tool 并执行一次调用。"""
    async with streamable_http_client(url) as (read_stream, write_stream, _):
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
            assert expected == tool_names, tool_names

            result = await session.call_tool(
                "extract_keywords",
                {"text": "agent agent mcp tools tools tools", "count": 2},
            )
            assert not result.isError
            assert '"word": "tools"' in result.content[0].text

            print("Tools:", sorted(tool_names))
            print("✅ Day43 Gradio MCP 端到端测试通过")


def main() -> None:
    """读取可选 endpoint 参数并执行异步测试。"""
    parser = argparse.ArgumentParser(description="验证 Day43 Gradio MCP endpoint")
    parser.add_argument(
        "url",
        nargs="?",
        default="http://127.0.0.1:7860/gradio_api/mcp/",
    )
    args = parser.parse_args()
    asyncio.run(verify(args.url))


if __name__ == "__main__":
    main()
