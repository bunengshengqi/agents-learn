"""Day24 示例 1：规则版文档分析 Agent。

这个脚本不调用真实 LLM，但仍然使用 LangGraph 的：
- AgentState
- add_messages
- ToolNode
- tools_condition

它模拟了 ReAct 工具调用循环：

assistant -> tools -> assistant -> tools -> assistant -> END
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from typing_extensions import TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


DATA_FILE = Path(__file__).parent / "data" / "alfred_invoice.txt"


class AgentState(TypedDict, total=False):
    input_file: str | None
    messages: Annotated[list[AnyMessage], add_messages]


@tool
def extract_text(file_path: str) -> str:
    """Extract text from a local text-like document file."""
    path = Path(file_path)
    if not path.exists():
        return f"ERROR: file not found: {file_path}"

    if path.suffix.lower() not in {".txt", ".md", ".csv"}:
        return f"ERROR: unsupported file type for this demo: {path.suffix}"

    return path.read_text(encoding="utf-8")


@tool
def divide(a: float, b: float) -> str:
    """Divide a by b and return the result."""
    if b == 0:
        return "ERROR: cannot divide by zero"
    return str(a / b)


TOOLS = [extract_text, divide]


def first_human_question(messages: list[AnyMessage]) -> str:
    for message in messages:
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def latest_tool_message(messages: list[AnyMessage]) -> ToolMessage | None:
    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            return message
    return None


def assistant(state: AgentState) -> dict:
    """A deterministic assistant that simulates LLM tool decisions."""
    messages = state.get("messages", [])
    question = first_human_question(messages).lower()
    tool_message = latest_tool_message(messages)
    input_file = state.get("input_file") or str(DATA_FILE)

    if tool_message is None:
        return {
            "messages": [
                AIMessage(
                    content="I need to extract text from the document first.",
                    tool_calls=[
                        {
                            "name": "extract_text",
                            "args": {"file_path": input_file},
                            "id": "call_extract_text",
                            "type": "tool_call",
                        }
                    ],
                )
            ]
        }

    if tool_message.name == "extract_text":
        extracted_text = str(tool_message.content)
        if extracted_text.startswith("ERROR:"):
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "I could not analyze the document because text extraction failed: "
                            f"{extracted_text}"
                        )
                    )
                ]
            }

        needs_average = "average" in question or "平均" in question or "per service hour" in question
        if needs_average:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "I found Total Amount = 1200 and Number of Service Hours = 40. "
                            "I need to divide 1200 by 40."
                        ),
                        tool_calls=[
                            {
                                "name": "divide",
                                "args": {"a": 1200, "b": 40},
                                "id": "call_divide",
                                "type": "tool_call",
                            }
                        ],
                    )
                ]
            }

        return {
            "messages": [
                AIMessage(
                    content=(
                        "Based on the extracted document, this is an invoice for Alfred "
                        "Consulting Service. The total amount is 1200 USD."
                    )
                )
            ]
        }

    if tool_message.name == "divide":
        if str(tool_message.content).startswith("ERROR:"):
            return {
                "messages": [
                    AIMessage(content=f"The calculation failed: {tool_message.content}")
                ]
            }

        return {
            "messages": [
                AIMessage(
                    content=(
                        "The average cost per service hour is "
                        f"{tool_message.content} USD."
                    )
                )
            ]
        }

    return {"messages": [AIMessage(content="I do not need more tools. Here is the final answer.")]}


def build_graph():
    builder = StateGraph(AgentState)

    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(TOOLS))

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    return builder.compile()


def print_conversation(messages: list[AnyMessage]) -> None:
    for index, message in enumerate(messages, start=1):
        print(f"\n--- Message {index}: {message.type} ---")
        print(message.content)
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            print("tool_calls:", tool_calls)


if __name__ == "__main__":
    graph = build_graph()

    result = graph.invoke(
        {
            "input_file": str(DATA_FILE),
            "messages": [
                HumanMessage(
                    content=(
                        "Please analyze this document and tell me the average cost "
                        "per service hour."
                    )
                )
            ],
        }
    )

    print_conversation(result["messages"])
