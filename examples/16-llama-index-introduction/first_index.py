"""
Day16: first_index.py

这是第 16 天的主练习：使用 LlamaIndex 读取本地资料，并让 LLM 基于资料回答。

这个示例会调用你的真实模型 API。

运行：

python first_index.py
"""

from __future__ import annotations

from pathlib import Path

from llama_index.core import Settings, SimpleDirectoryReader, SummaryIndex

from model_config import build_llm


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


QUESTIONS = [
    "LlamaIndex 是什么？请用适合初学者的话解释。",
    "LlamaHub 是什么？它和 LlamaIndex 是什么关系？",
    "如果我要做 Obsidian 笔记助手，为什么 LlamaIndex 合适？",
    "Alfred 的派对报名表如果提示邮箱无效，可能是什么原因？",
]


def build_query_engine():
    """
    构建一个最小 LlamaIndex 查询引擎。

    这里使用 SummaryIndex，而不是 VectorStoreIndex：
    - 它不需要额外 embedding API。
    - 更适合 Day16 入门学习组件和索引概念。
    - 数据量很小时，直接总结式查询足够清楚。
    """
    Settings.llm = build_llm()

    documents = SimpleDirectoryReader(input_dir=str(DATA_DIR)).load_data()
    index = SummaryIndex.from_documents(documents)

    return index.as_query_engine(response_mode="tree_summarize")


def run_questions() -> None:
    """依次询问几个和 Day16 学习内容对应的问题。"""
    query_engine = build_query_engine()

    print("=" * 80)
    print("Day16: LlamaIndex 本地资料问答")
    print("=" * 80)
    print(f"资料目录：{DATA_DIR}")

    for question in QUESTIONS:
        print("\n" + "-" * 80)
        print(f"问题：{question}")
        print("-" * 80)

        response = query_engine.query(question)

        print("回答：")
        print(response)


def main() -> None:
    """运行主练习。"""
    run_questions()


if __name__ == "__main__":
    main()
