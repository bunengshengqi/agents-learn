"""
Day12: default_toolbox_notes.py

这个脚本只展示 smolagents 默认工具箱里常见工具的名字和用途。
默认搜索、网页访问、Hub 工具可能需要额外依赖或网络环境，所以这里不直接调用它们。

运行：

python default_toolbox_notes.py
"""

from __future__ import annotations  # 允许类型注解延迟解析，保持代码风格统一。


def main() -> None:
    default_tools = [  # 用列表保存默认工具名称和用途说明。
        ("PythonInterpreterTool", "让 CodeAgent 执行 Python 代码，适合计算和数据处理。"),  # Python 执行工具。
        ("FinalAnswerTool", "让 Agent 输出最终答案，通常表示任务结束。"),  # 最终答案工具。
        ("UserInputTool", "当信息不足时，让 Agent 向用户请求补充输入。"),  # 用户输入工具。
        ("DuckDuckGoSearchTool", "通过 DuckDuckGo 搜索公开网页信息。"),  # DuckDuckGo 搜索工具。
        ("GoogleSearchTool", "通过 Google Search API 搜索信息，通常需要额外配置。"),  # Google 搜索工具。
        ("VisitWebpageTool", "访问网页并读取网页内容。"),  # 网页访问工具。
    ]  # 默认工具列表结束。

    print("=" * 80)  # 打印分隔线。
    print("Day12：smolagents 默认工具箱")  # 打印标题。
    print("=" * 80)  # 打印分隔线。

    for name, description in default_tools:  # 遍历默认工具说明。
        print(f"- {name}: {description}")  # 打印工具名称和用途。

    print("\n工具生态还包括：")  # 打印工具生态小标题。
    print("- tool.push_to_hub(...): 把自定义工具上传到 Hugging Face Hub。")  # 说明如何共享工具。
    print("- load_tool(..., trust_remote_code=True): 从 Hub 加载社区工具。")  # 说明如何加载 Hub 工具。
    print("- Tool.from_space(...): 把 Hugging Face Space 包装成工具。")  # 说明如何复用 Space。
    print("- Tool.from_langchain(...): 复用 LangChain 生态中的工具。")  # 说明如何复用 LangChain 工具。
    print("\n注意：trust_remote_code=True 表示允许执行远程代码，只能用于可信来源。")  # 提醒远程代码风险。


if __name__ == "__main__":  # 只有直接运行这个文件时，才执行 main。
    main()  # 启动默认工具箱说明流程。
