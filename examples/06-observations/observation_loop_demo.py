
"""
Day 6: Observation Loop Demo

这个脚本演示：
1. 主工具失败，返回错误 Observation。
2. Agent 根据 Observation 调整策略。
3. 切换备用工具。
4. 成功后输出 Final Answer。
"""


def query_primary_weather_api(city: str) -> dict:
    """模拟主天气接口失败。"""
    return {
        "status": "error",
        "tool": "query_primary_weather_api",
        "error_type": "timeout",
        "message": "主天气接口请求超时",
        "retryable": True,
    }


def query_backup_weather_api(city: str) -> dict:
    """模拟备用天气接口成功。"""
    weather_data = {
        "苏州": "晴，28°C，湿度55%",
        "上海": "小雨，24°C，湿度80%",
        "北京": "晴，22°C，湿度40%",
    }

    return {
        "status": "success",
        "tool": "query_backup_weather_api",
        "city": city,
        "data": weather_data.get(city, f"暂时没有 {city} 的天气数据"),
        "retryable": False,
    }


def append_message(messages: list[dict[str, str]], role: str, content: str) -> None:
    """追加消息。"""
    messages.append(
        {
            "role": role,
            "content": content,
        }
    )


def main() -> None:
    city = "苏州"

    messages = [
        {
            "role": "system",
            "content": "你是一个天气 Agent。工具失败时，要根据 Observation 调整策略。",
        },
        {
            "role": "user",
            "content": f"今天{city}天气怎么样？",
        },
    ]

    print("User:")
    print(f"今天{city}天气怎么样？")
    print("-" * 60)

    thought_1 = "用户问的是实时天气，我应该先调用主天气接口。"
    action_1 = {
        "action": "query_primary_weather_api",
        "action_input": {
            "city": city,
        },
    }

    append_message(messages, "assistant", f"Thought: {thought_1}\nAction: {action_1}")

    print("Thought 1:")
    print(thought_1)
    print("Action 1:")
    print(action_1)
    print("-" * 60)

    observation_1 = query_primary_weather_api(city)
    append_message(messages, "tool", f"Observation: {observation_1}")

    print("Observation 1:")
    print(observation_1)
    print("-" * 60)

    if observation_1["status"] == "error" and observation_1["retryable"]:
        thought_2 = "主接口超时，这是可重试错误。我应该切换备用天气接口。"
        action_2 = {
            "action": "query_backup_weather_api",
            "action_input": {
                "city": city,
            },
        }

        append_message(messages, "assistant", f"Thought: {thought_2}\nAction: {action_2}")

        print("Updated Thought:")
        print(thought_2)
        print("Action 2:")
        print(action_2)
        print("-" * 60)

        observation_2 = query_backup_weather_api(city)
        append_message(messages, "tool", f"Observation: {observation_2}")

        print("Observation 2:")
        print(observation_2)
        print("-" * 60)

        if observation_2["status"] == "success":
            final_answer = f"{city}当前天气：{observation_2['data']}。"
        else:
            final_answer = "天气查询失败，建议稍后重试。"
    else:
        final_answer = "天气查询失败，且当前错误不适合自动重试。"

    append_message(messages, "assistant", f"Final Answer: {final_answer}")

    print("Final Answer:")
    print(final_answer)
    print("-" * 60)

    print("最终 messages：")
    for index, message in enumerate(messages, start=1):
        print(f"{index}. {message['role']}: {message['content']}")


if __name__ == "__main__":
    main()


