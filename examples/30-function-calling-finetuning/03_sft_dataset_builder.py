"""生成 prompt-completion 格式的函数调用 SFT 教学数据集。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
OUTPUT_PATH = SCRIPT_DIR / "data" / "function_calling_sft.jsonl"


TOOLS = [
    {
        "name": "get_weather",
        "description": "查询指定城市的当前天气",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"],
        },
    },
    {
        "name": "calculator",
        "description": "计算一个简单算术表达式",
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string"}},
            "required": ["expression"],
        },
    },
    {
        "name": "publish_article",
        "description": "将已审核文章发布到指定平台，发布前必须获得用户确认",
        "parameters": {
            "type": "object",
            "properties": {
                "platform": {"type": "string"},
                "title": {"type": "string"},
            },
            "required": ["platform", "title"],
        },
    },
]


def compact_json(value: Any) -> str:
    """生成适合训练协议的紧凑 JSON。"""

    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def common_prefix(user: str) -> str:
    """把工具定义和用户消息组成 prompt 的公共前缀。"""

    return (
        f"<|available_tools|>{compact_json(TOOLS)}<|end_available_tools|>\n"
        f"<|user|>{user}<|end|>\n"
    )


def action_record(
    user: str,
    thought_summary: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, str]:
    """创建一条“用户问题 -> 工具调用”训练记录。"""

    completion = (
        f"<|thought|>{thought_summary}<|end|>\n"
        f"<|tool_call|>{compact_json({'name': tool_name, 'arguments': arguments})}<|end|>"
    )
    return {"prompt": common_prefix(user), "completion": completion}


def final_record(
    user: str,
    tool_name: str,
    arguments: dict[str, Any],
    observation: dict[str, Any],
    final_answer: str,
) -> dict[str, str]:
    """创建一条“工具结果 -> 最终回答”训练记录。"""

    call = compact_json({"name": tool_name, "arguments": arguments})
    prompt = (
        common_prefix(user)
        + f"<|tool_call|>{call}<|end|>\n"
        + f"<|observation|>{compact_json(observation)}<|end|>\n"
    )
    return {"prompt": prompt, "completion": f"<|final|>{final_answer}<|end|>"}


def direct_answer_record(user: str, answer: str) -> dict[str, str]:
    """创建一条无需调用工具的负样本。"""

    return {
        "prompt": common_prefix(user),
        "completion": f"<|final|>{answer}<|end|>",
    }


def build_records() -> list[dict[str, str]]:
    """构造成功、无需工具、缺参数和高风险确认等不同场景。"""

    records = [
        action_record(
            "杭州今天适合跑步吗？",
            "需要先查询杭州的当前天气。",
            "get_weather",
            {"city": "杭州"},
        ),
        final_record(
            "杭州今天适合跑步吗？",
            "get_weather",
            {"city": "杭州"},
            {"city": "杭州", "temperature_c": 24, "condition": "小雨"},
            "杭州当前 24℃、有小雨，可以短时慢跑，但要注意路滑。",
        ),
        action_record(
            "计算 28 乘以 17。",
            "这是明确的算术任务，应调用计算器。",
            "calculator",
            {"expression": "28 * 17"},
        ),
        final_record(
            "计算 28 乘以 17。",
            "calculator",
            {"expression": "28 * 17"},
            {"expression": "28 * 17", "result": 476},
            "28 × 17 = 476。",
        ),
        direct_answer_record("你好，请介绍一下自己。", "你好，我是一个可以调用工具完成任务的助手。"),
        direct_answer_record("把这段话改得简洁：我们目前现在正在进行讨论。", "我们正在讨论。"),
        direct_answer_record(
            "帮我查天气。",
            "请告诉我需要查询哪个城市；获得城市名后我才能调用天气工具。",
        ),
        direct_answer_record(
            "立即把《今日热点》发布到头条。",
            "发布属于外部写操作。请先确认文章已审核，并明确回复是否确认发布。",
        ),
        action_record(
            "我确认发布已审核的《今日热点》到头条。",
            "用户已明确确认，可以调用发布工具。",
            "publish_article",
            {"platform": "头条", "title": "今日热点"},
        ),
        final_record(
            "我确认发布已审核的《今日热点》到头条。",
            "publish_article",
            {"platform": "头条", "title": "今日热点"},
            {"status": "success", "article_id": "demo-1001"},
            "文章《今日热点》已发布，文章编号为 demo-1001。",
        ),
    ]
    return records


def write_jsonl(records: list[dict[str, str]], output_path: Path = OUTPUT_PATH) -> None:
    """将训练记录写成 UTF-8 JSONL 文件。"""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> None:
    """生成数据并打印每种训练目标的数量。"""

    records = build_records()
    write_jsonl(records)
    action_count = sum("<|tool_call|>" in record["completion"] for record in records)
    final_count = len(records) - action_count

    print(f"已生成：{OUTPUT_PATH}")
    print(f"总记录数：{len(records)}")
    print(f"工具调用记录：{action_count}")
    print(f"最终回答记录：{final_count}")
    print("说明：prompt 不参与 completion-only loss，模型只学习 completion。")


if __name__ == "__main__":
    main()

