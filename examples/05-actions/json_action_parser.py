import json


def get_weather(city: str) -> str:
    weather_data = {
        "苏州": "晴，28°C，湿度55%",
        "上海": "小雨，24°C，湿度80%",
        "北京": "晴，22°C，湿度40%",
        "New York": "多云，15°C，湿度60%",
    }

    return weather_data.get(city, f"暂时没有 {city} 的天气数据")


def calculator(a: int, b: int) -> int:
    return a * b


def parse_action(action_text: str) -> dict | None:
    try:
        action = json.loads(action_text)
    except json.JSONDecodeError:
        return None

    if "action" not in action or "action_input" not in action:
        return None

    return action


def run_tool(action: dict) -> str:
    tool_name = action["action"]
    tool_input = action["action_input"]

    if tool_name == "get_weather":
        return get_weather(tool_input["city"])

    if tool_name == "calculator":
        result = calculator(
            int(tool_input["a"]),
            int(tool_input["b"]),
        )
        return str(result)

    return f"未知工具：{tool_name}"


def main() -> None:
    print("Day 5: JSON Action Parser")
    print("请输入 JSON Action，例如：")
    print(
        """
{
  "action": "calculator",
  "action_input": {
    "a": 3,
    "b": 4
  }
}
"""
    )
    print("输入 END 结束。")
    print("-" * 60)

    lines = []

    while True:
        line = input()
        if line.strip() == "END":
            break
        lines.append(line)

    action_text = "\n".join(lines)
    action = parse_action(action_text)

    if action is None:
        print("Action 解析失败，请检查 JSON 格式。")
        return

    print("\nParse 成功：")
    print(action)
    print("-" * 60)

    observation = run_tool(action)

    print("Observation：")
    print(observation)


if __name__ == "__main__":
    main()
