"""
Day16: query_local_notes.py

命令行版本地资料问答。

运行：

python query_local_notes.py "LlamaHub 怎么安装？"
"""

from __future__ import annotations

import argparse
from pathlib import Path

from llama_index.core import Settings, SimpleDirectoryReader, SummaryIndex

from model_config import build_llm


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def build_query_engine():
    """读取 data/ 目录并构建查询引擎。"""
    Settings.llm = build_llm()

    documents = SimpleDirectoryReader(input_dir=str(DATA_DIR)).load_data()
    index = SummaryIndex.from_documents(documents)

    return index.as_query_engine(response_mode="tree_summarize")


def main() -> None:
    """读取命令行问题，并基于本地资料回答。"""
    parser = argparse.ArgumentParser(description="Day16 LlamaIndex 本地资料问答")
    parser.add_argument("question", help="你想问本地资料的问题")
    args = parser.parse_args()

    query_engine = build_query_engine()
    response = query_engine.query(args.question)

    print(response)


if __name__ == "__main__":
    main()
