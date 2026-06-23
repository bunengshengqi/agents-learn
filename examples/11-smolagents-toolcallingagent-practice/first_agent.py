"""
Day11: first_agent.py

这是第 11 天的 ToolCallingAgent 练习代码，对应 Hugging Face Agents Course：
“ToolCallingAgent 与 JSON 工具调用”。

你会练习：
1. 创建 ToolCallingAgent。
2. 给 ToolCallingAgent 准备 JSON 工具调用需要的工具菜单。
3. 使用 agent.run() 运行简单工具调用任务。
4. 观察复杂循环任务为什么通常更适合 CodeAgent。

运行：

python first_agent.py
"""

from __future__ import annotations

from smolagents import ToolCallingAgent

from model_config import build_model
from tools import get_all_tools, get_simple_tools


def build_simple_agent() -> ToolCallingAgent:
    """
    创建适合简单工具调用任务的 ToolCallingAgent。

    ToolCallingAgent 会让模型生成结构化工具调用数据。
    框架随后解析工具名称和参数，并调用工具列表里对应的 Python 函数。
    """
    return ToolCallingAgent(
        tools=get_simple_tools(),
        model=build_model(),
        max_steps=8,
    )


def build_full_agent() -> ToolCallingAgent:
    """
    创建带有 Day11 全部工具的 ToolCallingAgent。

    这个版本可以运行手机价格比较任务，但可能需要更多 Action 轮次。
    因为 JSON 工具调用不擅长自然表达循环和变量保存。
    """
    return ToolCallingAgent(
        tools=get_all_tools(),
        model=build_model(),
        max_steps=24,
    )


def run_weather_demo(agent: ToolCallingAgent) -> None:
    """
    练习 1：一次明确的工具调用。

    预期 Action 形式：
    {"name": "get_weather", "arguments": {"city": "苏州"}}
    """
    task = """
请查询苏州今天的天气。
请优先使用工具，不要凭空猜测。
最后用中文一句话回答。
"""

    print("=" * 80)
    print("练习 1：简单天气查询 ToolCallingAgent")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def run_food_demo(agent: ToolCallingAgent) -> None:
    """
    练习 2：多个简单工具调用。

    这个任务仍然适合 ToolCallingAgent，因为每一步都很清楚：
    查看菜单、推荐菜品、查询天气、计算折扣。
    """
    task = """
我今天在苏州，想吃减脂一点的午饭。
请你：
1. 查看今日菜单。
2. 推荐一个适合我的菜。
3. 查询苏州天气。
4. 如果推荐菜品打 9 折，帮我算出最终价格。
5. 最后用中文给我一个简洁建议。
"""

    print("\n" + "=" * 80)
    print("练习 2：点菜推荐 ToolCallingAgent")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def run_phone_price_demo(agent: ToolCallingAgent) -> None:
    """
    练习 3：展示 ToolCallingAgent 局限的任务。

    它可以通过足够多的工具调用解决这个任务，但 Day10 的 CodeAgent 更合适。
    因为这个任务天然需要循环、变量和 min() 这样的比较逻辑。
    """
    task = """
请判断在哪个国家购买 CodeAct 1 手机最划算。
候选国家包括：USA、Japan、Germany、India。

你可以使用工具：
- lookup_rates(country)
- lookup_phone_price(model, country)
- convert_and_tax(price, exchange_rate, tax_rate)
- estimate_shipping(country)
- estimate_final_price(converted_price, shipping_cost)

请分别计算每个国家的最终价格，并说明最划算的国家。
"""

    print("\n" + "=" * 80)
    print("练习 3：手机价格比较 ToolCallingAgent")
    print("=" * 80)
    print("提示：这个任务能跑，但更适合 Day10 的 CodeAgent。")

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def main() -> None:
    simple_agent = build_simple_agent()

    run_weather_demo(simple_agent)
    run_food_demo(simple_agent)

    full_agent = build_full_agent()
    run_phone_price_demo(full_agent)


if __name__ == "__main__":
    main()
