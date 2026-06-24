"""
Day12: first_agent.py

这是第 12 天的真实 Agent 练习代码。

今天重点不是比较 CodeAgent 和 ToolCallingAgent，而是学习：
1. 工具接口描述为什么重要。
2. 如何用 @tool 创建简单工具。
3. 如何用 Tool 类创建复杂工具。
4. Agent 如何根据工具说明自动选择工具。

运行：

python first_agent.py
"""

from __future__ import annotations  # 允许类型注解延迟解析，保持代码兼容。

from smolagents import CodeAgent  # 导入 CodeAgent，用它来运行 Day12 的工具练习。

from model_config import build_model  # 导入模型构建函数，负责读取 .env 并创建模型对象。
from tools import get_all_tools, get_class_tools, get_decorator_tools  # 导入三组工具菜单。


def build_decorator_tool_agent() -> CodeAgent:
    """
    创建只使用 @tool 函数工具的 Agent。

    这个 Agent 用来观察：函数名、类型注解、docstring 如何变成工具说明书。
    """
    return CodeAgent(  # 创建并返回一个 CodeAgent 实例。
        tools=get_decorator_tools(),  # 只给 Agent 提供 @tool 装饰器创建的函数工具。
        model=build_model(),  # 给 Agent 绑定真实模型。
        max_steps=6,  # 限制最多执行 6 个步骤，防止任务无限循环。
        additional_authorized_imports=["math"],  # 允许 Agent 生成的代码导入 math 标准库。
    )  # CodeAgent 创建结束。


def build_class_tool_agent() -> CodeAgent:
    """
    创建只使用 Tool 类工具的 Agent。

    这个 Agent 用来观察：类工具如何通过 name、description、inputs、
    output_type 和 forward 明确描述工具能力。
    """
    return CodeAgent(  # 创建并返回一个 CodeAgent 实例。
        tools=get_class_tools(),  # 只给 Agent 提供继承 Tool 类创建的工具。
        model=build_model(),  # 给 Agent 绑定真实模型。
        max_steps=6,  # 限制最多执行 6 个步骤。
    )  # CodeAgent 创建结束。


def build_full_agent() -> CodeAgent:
    """
    创建包含 Day12 全部自定义工具的 Agent。
    """
    return CodeAgent(  # 创建并返回包含全部工具的 CodeAgent。
        tools=get_all_tools(),  # 提供 Day12 的全部自定义工具。
        model=build_model(),  # 给 Agent 绑定真实模型。
        max_steps=8,  # 完整工具菜单任务稍复杂，所以给 8 个步骤。
        additional_authorized_imports=["math"],  # 允许 Agent 生成的代码导入 math 标准库。
    )  # CodeAgent 创建结束。


def run_decorator_tool_demo(agent: CodeAgent) -> None:
    """
    练习 1：使用 @tool 函数工具。
    """
    # 定义要交给 Agent 的自然语言任务。
    task = """
我想比较海底捞和轻食实验室哪家更适合作为团队午餐。
请你：
1. 查询两家餐厅评分。
2. 假设海底捞人均 120 元，轻食实验室人均 45 元。
3. 分别计算服务性价比分数。
4. 用中文给出简洁建议。
"""

    print("=" * 80)  # 打印分隔线。
    print("练习 1：@tool 函数工具")  # 打印当前练习标题。
    print("=" * 80)  # 再打印一条分隔线。

    answer = agent.run(task)  # 把自然语言任务交给 Agent，让它自行选择并调用工具。

    print("\nFinal Answer:")  # 打印最终答案标题。
    print(answer)  # 打印 Agent 返回的最终答案。


def run_class_tool_demo(agent: CodeAgent) -> None:
    """
    练习 2：使用 Tool 类工具。
    """
    # 定义要交给类工具 Agent 的自然语言任务。
    task = """
请做两件事：
1. 为 villain masquerade 生成一个中文派对主题。
2. 帮我把商品 iPad Air、卖点“几乎全新，配件齐全”、目标人群“学生”生成一个二手平台标题。
最后用中文分点输出。
"""

    print("\n" + "=" * 80)  # 换行后打印分隔线，让两个练习隔开。
    print("练习 2：Tool 类工具")  # 打印当前练习标题。
    print("=" * 80)  # 再打印一条分隔线。

    answer = agent.run(task)  # 运行任务，观察 Agent 如何调用类工具。

    print("\nFinal Answer:")  # 打印最终答案标题。
    print(answer)  # 打印 Agent 返回的最终答案。


def run_full_toolbox_demo(agent: CodeAgent) -> None:
    """
    练习 3：让 Agent 在全部工具里自行选择。
    """
    # 定义完整工具菜单练习任务。
    task = """
请完成一个小型运营检查：
1. 检查文案“全网最低价，稳赚不亏，学生党必入”的风险。
2. 查询星巴克评分。
3. 生成一个 classic heroes 类型的派对主题。
最后用中文说明你分别使用了哪些工具。
"""

    print("\n" + "=" * 80)  # 换行后打印分隔线。
    print("练习 3：完整工具菜单")  # 打印当前练习标题。
    print("=" * 80)  # 再打印一条分隔线。

    answer = agent.run(task)  # 运行任务，让 Agent 在全部工具中自行选择。

    print("\nFinal Answer:")  # 打印最终答案标题。
    print(answer)  # 打印 Agent 返回的最终答案。


def main() -> None:
    decorator_agent = build_decorator_tool_agent()  # 创建只包含 @tool 函数工具的 Agent。
    run_decorator_tool_demo(decorator_agent)  # 运行 @tool 函数工具练习。

    class_agent = build_class_tool_agent()  # 创建只包含 Tool 类工具的 Agent。
    run_class_tool_demo(class_agent)  # 运行 Tool 类工具练习。

    full_agent = build_full_agent()  # 创建包含全部自定义工具的 Agent。
    run_full_toolbox_demo(full_agent)  # 运行完整工具菜单练习。


if __name__ == "__main__":  # 只有直接运行 python first_agent.py 时，才会进入这里。
    main()  # 启动 Day12 的三个 Agent 练习。
