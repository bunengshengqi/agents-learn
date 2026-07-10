"""展示特殊 token 如何把函数调用对话分隔成清晰的协议。"""

from __future__ import annotations

import json
from dataclasses import dataclass


SPECIAL_TOKENS = (
    "<|available_tools|>",
    "<|end_available_tools|>",
    "<|user|>",
    "<|thought|>",
    "<|tool_call|>",
    "<|observation|>",
    "<|final|>",
    "<|end|>",
)


@dataclass(frozen=True)
class FunctionCallingExample:
    """一条完整的函数调用教学样本。"""

    tools: list[dict[str, object]]
    user: str
    thought_summary: str
    tool_call: dict[str, object]
    observation: dict[str, object]
    final_answer: str


def render_example(example: FunctionCallingExample) -> str:
    """把结构化字段渲染为可供 tokenizer 处理的文本。"""

    tools_json = json.dumps(example.tools, ensure_ascii=False, separators=(",", ":"))
    call_json = json.dumps(example.tool_call, ensure_ascii=False, separators=(",", ":"))
    observation_json = json.dumps(
        example.observation,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return "\n".join(
        [
            f"<|available_tools|>{tools_json}<|end_available_tools|>",
            f"<|user|>{example.user}<|end|>",
            f"<|thought|>{example.thought_summary}<|end|>",
            f"<|tool_call|>{call_json}<|end|>",
            f"<|observation|>{observation_json}<|end|>",
            f"<|final|>{example.final_answer}<|end|>",
        ]
    )


def validate_protocol(text: str) -> list[str]:
    """检查关键阶段是否存在并按正确顺序出现。"""

    errors: list[str] = []
    ordered_tokens = [
        "<|available_tools|>",
        "<|user|>",
        "<|thought|>",
        "<|tool_call|>",
        "<|observation|>",
        "<|final|>",
    ]
    positions = [text.find(token) for token in ordered_tokens]

    for token, position in zip(ordered_tokens, positions, strict=True):
        if position == -1:
            errors.append(f"缺少特殊 token：{token}")

    existing_positions = [position for position in positions if position >= 0]
    if existing_positions != sorted(existing_positions):
        errors.append("特殊 token 的阶段顺序错误")

    return errors


def build_example() -> FunctionCallingExample:
    """创建一条天气工具样本。"""

    weather_tool = {
        "name": "get_weather",
        "description": "查询指定城市的当前天气",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    }
    return FunctionCallingExample(
        tools=[weather_tool],
        user="杭州今天适合跑步吗？",
        thought_summary="需要先查询杭州的当前天气。",
        tool_call={"name": "get_weather", "arguments": {"city": "杭州"}},
        observation={"city": "杭州", "temperature_c": 24, "condition": "小雨"},
        final_answer="杭州当前 24℃、有小雨，可以短时慢跑，但要注意路滑。",
    )


def main() -> None:
    """输出格式化样本和协议校验结果。"""

    rendered = render_example(build_example())
    errors = validate_protocol(rendered)

    print("已注册的教学特殊 token：")
    for token in SPECIAL_TOKENS:
        print(f"- {token}")

    print("\n格式化后的训练文本：\n")
    print(rendered)
    print("\n协议校验：", "通过" if not errors else "；".join(errors))


if __name__ == "__main__":
    main()

