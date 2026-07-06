"""Day24 示例 4：输出文档分析 Agent 的 Mermaid 图。

运行：

python examples/24-langgraph-document-analysis-agent/04_mermaid_visualization.py

把输出复制到 Obsidian 的 Mermaid 代码块中即可查看图。
"""

from typing import Annotated

from langchain_core.messages import AIMessage, AnyMessage
from langchain_core.tools import tool
from typing_extensions import TypedDict

from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


class AgentState(TypedDict, total=False):
    input_file: str | None
    messages: Annotated[list[AnyMessage], add_messages]


@tool
def extract_text(file_path: str) -> str:
    """Extract text from a local document file."""
    return "sample text"


@tool
def divide(a: float, b: float) -> str:
    """Divide a by b."""
    if b == 0:
        return "ERROR: cannot divide by zero"
    return str(a / b)


TOOLS = [extract_text, divide]


def assistant(state: AgentState) -> dict:
    return {"messages": [AIMessage(content="Final answer without tool calls.")]}


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(TOOLS))

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()
    print(graph.get_graph().draw_mermaid())
