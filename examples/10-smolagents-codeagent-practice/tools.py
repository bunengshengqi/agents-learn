"""
Day10: tools.py

这个文件是给 CodeAgent 准备的“工具菜单”。

Agent 不能凭空调用工具。
你在这里定义并注册什么工具，Agent 才能使用什么工具。
"""

from __future__ import annotations

from smolagents import tool


@tool
def get_menu() -> str:
    """
    获取今日菜单。
    """
    return """
今日菜单：
1. 红烧牛肉饭 28元
2. 番茄鸡蛋面 18元
3. 黑椒鸡胸沙拉 22元
4. 酸菜鱼套餐 36元
"""


@tool
def recommend_food(preference: str) -> str:
    """
    根据用户偏好推荐菜品。

    Args:
        preference: 用户偏好，比如“减脂”“重口味”“便宜”“清淡”
    """
    if "减脂" in preference:
        return "推荐黑椒鸡胸沙拉，价格 22 元，适合减脂。"

    if "重口味" in preference:
        return "推荐酸菜鱼套餐，价格 36 元，口味比较重。"

    if "便宜" in preference or "省钱" in preference:
        return "推荐番茄鸡蛋面，价格 18 元，最省钱。"

    if "清淡" in preference:
        return "推荐番茄鸡蛋面，价格 18 元，相对清淡。"

    return "推荐红烧牛肉饭，价格 28 元，比较稳。"


@tool
def calculate_discount_price(price: float, discount: float) -> float:
    """
    计算折扣后的价格。

    Args:
        price: 商品原价
        discount: 折扣，比如 0.9 表示九折
    """
    return round(price * discount, 2)


@tool
def get_weather(city: str) -> str:
    """
    查询城市天气。

    Args:
        city: 城市名称
    """
    weather_data = {
        "苏州": "晴，28度，湿度55%",
        "上海": "小雨，24度，湿度80%",
        "北京": "晴，22度，湿度40%",
    }
    return weather_data.get(city, f"暂时没有 {city} 的天气数据")


@tool
def lookup_rates(country: str) -> tuple[float, float]:
    """
    查询国家对应的汇率和税率。

    Args:
        country: 国家名称，比如 USA、Japan、Germany、India
    """
    rates = {
        "USA": (1.0, 0.08),
        "Japan": (0.0064, 0.10),
        "Germany": (1.08, 0.19),
        "India": (0.012, 0.18),
    }
    return rates.get(country, (1.0, 0.0))


@tool
def lookup_phone_price(model: str, country: str) -> float:
    """
    查询某款手机在某个国家的本地价格。

    Args:
        model: 手机型号
        country: 国家名称，比如 USA、Japan、Germany、India
    """
    prices = {
        "USA": 799.0,
        "Japan": 118000.0,
        "Germany": 760.0,
        "India": 69999.0,
    }
    return prices.get(country, 999999.0)


@tool
def convert_and_tax(price: float, exchange_rate: float, tax_rate: float) -> float:
    """
    将本地价格换算成美元，并加上税费。

    Args:
        price: 本地价格
        exchange_rate: 汇率
        tax_rate: 税率
    """
    return round(price * exchange_rate * (1 + tax_rate), 2)


@tool
def estimate_shipping(country: str) -> float:
    """
    估算从某个国家购买商品的运费，单位为美元。

    Args:
        country: 国家名称，比如 USA、Japan、Germany、India
    """
    shipping = {
        "USA": 30.0,
        "Japan": 25.0,
        "Germany": 40.0,
        "India": 35.0,
    }
    return shipping.get(country, 50.0)


@tool
def estimate_final_price(converted_price: float, shipping_cost: float) -> float:
    """
    计算最终价格。

    Args:
        converted_price: 换算并加税后的价格
        shipping_cost: 运费
    """
    return round(converted_price + shipping_cost, 2)


def get_all_tools() -> list:
    """
    统一返回所有工具。

    first_agent.py 只需要导入这个函数，就可以拿到工具菜单。
    """
    return [
        get_menu,
        recommend_food,
        calculate_discount_price,
        get_weather,
        lookup_rates,
        lookup_phone_price,
        convert_and_tax,
        estimate_shipping,
        estimate_final_price,
    ]


