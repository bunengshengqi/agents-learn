"""
Day 3: Fake Weather Agent

这个脚本不调用真实大模型，也不调用真实天气 API。
它的目的只有一个：用最简单的方式看懂 Thought -> Action -> Observation -> Final Answer。
"""


def get_weather(location: str) -> str:
    """假天气工具。真实项目里这里可以换成天气 API。"""
    weather_data = {
        "New York": "多云，15°C，湿度60%",
        "Suzhou": "晴，28°C，湿度55%",
        "Shanghai": "小雨，24°C，湿度80%",
    }

    return weather_data.get(location, f"暂时没有 {location} 的天气数据")


def main() -> None:
    user_question = "今天 New York 天气怎么样？"

    print("User:")
    print(user_question)
    print("-" * 60)

    thought = "用户问的是实时天气，我需要调用 get_weather 工具查询 New York 的天气。"
    print("Thought:")
    print(thought)
    print("-" * 60)

    action = {
        "action": "get_weather",
        "action_input": {
            "location": "New York",
        },
    }
    print("Action:")
    print(action)
    print("-" * 60)

    location = action["action_input"]["location"]
    observation = get_weather(location)
    print("Observation:")
    print(observation)
    print("-" * 60)

    updated_thought = "我已经拿到天气工具返回的结果，现在可以整理成用户能看懂的最终答案。"
    print("Updated Thought:")
    print(updated_thought)
    print("-" * 60)

    final_answer = f"{location} 当前天气：{observation}。"
    print("Final Answer:")
    print(final_answer)


if __name__ == "__main__":
    main()


