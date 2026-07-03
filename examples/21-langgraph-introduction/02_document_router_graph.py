"""Day21 示例 2：文档类型条件路由。

这个例子对应课程里的文档分析场景：
不同类型的文档，需要进入不同处理分支。

普通文本 -> 抽取文本
表格文件 -> 用代码解析
图片文件 -> OCR / VLM 转文本
"""

from pathlib import Path
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph


class DocumentState(TypedDict, total=False):
    file_name: str
    question: str
    doc_type: str
    extracted_text: str
    answer: str


def detect_document_type(state: DocumentState) -> dict:
    suffix = Path(state["file_name"]).suffix.lower()

    if suffix in {".csv", ".xls", ".xlsx"}:
        doc_type = "table"
    elif suffix in {".png", ".jpg", ".jpeg"}:
        doc_type = "image"
    else:
        doc_type = "text"

    return {"doc_type": doc_type}


def route_by_doc_type(state: DocumentState) -> Literal["text", "table", "image"]:
    return state["doc_type"]  # type: ignore[return-value]


def extract_text_document(state: DocumentState) -> dict:
    return {
        "extracted_text": (
            f"从文本文件 {state['file_name']} 中抽取到："
            "LangGraph 适合多步骤、有状态、可控的 Agent 工作流。"
        )
    }


def extract_table_document(state: DocumentState) -> dict:
    return {
        "extracted_text": (
            f"从表格文件 {state['file_name']} 中解析到："
            "本月投诉数 12，账单问题占比最高。"
        )
    }


def extract_image_document(state: DocumentState) -> dict:
    return {
        "extracted_text": (
            f"从图片文件 {state['file_name']} 中识别到："
            "图片包含一张流程图，展示邮件分类到人工审核的过程。"
        )
    }


def answer_question(state: DocumentState) -> dict:
    answer = (
        f"问题：{state['question']}\n"
        f"文档类型：{state['doc_type']}\n"
        f"基于抽取内容的回答：{state['extracted_text']}"
    )
    return {"answer": answer}


def build_graph():
    builder = StateGraph(DocumentState)

    builder.add_node("detect_document_type", detect_document_type)
    builder.add_node("extract_text_document", extract_text_document)
    builder.add_node("extract_table_document", extract_table_document)
    builder.add_node("extract_image_document", extract_image_document)
    builder.add_node("answer_question", answer_question)

    builder.add_edge(START, "detect_document_type")
    builder.add_conditional_edges(
        "detect_document_type",
        route_by_doc_type,
        {
            "text": "extract_text_document",
            "table": "extract_table_document",
            "image": "extract_image_document",
        },
    )
    builder.add_edge("extract_text_document", "answer_question")
    builder.add_edge("extract_table_document", "answer_question")
    builder.add_edge("extract_image_document", "answer_question")
    builder.add_edge("answer_question", END)

    return builder.compile()


if __name__ == "__main__":
    graph = build_graph()

    test_cases = [
        {"file_name": "agent_notes.md", "question": "LangGraph 适合什么场景？"},
        {"file_name": "billing_report.xlsx", "question": "投诉主要集中在哪里？"},
        {"file_name": "workflow.png", "question": "图片展示了什么？"},
    ]

    for case in test_cases:
        print("=" * 60)
        print(graph.invoke(case)["answer"])
