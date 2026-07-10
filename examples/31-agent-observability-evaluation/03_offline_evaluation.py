"""用固定测试集对 Agent 做离线评估。"""

from __future__ import annotations

import json
from pathlib import Path

from agent_core import (
    OUTPUT_DIR,
    TeachingObservableAgent,
    TraceRecorder,
    load_jsonl,
    score_answer,
    write_json,
)


DATA_PATH = Path(__file__).resolve().parent / "data" / "offline_eval_cases.jsonl"


def main() -> None:
    """运行离线评估并输出报告。"""

    cases = load_jsonl(DATA_PATH)
    agent = TeachingObservableAgent()
    results: list[dict[str, object]] = []

    for case in cases:
        recorder = TraceRecorder(f"offline-eval-{case['id']}")
        result = agent.run(case["input"], recorder)
        score = score_answer(
            result["answer"],
            case["expected_keywords"],
            case["forbidden_keywords"],
        )
        summary = recorder.summary()
        results.append(
            {
                "id": case["id"],
                "input": case["input"],
                "answer": result["answer"],
                "requires_tool": case["requires_tool"],
                "used_tool": result["used_tool"],
                "tool_requirement_passed": (result["used_tool"] != "none") == bool(case["requires_tool"]),
                "score": score["score"],
                "passed": score["passed"],
                "matched_keywords": score["matched_keywords"],
                "violations": score["violations"],
                "estimated_cost_usd": summary["estimated_cost_usd"],
                "span_count": summary["span_count"],
                "trace_id": recorder.trace_id,
                "rubric": case["rubric"],
            }
        )

    passed_count = sum(1 for item in results if item["passed"] and item["tool_requirement_passed"])
    report = {
        "dataset": str(DATA_PATH),
        "case_count": len(results),
        "passed_count": passed_count,
        "pass_rate": round(passed_count / len(results), 3),
        "average_score": round(sum(float(item["score"]) for item in results) / len(results), 3),
        "total_estimated_cost_usd": round(sum(float(item["estimated_cost_usd"]) for item in results), 6),
        "results": results,
    }

    output_path = OUTPUT_DIR / "offline_evaluation_report.json"
    write_json(output_path, report)

    print("Offline evaluation report:")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}, ensure_ascii=False, indent=2))
    print(f"\nReport file: {output_path}")


if __name__ == "__main__":
    main()
