"""
Day 20 code 00: Workflow concept map.

Run:
python 00_workflow_map.py
"""

from __future__ import annotations


def main() -> None:
    rows = [
        ("Workflow", "整个流程容器", "把 RAG / Agent 流程组织起来"),
        ("@step", "处理节点", "接收 Event，执行动作，返回新 Event"),
        ("Event", "数据包 / 信号", "Step 之间不直接调用，而是通过 Event 交互"),
        ("StartEvent", "入口事件", "w.run(...) 传入的参数会进入 StartEvent"),
        ("StopEvent", "结束事件", "StopEvent(result=...) 的 result 是最终返回值"),
        ("Context", "共享状态", "跨 Step 保存 query、结果、重试次数、日志等"),
        ("Branch", "分支", "一个 Step 按条件返回不同 Event"),
        ("Loop", "循环", "返回同类 Event 再次触发某个 Step"),
        ("Fan-out/Fan-in", "拆分与汇总", "同时处理多个子任务，再收集结果"),
        ("AgentWorkflow", "多智能体流程", "让多个 Agent 按职责协作"),
    ]

    print("第20天：LlamaIndex Workflows 练习地图\n")
    for name, meaning, usage in rows:
        print(f"{name:15} | {meaning:10} | {usage}")

    print("\n建议练习顺序：")
    for filename in [
        "01_minimal_workflow.py",
        "02_multi_step_events.py",
        "03_branch_workflow.py",
        "04_loop_workflow.py",
        "05_context_state_workflow.py",
        "06_fan_out_fan_in_workflow.py",
        "07_rag_workflow_with_llm.py",
        "08_agent_workflow_state_demo.py",
        "09_visualize_workflow_optional.py",
    ]:
        print(f"- {filename}")


if __name__ == "__main__":
    main()
