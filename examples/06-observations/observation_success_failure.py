"""
Day 6: Observation Success and Failure

这个脚本不调用大模型。
它用于理解：
1. Action 执行后会产生 Observation。
2. Observation 要放回 messages。
3. Observation 可能成功，也可能失败。
"""


def query_weather(city: str) -> dict:
    """模拟天气工具。"""
    weather_data = {
        "苏州": "晴，28°C，湿度55%",
        "上海": "小雨，24°C，湿度80%",
        "北京": "晴，22°C，湿度40%",
    }

    if not city:
        return {
            "status": "error",
            "tool": "query_weather",
            "error_type": "missing_parameter",
            "message": "缺少必要参数 city",
            "retryable": False,
        }

    if city not in weather_data:
        return {
            "status": "partial_success",
            "tool": "query_weather",
            "message": f"没有查询到 {city} 的天气数据",
            "retryable": False,
        }

    return {
        "status": "success",
        "tool": "query_weather",
        "city": city,
        "data": weather_data[city],
        "retryable": False,
    }


def append_observation(messages: list[dict[str, str]], observation: dict) -> None:
    """把 Observation 放回 messages。"""
    messages.append(
        {
            "role": "tool",
            "content": f"Observation: {observation}",
        }
    )


def main() -> None:
    messages = [
        {
            "role": "system",
            "content": "你是一个天气 Agent，可以调用 query_weather 工具。",
        },
        {
            "role": "user",
            "content": "今天苏州天气怎么样？",
        },
    ]

    print("初始 messages：")
    print(messages)
    print("-" * 60)

    action = {
        "action": "query_weather",
        "action_input": {
            "city": "苏州",
        },
    }

    print("Action：")
    print(action)
    print("-" * 60)

    observation = query_weather(action["action_input"]["city"])

    print("工具执行后得到 Observation：")
    print(observation)
    print("-" * 60)

    append_observation(messages, observation)

    print("Observation 放回 messages 后：")
    for message in messages:
        print(message)

    print("-" * 60)
    print("理解重点：")
    print("Observation 是工具执行结果。")
    print("Observation 必须放回 messages，模型下一轮才知道真实结果。")


if __name__ == "__main__":
    main()


