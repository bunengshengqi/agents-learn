"""运行一次可观测 Agent，并生成本地 trace JSON。"""

from __future__ import annotations

import json

from agent_core import OUTPUT_DIR, TeachingObservableAgent, TraceRecorder


def main() -> None:
    """演示一次完整 trace。"""

    query = "OpenTelemetry 里的 trace 和 span 有什么关系？"
    recorder = TraceRecorder("day31-single-agent-run")
    agent = TeachingObservableAgent()
    result = agent.run(query, recorder)
    output_path = OUTPUT_DIR / "single_trace.json"
    recorder.write_json(output_path)

    print("Agent answer:")
    print(result["answer"])
    print("\nTrace summary:")
    print(json.dumps(recorder.summary(), ensure_ascii=False, indent=2))
    print(f"\nTrace file: {output_path}")


if __name__ == "__main__":
    main()
