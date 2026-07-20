"""Day 41：供代码代理连接的本地 stdio MCP Server。"""

from mcp.server.fastmcp import FastMCP


# Client 会在初始化后看到这个 Server 名称，并发现下面注册的能力。
mcp = FastMCP("day41-learning-assistant")


@mcp.tool()
def add(a: float, b: float) -> float:
    """计算两个数字之和。"""
    return a + b


@mcp.tool()
def make_study_plan(topic: str, days: int = 3) -> list[str]:
    """为一个主题生成简单的分日学习计划。"""
    if days < 1 or days > 14:
        raise ValueError("days 必须在 1 到 14 之间")

    return [f"第 {day} 天：学习并练习 {topic} 的第 {day} 部分" for day in range(1, days + 1)]


@mcp.resource("course://day41/summary")
def day41_summary() -> str:
    """返回第 41 天的课程摘要。"""
    return "MCP Client 负责连接 Server、发现能力、发送调用并把结果交还给 Agent。"


@mcp.prompt()
def explain_for_beginner(concept: str) -> str:
    """生成适合初学者的概念讲解要求。"""
    return f"请用生活类比、一个代码例子和三道自测题讲解：{concept}。"


if __name__ == "__main__":
    # stdio 模式会占用 stdout 传输协议消息，不要在这里普通 print。
    mcp.run(transport="stdio")
