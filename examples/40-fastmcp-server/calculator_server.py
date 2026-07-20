"""Day40：适合初学者阅读的 FastMCP Server。

这个 Server 同时公开：
1. Tools：执行计算和 JSON 解析；
2. Resources：提供只读学习资料；
3. Prompts：生成可复用的学习提示模板。

直接运行时使用 stdio Transport。请勿向 stdout 打印普通日志，
否则会污染 MCP 的 JSON-RPC 消息；日志应写入 stderr。
"""

from __future__ import annotations

import json
from typing import Literal

from mcp.server.fastmcp import FastMCP


# FastMCP 会读取函数签名、类型注解和 docstring，自动生成 MCP Schema。
mcp = FastMCP(
    "day40-fastmcp-demo",
    instructions="A beginner-friendly server for learning tools, resources, and prompts.",
    json_response=True,
)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """

    return a + b


@mcp.tool()
def calculate(
    operation: Literal["add", "subtract", "multiply", "divide"],
    a: float,
    b: float,
) -> dict[str, bool | float | str]:
    """Calculate two numbers with an explicitly selected operation.

    Args:
        operation: One of add, subtract, multiply, or divide.
        a: The first number.
        b: The second number.

    Returns:
        A structured success result, or a structured error for division by zero.
    """

    if operation == "add":
        value = a + b
    elif operation == "subtract":
        value = a - b
    elif operation == "multiply":
        value = a * b
    elif b == 0:
        return {"ok": False, "error": "denominator must not be zero"}
    else:
        value = a / b

    return {"ok": True, "operation": operation, "result": value}


@mcp.tool()
def parse_json(data: str) -> dict[str, bool | str | object]:
    """Parse a JSON string without crashing the MCP Server.

    Args:
        data: A JSON document represented as text.
    """

    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "error": "invalid JSON",
            "detail": f"line {exc.lineno}, column {exc.colno}: {exc.msg}",
        }

    return {"ok": True, "value": parsed}


@mcp.resource("course://day40/guide")
def day40_guide() -> str:
    """Return the read-only Day40 learning guide."""

    return (
        "FastMCP beginner path:\n"
        "1. Install mcp[cli].\n"
        "2. Create FastMCP(name).\n"
        "3. Add @mcp.tool, @mcp.resource, and @mcp.prompt.\n"
        "4. Test with an MCP Client or Inspector.\n"
        "5. Run with stdio or Streamable HTTP."
    )


@mcp.resource("greeting://{name}")
def greeting(name: str) -> str:
    """Return a templated greeting resource for one name."""

    cleaned_name = name.strip() or "learner"
    return f"Hello, {cleaned_name}! Welcome to FastMCP Day40."


@mcp.prompt()
def explain_fastmcp(
    topic: str = "FastMCP",
    level: Literal["beginner", "intermediate"] = "beginner",
) -> str:
    """Create a reusable prompt for explaining one FastMCP topic.

    Args:
        topic: The MCP topic that should be explained.
        level: The learner's current level.
    """

    if level == "beginner":
        requirements = "Use plain Chinese, one analogy, and one tiny Python example."
    else:
        requirements = "Explain protocol boundaries, trade-offs, and production concerns."

    return f"Explain {topic} to a {level} learner. {requirements}"


if __name__ == "__main__":
    # stdio 是本地 MCP Server 最简单的启动方式。
    mcp.run(transport="stdio")
