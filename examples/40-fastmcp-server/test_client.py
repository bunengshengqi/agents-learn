"""通过官方 MCP Client 启动并验证 calculator_server.py。"""

from __future__ import annotations

import asyncio
from pathlib import Path
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER_FILE = Path(__file__).with_name("calculator_server.py")


async def main() -> None:
    """完成初始化、发现，并分别调用三种 Server 能力。"""

    server = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_FILE)],
    )

    async with stdio_client(server) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            print("Tools:", tool_names)
            assert {"add", "calculate", "parse_json"}.issubset(tool_names)

            add_result = await session.call_tool("add", {"a": 7, "b": 5})
            print("add(7, 5):", add_result.content)
            assert not add_result.isError

            invalid_add = await session.call_tool("add", {"a": "hello", "b": 5})
            print("invalid add parameters:", invalid_add.content)
            assert invalid_add.isError

            divide_result = await session.call_tool(
                "calculate",
                {"operation": "divide", "a": 10, "b": 0},
            )
            print("divide by zero:", divide_result.content)
            assert not divide_result.isError

            resources = await session.list_resources()
            resource_uris = [str(resource.uri) for resource in resources.resources]
            print("Resources:", resource_uris)
            assert "course://day40/guide" in resource_uris

            guide = await session.read_resource("course://day40/guide")
            print("Guide:", guide.contents[0])

            templates = await session.list_resource_templates()
            template_uris = [template.uriTemplate for template in templates.resourceTemplates]
            print("Resource templates:", template_uris)
            assert "greeting://{name}" in template_uris

            prompts = await session.list_prompts()
            prompt_names = [prompt.name for prompt in prompts.prompts]
            print("Prompts:", prompt_names)
            assert "explain_fastmcp" in prompt_names

            prompt = await session.get_prompt(
                "explain_fastmcp",
                {"topic": "stdio", "level": "beginner"},
            )
            print("Prompt:", prompt.messages[0].content)

    print("Day40 FastMCP smoke test passed.")


if __name__ == "__main__":
    asyncio.run(main())
