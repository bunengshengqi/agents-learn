"""模拟在线监控：成本、延迟、错误、用户反馈。"""

from __future__ import annotations

import json
import time

from agent_core import OUTPUT_DIR, TeachingObservableAgent, TraceRecorder, score_answer, write_json


ONLINE_CASES = [
    {
        "input": "LangGraph 适合在什么场景使用？",
        "expected_keywords": ["多步骤", "状态", "控制"],
        "forbidden_keywords": ["只能聊天"],
    },
    {
        "input": "请计算 7 * 8，然后解释是否需要搜索。",
        "expected_keywords": ["56", "不需要搜索"],
        "forbidden_keywords": ["我查到"],
    },
    {
        "input": "GAIA 评测主要考察 Agent 什么能力？",
        "expected_keywords": ["真实世界", "多步骤", "工具"],
        "forbidden_keywords": ["只考闲聊"],
    },
    {
        "input": "帮我解释一个本地知识库没有的冷门概念。",
        "expected_keywords": ["无需外部工具"],
        "forbidden_keywords": ["可靠答案"],
    },
]


def main() -> None:
    """运行一组模拟线上请求，并生成指标摘要。"""

    agent = TeachingObservableAgent()
    rows: list[dict[str, object]] = []

    for index, case in enumerate(ONLINE_CASES, start=1):
        started = time.perf_counter()
        recorder = TraceRecorder(f"online-run-{index}")
        result = agent.run(case["input"], recorder)
        elapsed_ms = round((time.perf_counter() - started) * 1000, 3)
        quality = score_answer(
            result["answer"],
            case["expected_keywords"],
            case["forbidden_keywords"],
        )
        user_feedback = 1 if quality["passed"] else 0
        summary = recorder.summary()
        rows.append(
            {
                "trace_id": recorder.trace_id,
                "input": case["input"],
                "answer": result["answer"],
                "used_tool": result["used_tool"],
                "latency_ms": elapsed_ms,
                "estimated_cost_usd": summary["estimated_cost_usd"],
                "span_count": summary["span_count"],
                "error_count": summary["error_count"],
                "quality_score": quality["score"],
                "user_feedback": user_feedback,
            }
        )

    output_jsonl = OUTPUT_DIR / "online_metrics.jsonl"
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    output_jsonl.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n",
        encoding="utf-8",
    )

    dashboard = {
        "run_count": len(rows),
        "average_latency_ms": round(sum(float(row["latency_ms"]) for row in rows) / len(rows), 3),
        "average_quality_score": round(sum(float(row["quality_score"]) for row in rows) / len(rows), 3),
        "total_estimated_cost_usd": round(sum(float(row["estimated_cost_usd"]) for row in rows), 6),
        "positive_feedback_rate": round(sum(int(row["user_feedback"]) for row in rows) / len(rows), 3),
        "tool_usage": {
            tool: sum(1 for row in rows if row["used_tool"] == tool)
            for tool in sorted({str(row["used_tool"]) for row in rows})
        },
    }
    output_summary = OUTPUT_DIR / "online_metrics_summary.json"
    write_json(output_summary, dashboard)

    print("Online metrics summary:")
    print(json.dumps(dashboard, ensure_ascii=False, indent=2))
    print(f"\nMetrics file: {output_jsonl}")
    print(f"Summary file: {output_summary}")


if __name__ == "__main__":
    main()
