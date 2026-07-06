"""Day24 示例 2：调用 LLM 的文档分析 Agent。

运行前需要在项目根目录配置 .env：

OPENAI_API_KEY=你的真实key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash

这个版本让 LLM 自己决定是否调用 extract_text 和 divide。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


DATA_FILE = Path(__file__).parent / "data" / "alfred_invoice.txt"


class AgentState(TypedDict, total=False):
    input_file: str | None
    messages: Annotated[list[AnyMessage], add_messages]


@tool
def extract_text(file_path: str) -> str:
    """Extract text from a local text-like document file.

    Use this tool when you need to inspect the content of a document file.
    The demo supports .txt, .md, and .csv files.
    """
    path = Path(file_path)
    if not path.exists():
        return f"ERROR: file not found: {file_path}"

    if path.suffix.lower() not in {".txt", ".md", ".csv"}:
        return f"ERROR: unsupported file type for this demo: {path.suffix}"

    return path.read_text(encoding="utf-8")


@tool
def divide(a: float, b: float) -> str:
    """Divide a by b.

    Use this tool when a document analysis question requires a ratio, average,
    or per-unit calculation.
    """
    if b == 0:
        return "ERROR: cannot divide by zero"
    return str(a / b)


TOOLS = [extract_text, divide]


def build_model() -> ChatOpenAI:
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model_name = os.getenv("OPENAI_MODEL")

    missing = [
        name
        for name, value in {
            "OPENAI_API_KEY": api_key,
            "OPENAI_BASE_URL": base_url,
            "OPENAI_MODEL": model_name,
        }.items()
        if not value
    ]

    if missing:
        raise ValueError("缺少环境变量：" + ", ".join(missing))

    return ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model_name,
        temperature=0,
    )


MODEL_WITH_TOOLS = None


def get_model_with_tools():
    global MODEL_WITH_TOOLS
    if MODEL_WITH_TOOLS is None:
        MODEL_WITH_TOOLS = build_model().bind_tools(TOOLS)
    return MODEL_WITH_TOOLS


def assistant(state: AgentState) -> dict:
    input_file = state.get("input_file") or str(DATA_FILE)
    system_message = SystemMessage(
        content=(
            "You are Alfred, a precise document analysis assistant. "
            "Use tools when you need to inspect a document or calculate a value. "
            f"The current input file is: {input_file}. "
            "If a tool returns an ERROR, explain the problem clearly and ask for a fix."
        )
    )

    response = get_model_with_tools().invoke(
        [system_message] + state.get("messages", [])
    )

    return {"messages": [response]}


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

    result = graph.invoke(
        {
            "input_file": str(DATA_FILE),
            "messages": [
                HumanMessage(
                    content=(
                        "Analyze the document. What is the average cost per service hour?"
                    )
                )
            ],
        }
    )

    print("\nFinal conversation:")
    for index, message in enumerate(result["messages"], start=1):
        print(f"\n--- Message {index}: {message.type} ---")
        print(message.content)
        tool_calls = getattr(message, "tool_calls", None)
        if tool_calls:
            print("tool_calls:", tool_calls)
