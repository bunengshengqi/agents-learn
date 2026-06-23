"""
Day11: action_format_demo.py

这个文件不调用真实大模型，只打印课程里的两种 Action 表达方式：

1. CodeAgent 的 Action：Python 代码。
2. ToolCallingAgent 的 Action：JSON 风格的工具调用结构。

运行：

python action_format_demo.py
"""

from __future__ import annotations

import json
import textwrap


def show_search_action_styles() -> None:
    """
    展示同一个搜索任务如何分别用代码和 JSON 表达。
    """
    code_action = """
for query in [
    "Best catering services in Gotham City",
    "Party theme ideas for superheroes",
]:
    print(web_search(f"Search for: {query}"))
"""

    json_action = [
        {
            "name": "web_search",
            "arguments": {"query": "Best catering services in Gotham City"},
        },
        {
            "name": "web_search",
            "arguments": {"query": "Party theme ideas for superheroes"},
        },
    ]

    print("=" * 80)
    print("CodeAgent 的 Action：Python 代码")
    print("=" * 80)
    print(textwrap.dedent(code_action).strip())

    print("\n" + "=" * 80)
    print("ToolCallingAgent 的 Action：JSON 工具调用")
    print("=" * 80)
    print(json.dumps(json_action, ensure_ascii=False, indent=2))


def show_phone_price_code_action() -> None:
    """
    展示为什么代码 Action 更适合循环和数据流处理。
    """
    code_action = """
countries = ["USA", "Japan", "Germany", "India"]
final_prices = {}

for country in countries:
    exchange_rate, tax_rate = lookup_rates(country)
    local_price = lookup_phone_price("CodeAct 1", country)
    converted_price = convert_and_tax(local_price, exchange_rate, tax_rate)
    shipping_cost = estimate_shipping(country)
    final_price = estimate_final_price(converted_price, shipping_cost)
    final_prices[country] = final_price

most_cost_effective_country = min(final_prices, key=final_prices.get)
print(most_cost_effective_country, final_prices[most_cost_effective_country])
"""

    print("\n" + "=" * 80)
    print("复杂任务：CodeAgent 可以保存变量、循环和比较")
    print("=" * 80)
    print(textwrap.dedent(code_action).strip())


def show_phone_price_json_actions() -> None:
    """
    展示 JSON Action 在多国家价格比较任务中为什么会变得重复。
    """
    json_actions = [
        {"name": "lookup_rates", "arguments": {"country": "Germany"}},
        {
            "name": "lookup_phone_price",
            "arguments": {"model": "CodeAct 1", "country": "Germany"},
        },
        {
            "name": "convert_and_tax",
            "arguments": {"price": 760.0, "exchange_rate": 1.08, "tax_rate": 0.19},
        },
        {"name": "estimate_shipping", "arguments": {"country": "Germany"}},
        {
            "name": "estimate_final_price",
            "arguments": {"converted_price": 976.75, "shipping_cost": 40.0},
        },
    ]

    print("\n" + "=" * 80)
    print("复杂任务：ToolCallingAgent 需要多次 JSON 工具调用")
    print("=" * 80)
    print(json.dumps(json_actions, ensure_ascii=False, indent=2))
    print("\n同样的步骤还要对 USA、Japan、India 再重复。")


def main() -> None:
    show_search_action_styles()
    show_phone_price_code_action()
    show_phone_price_json_actions()


if __name__ == "__main__":
    main()
