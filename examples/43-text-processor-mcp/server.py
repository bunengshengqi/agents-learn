"""Part 1：使用 FastMCP 暴露本地 stdio MCP Server。"""

from mcp.server.fastmcp import FastMCP

import text_tools


mcp = FastMCP("day43-text-processor")


# 包一层 MCP Tool 的好处是：业务函数仍然保持与框架无关。
mcp.tool()(text_tools.analyze_text)
mcp.tool()(text_tools.extract_keywords)
mcp.tool()(text_tools.check_reading_level)
mcp.tool()(text_tools.check_writing_basics)
mcp.tool()(text_tools.summarize_text)
mcp.tool()(text_tools.reverse_text)


@mcp.resource("text-processor://guide")
def usage_guide() -> str:
    """返回 Day43 文本处理工具的能力、限制和使用顺序。"""
    return """# Day43 Text Processor

1. Use `analyze_text` for deterministic statistics.
2. Use `extract_keywords` only for English keywords.
3. Treat `check_reading_level` as a rough English heuristic.
4. `check_writing_basics` is not a full spelling or grammar checker.
5. `summarize_text` selects leading sentences and does not call an LLM.
"""


@mcp.prompt()
def review_text_workflow(goal: str = "improve clarity") -> str:
    """生成一个让 Agent 组合多个文本工具的标准工作流。"""
    return (
        f"Review the supplied text with the goal: {goal}. "
        "First analyze statistics, then check reading level and writing basics. "
        "Explain tool limitations and give prioritized edits."
    )


if __name__ == "__main__":
    # stdio 的 stdout 用于 MCP 消息，不要在 Server 中随意 print。
    mcp.run(transport="stdio")
