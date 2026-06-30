"""
第19天代码 00：概念流程图

不调用模型 API。

运行：
python 00_agent_workflow_map.py
"""

from __future__ import annotations


def main() -> None:
    """打印 Day17 -> Day18 -> Day19 的关系。"""
    print("=" * 80)
    print("Day19: LlamaIndex AgentWorkflow 学习地图")
    print("=" * 80)

    print(
        """
Day17：组件与 QueryEngine
  你的数据 -> Reader -> Index -> QueryEngine -> RAG 问答

Day18：工具系统
  FunctionTool：把 Python 函数变成工具
  QueryEngineTool：把 QueryEngine 变成 Agent 可调用的 RAG 工具

Day19：智能体系统
  AgentWorkflow：让 Agent 判断什么时候调用哪个工具
  ReActAgent：用 Thought / Action / Observation 循环调用工具
  FunctionAgent：适合支持 function calling 的模型
  Context：保存多轮对话状态
  Multi-Agent：多个职责清晰的 Agent 在同一个 workflow 中协作
"""
    )

    print("核心结论：第19天不是重新学工具，而是学习 Agent 如何选择和组合工具。")


if __name__ == "__main__":
    main()
