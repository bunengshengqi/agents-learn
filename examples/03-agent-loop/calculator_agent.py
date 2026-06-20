"""
Day 3: Calculator Agent

这个脚本模拟课程图片里的 calculator 工具。
重点理解：
1. LLM 负责输出 Action。
2. Python 程序负责执行工具。
3. 工具结果作为 Observation 返回给模型。
"""


def calculator(a: int, b: int) -> int:
    """计算两个整数相乘。"""
    return a * b


def run_tool(action: dict) -> str:
    """根据 action 执行对应工具。"""
    tool_name = action["action"]
    tool_input = action["action_input"]

    if tool_name == "calculator":
        result = calculator(
            a=tool_input["a"],
            b=tool_input["b"],
        )
        return str(result)

    return f"未知工具：{tool_name}"


def main() -> None:
    user_question = "12 乘以 8 等于多少？"

    print("User:")
    print(user_question)
    print("-" * 60)

    thought = "我需要计算 12 * 8，可以调用 calculator 工具。"
    print("Thought:")
    print(thought)
    print("-" * 60)

    action = {
        "action": "calculator",
        "action_input": {
            "a": 12,
            "b": 8,
        },
    }
    print("Action:")
    print(action)
    print("-" * 60)

    observation = run_tool(action)
    print("Observation:")
    print(observation)
    print("-" * 60)

    final_answer = f"12 乘以 8 等于 {observation}。"
    print("Final Answer:")
    print(final_answer)


if __name__ == "__main__":
    main()


