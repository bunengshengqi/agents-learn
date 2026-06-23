"""
Day10: first_agent.py

这是第 10 天的真实 API 练习代码。

你会练习：
1. 创建 CodeAgent。
2. 给 CodeAgent 准备 tools 工具菜单。
3. 使用 agent.run() 运行智能体。
4. 观察 CodeAgent 如何自己写 Python 代码调用工具。

运行：

python first_agent.py
"""

from __future__ import annotations

from smolagents import CodeAgent

from model_config import build_model
from tools import get_all_tools


def build_agent() -> CodeAgent:
    """
    创建 CodeAgent。

    这里的 tools 就是给 Agent 准备的工具菜单。
    """
    model = build_model()
    tools = get_all_tools()

    agent = CodeAgent(
        tools=tools,
        model=model,
        additional_authorized_imports=["math", "statistics", "datetime"],
    )

    return agent


def run_food_demo(agent: CodeAgent) -> None:
    """
    练习 1：点菜推荐 Agent。

    这个练习对应：
    - 自定义工具准备菜单
    - CodeAgent 调用工具
    - agent.run() 的使用
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

    print("=" * 80)
    print("练习 1：点菜推荐 Agent")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def run_phone_price_demo(agent: CodeAgent) -> None:
    """
    练习 2：手机购买国家价格比较。

    这个练习对应课程图片里的例子：
    用 CodeAgent 一次性处理多个国家的价格、汇率、税费、运费，并找出最便宜的国家。
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

请你用 Python 代码循环计算每个国家的最终价格，
最后告诉我每个国家的价格明细，以及最划算的国家。
"""

    print("\n" + "=" * 80)
    print("练习 2：手机价格比较 CodeAgent")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def main() -> None:
    agent = build_agent()

    run_food_demo(agent)
    run_phone_price_demo(agent)


if __name__ == "__main__":
    main()

