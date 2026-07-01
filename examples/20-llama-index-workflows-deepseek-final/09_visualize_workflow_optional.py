"""
Day 20 code 09: optional workflow graph visualization.

The course uses llama-index-utils-workflow for visualization. It is optional.

Install if needed:
pip install llama-index-utils-workflow

Run:
python 09_visualize_workflow_optional.py
"""

from __future__ import annotations

from pathlib import Path

from llama_index.core.workflow import Event, StartEvent, StopEvent, Workflow, step


class RAGEvent(Event):
    query: str


class DirectAnswerEvent(Event):
    query: str


class GraphDemoWorkflow(Workflow):
    @step
    async def classify(self, ev: StartEvent) -> RAGEvent | DirectAnswerEvent:
        query = ev.get("query", "")
        if "知识库" in query:
            return RAGEvent(query=query)
        return DirectAnswerEvent(query=query)

    @step
    async def rag_answer(self, ev: RAGEvent) -> StopEvent:
        return StopEvent(result=f"RAG answer: {ev.query}")

    @step
    async def direct_answer(self, ev: DirectAnswerEvent) -> StopEvent:
        return StopEvent(result=f"Direct answer: {ev.query}")


def main() -> None:
    try:
        from llama_index.utils.workflow import draw_all_possible_flows
    except ModuleNotFoundError:
        print("当前环境没有安装可视化工具。")
        print("如需画图，请运行：pip install llama-index-utils-workflow")
        return

    output_path = Path(__file__).resolve().parent / "workflow_graph.html"
    draw_all_possible_flows(GraphDemoWorkflow, filename=str(output_path))
    print(f"已生成：{output_path}")


if __name__ == "__main__":
    main()
