"""连接已运行的 Gradio MCP endpoint，验证发现和调用能力。"""

from __future__ import annotations

import argparse
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def verify(url: str) -> None:
    """通过 Streamable HTTP 验证 Tools、Resource、Prompt 和 Tool 调用。"""
    async with streamable_http_client(url) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            expected_tools = {
                "analyze_text",
                "reverse_text",
                "count_vowels",
                "extract_keywords",
            }
            assert expected_tools.issubset(tool_names), tool_names

            result = await session.call_tool("analyze_text", {"text": "Hello MCP"})
            assert not result.isError
            assert '"words": 2' in result.content[0].text

            resources = await session.list_resources()
            resource_uris = {str(resource.uri) for resource in resources.resources}
            assert "course://day42/guide" in resource_uris

            prompts = await session.list_prompts()
            prompt_names = {prompt.name for prompt in prompts.prompts}
            assert "explain_text_analysis" in prompt_names

            print("Tools:", sorted(tool_names))
            print("Resources:", sorted(resource_uris))
            print("Prompts:", sorted(prompt_names))
            print("✅ Day42 Gradio MCP 端到端测试通过")


def main() -> None:
    """读取 endpoint 参数并运行异步验证。"""
    parser = argparse.ArgumentParser(description="验证 Gradio MCP endpoint")
    parser.add_argument(
        "url",
        nargs="?",
        default="http://127.0.0.1:7860/gradio_api/mcp/",
        help="Gradio 的 Streamable HTTP MCP endpoint",
    )
    args = parser.parse_args()
    asyncio.run(verify(args.url))


if __name__ == "__main__":
    main()
