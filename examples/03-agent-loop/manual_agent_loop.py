"""
Day 3: Manual Agent Loop

这个脚本是 Day 3 的核心练习：
用 OpenAI 兼容 API 手写一个极简 Thought -> Action -> Observation 循环。

运行前需要在项目根目录准备 .env：

OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=你的中转站地址
OPENAI_MODEL=你的模型名
"""

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
model = os.getenv("OPENAI_MODEL")


SYSTEM_PROMPT = """
你是一个教学用 AI Agent。

你可以使用下面这些工具：

Tool Name: calculator
Description: 计算两个整数相乘
Arguments: a: int, b: int
Outputs: int

Tool Name: get_weather
Description: 查询某个城市的模拟天气
Arguments: location: str
Outputs: str

你必须遵守下面的工作流程：

1. 如果需要调用工具，先输出 Thought，再输出 Action。
2. Action 必须是严格 JSON，不要写 Markdown 代码块。
3. Action 格式如下：
{
  "action": "工具名称",
  "action_input": {
    "参数名": "参数值"
  }
}
4. 如果你已经拿到 Observation，可以输出 Final Answer。
5. Final Answer 必须用中文回答用户。

示例：

Thought: 我需要计算两个数相乘，可以调用 calculator 工具。
Action:
{
  "action": "calculator",
  "action_input": {
    "a": 12,
    "b": 8
  }
}
"""


def validate_config() -> None:
    """检查环境变量是否配置完整。"""
    missing = []

    if not api_key:
        missing.append("OPENAI_API_KEY")
    if not base_url:
        missing.append("OPENAI_BASE_URL")
    if not model:
        missing.append("OPENAI_MODEL")

    if missing:
        raise ValueError("缺少环境变量：" + ", ".join(missing))


def call_llm(messages: list[dict[str, str]]) -> str:
    """调用 OpenAI 兼容接口。"""
    validate_config()

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
    )

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
    )

    return response.choices[0].message.content or ""


def calculator(a: int, b: int) -> int:
    """计算两个整数相乘。"""
    return a * b


def get_weather(location: str) -> str:
    """模拟天气工具。真实项目里可以替换成天气 API。"""
    weather_data = {
        "New York": "多云，15°C，湿度60%",
        "Suzhou": "晴，28°C，湿度55%",
        "Shanghai": "小雨，24°C，湿度80%",
        "北京": "晴，22°C，湿度40%",
        "苏州": "晴，28°C，湿度55%",
        "上海": "小雨，24°C，湿度80%",
    }

    return weather_data.get(location, f"暂时没有 {location} 的天气数据")


def extract_action(text: str) -> dict[str, Any] | None:
    """
    从模型输出中提取 Action JSON。

    课程阶段先用简单方法：
    找到第一个 { 和最后一个 }，中间内容按 JSON 解析。
    """
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    json_text = text[start : end + 1]

    try:
        action = json.loads(json_text)
    except json.JSONDecodeError:
        return None

    if "action" not in action or "action_input" not in action:
        return None

    return action


def run_tool(action: dict[str, Any]) -> str:
    """根据模型给出的 action 执行本地工具。"""
    tool_name = action["action"]
    tool_input = action["action_input"]

    if tool_name == "calculator":
        result = calculator(
            a=int(tool_input["a"]),
            b=int(tool_input["b"]),
        )
        return str(result)

    if tool_name == "get_weather":
        return get_weather(location=str(tool_input["location"]))

    return f"未知工具：{tool_name}"


def main() -> None:
    """运行极简 Agent Loop。"""
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    print("Day 3: Manual Agent Loop")
    print("可测试：")
    print("1. 12 乘以 8 等于多少？")
    print("2. 今天苏州天气怎么样？")
    print("输入 exit / quit / q 退出")
    print("-" * 60)

    while True:
        user_input = input("用户：").strip()

        if user_input.lower() in {"exit", "quit", "q"}:
            print("程序已退出。")
            break

        if not user_input:
            print("输入不能为空。")
            continue

        messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        assistant_message = call_llm(messages)
        print("\n模型第一次输出：")
        print(assistant_message)
        print("-" * 60)

        action = extract_action(assistant_message)

        if action is None:
            print("没有检测到 Action，直接作为最终回答。")
            print(assistant_message)
            print("-" * 60)
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message,
                }
            )
            continue

        observation = run_tool(action)

        print("Python 执行工具后得到 Observation：")
        print(observation)
        print("-" * 60)

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message,
            }
        )

        messages.append(
            {
                "role": "user",
                "content": f"Observation: {observation}\n请基于 Observation 输出 Final Answer。",
            }
        )

        final_answer = call_llm(messages)

        messages.append(
            {
                "role": "assistant",
                "content": final_answer,
            }
        )

        print("Final Answer:")
        print(final_answer)
        print("-" * 60)


if __name__ == "__main__":
    main()


