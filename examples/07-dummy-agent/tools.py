"""
Day 7: Tools

这个文件专门存放工具函数。

对应知识点：
- Day 5 Action：模型决定要调用哪个工具，以及传什么参数。
- Day 6 Observation：工具执行后的返回值，会变成 Observation。
"""


def calculator(a: int, b: int) -> str:
    """
    计算两个整数相乘。

    对应知识点：
    - 工具本质上就是普通 Python 函数。
    - Agent 不直接“算”，而是生成 Action，程序再调用这个函数。
    """
    return str(a * b)


def get_weather(city: str) -> str:
    """
    模拟天气查询工具。

    对应知识点：
    - 真实项目中这里可以换成天气 API。
    - 当前为了学习 Agent Loop，先用假数据，避免 API 干扰理解。
    """
    weather_data = {
        "苏州": "晴，28°C，湿度55%",
        "上海": "小雨，24°C，湿度80%",
        "北京": "晴，22°C，湿度40%",
        "New York": "多云，15°C，湿度60%",
    }

    return weather_data.get(city, f"暂时没有 {city} 的天气数据")


TOOLS = {
    "calculator": calculator,
    "get_weather": get_weather,
}


TOOL_DESCRIPTIONS = """
你可以使用下面这些工具：

1. calculator
   作用：计算两个整数相乘
   参数：
   - a: int
   - b: int
   返回：字符串形式的计算结果

2. get_weather
   作用：查询城市的模拟天气
   参数：
   - city: str
   返回：天气描述字符串
"""


