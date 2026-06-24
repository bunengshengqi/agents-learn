"""
Day12: tool_schema_demo.py

这个脚本不调用真实模型。
它只打印工具的“说明书”，帮助你观察 LLM 到底会看到什么工具信息。

运行：

python tool_schema_demo.py
"""

from __future__ import annotations  # 允许类型注解延迟解析，提升兼容性。

import json  # 用来把工具 schema 格式化打印成 JSON。
from typing import Any  # 用 Any 表示任意 smolagents 工具对象。

from smolagents.models import get_tool_json_schema  # smolagents 内部用于生成工具 JSON schema 的函数。

from tools import get_all_tools  # 导入 Day12 定义的全部自定义工具。


def simplify_schema(tool: Any) -> dict[str, Any]:
    """
    提取最关键的工具接口信息。

    smolagents 会把这些信息放进系统提示或工具 schema 中，让模型知道：
    这个工具叫什么、能做什么、需要哪些参数、返回什么类型。
    """
    schema = get_tool_json_schema(tool)  # 生成 smolagents 传给模型的完整工具 schema。
    function_schema = schema["function"]  # 取出 OpenAI tool schema 中的 function 部分。
    return {  # 返回一个更适合学习观察的简化字典。
        "name": function_schema["name"],  # 工具名称。
        "description": function_schema["description"],  # 工具描述。
        "parameters": function_schema["parameters"],  # 工具输入参数定义。
    }  # 简化后的工具 schema 结束。


def main() -> None:
    tools = get_all_tools()  # 获取 Day12 的全部工具。

    print("=" * 80)  # 打印分隔线，让输出更清楚。
    print("Day12：工具说明书")  # 打印标题。
    print("=" * 80)  # 再打印一条分隔线。

    for index, tool in enumerate(tools, start=1):  # 遍历每一个工具，并从 1 开始编号。
        print(f"\n工具 {index}: {tool.name}")  # 打印当前工具编号和名称。
        print(json.dumps(simplify_schema(tool), ensure_ascii=False, indent=2))  # 以中文友好的 JSON 格式打印 schema。


if __name__ == "__main__":  # 只有直接运行这个文件时，才执行 main。
    main()  # 启动工具 schema 展示流程。
