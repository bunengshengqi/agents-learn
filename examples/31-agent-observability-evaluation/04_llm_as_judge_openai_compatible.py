"""使用真实 OpenAI-compatible API 做 LLM-as-a-Judge。"""

from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from agent_core import OUTPUT_DIR, TeachingObservableAgent, TraceRecorder, load_jsonl, write_json


DATA_PATH = Path(__file__).resolve().parent / "data" / "offline_eval_cases.jsonl"
REPO_ROOT = Path(__file__).resolve().parents[2]


def load_dotenv(path: Path) -> None:
    """加载简单的 KEY=VALUE 形式 .env 文件。"""

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def call_openai_compatible_chat(messages: list[dict[str, str]]) -> str:
    """通过标准库 urllib 调用 OpenAI-compatible chat/completions。"""

    api_key = os.environ["OPENAI_API_KEY"]
    base_url = os.environ["OPENAI_BASE_URL"].rstrip("/")
    model = os.environ["OPENAI_MODEL"]
    url = f"{base_url}/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"]


def build_judge_messages(case: dict[str, Any], answer: str) -> list[dict[str, str]]:
    """构造 Judge LLM 的评分消息。"""

    rubric = {
        "任务": "你是 Agent 评估器，请根据 rubric 判断回答质量。",
        "评分范围": "score 必须是 0 到 1 的数字。",
        "输出格式": {"score": 0.0, "passed": False, "reason": "简短中文理由"},
        "要求": "只输出 JSON，不要输出 Markdown。",
    }
    user_payload = {
        "input": case["input"],
        "answer": answer,
        "expected_keywords": case["expected_keywords"],
        "forbidden_keywords": case["forbidden_keywords"],
        "rubric": case["rubric"],
    }
    return [
        {"role": "system", "content": json.dumps(rubric, ensure_ascii=False)},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]


def main() -> None:
    """预览或真实运行 LLM-as-a-Judge。"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="真正调用 OpenAI-compatible API")
    parser.add_argument("--limit", type=int, default=3, help="最多评估多少条样本")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    cases = load_jsonl(DATA_PATH)[: args.limit]
    agent = TeachingObservableAgent()
    rows: list[dict[str, Any]] = []

    missing = [name for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL") if not os.environ.get(name)]
    if missing and args.run:
        raise SystemExit(f"缺少环境变量：{', '.join(missing)}")

    for case in cases:
        recorder = TraceRecorder(f"judge-{case['id']}")
        result = agent.run(case["input"], recorder)
        messages = build_judge_messages(case, result["answer"])
        if args.run:
            try:
                judge_raw = call_openai_compatible_chat(messages)
                judge = json.loads(judge_raw)
            except (urllib.error.URLError, KeyError, json.JSONDecodeError) as exc:
                judge = {"score": 0.0, "passed": False, "reason": f"Judge 调用失败：{exc}"}
        else:
            judge = {"score": None, "passed": None, "reason": "预览模式：加 --run 后调用真实 Judge LLM"}
        rows.append(
            {
                "id": case["id"],
                "input": case["input"],
                "answer": result["answer"],
                "judge": judge,
                "trace_id": recorder.trace_id,
            }
        )

    output_path = OUTPUT_DIR / "llm_as_judge_report.json"
    write_json(output_path, rows)

    print("LLM-as-a-Judge report:")
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    print(f"\nReport file: {output_path}")


if __name__ == "__main__":
    main()
