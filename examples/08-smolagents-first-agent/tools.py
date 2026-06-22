"""
Day 8: Tools for smolagents

工具是 Agent 的能力来源。
smolagents 会读取函数名、类型标注和 docstring，帮助模型理解什么时候调用工具。
"""

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from smolagents import tool


@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Get the current local time in a specified timezone.

    Args:
        timezone: A valid timezone name, such as 'Asia/Shanghai' or 'America/New_York'.
    """
    try:
        now = datetime.now(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        return f"无效时区：{timezone}。示例：Asia/Shanghai、America/New_York"

    return now.strftime("%Y-%m-%d %H:%M:%S %Z")


@tool
def multiply_numbers(a: int, b: int) -> str:
    """Multiply two integers and return the result.

    Args:
        a: The first integer.
        b: The second integer.
    """
    return str(a * b)
