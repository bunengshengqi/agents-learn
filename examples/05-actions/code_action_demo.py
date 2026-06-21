def get_weather(city: str) -> str:
    weather_data = {
        "苏州": "晴，28°C，湿度55%",
        "上海": "小雨，24°C，湿度80%",
        "北京": "晴，22°C，湿度40%",
        "New York": "多云，15°C，湿度60%",
    }

    return weather_data.get(city, f"暂时没有 {city} 的天气数据")


def safe_execute(code: str) -> None:
    allowed_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "len": len,
            "min": min,
            "max": max,
            "sum": sum,
        },
        "get_weather": get_weather,
    }

    allowed_locals = {}

    exec(code, allowed_globals, allowed_locals)


def main() -> None:
    print("Day 5: Code Action Demo")
    print("这个脚本模拟 Code Agent：模型输出一段 Python 代码，由程序执行。")
    print("-" * 60)

    code_action = """
cities = ["苏州", "上海", "北京"]

for city in cities:
    weather = get_weather(city)
    print(f"{city} 当前天气：{weather}")
"""

    print("Code Action：")
    print(code_action)
    print("-" * 60)

    print("执行结果：")
    safe_execute(code_action)


if __name__ == "__main__":
    main()
