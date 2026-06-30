"""
第17天：查询本地 Chroma 知识库

前提：
python first_index.py

运行：
python query_local_notes.py
"""

import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore

from model_config import init_models


CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "alfred_day17"


def get_query_engine():
    init_models()

    db = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
    )

    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        similarity_top_k=3,
    )

    return query_engine


def main() -> None:
    query_engine = get_query_engine()

    print("本地 RAG 知识库已启动。输入 exit 退出。")

    while True:
        question = input("\n请输入你的问题：").strip()

        if question.lower() in {"exit", "quit", "q"}:
            print("已退出")
            break

        if not question:
            continue

        response = query_engine.query(question)

        print("\n====== 回答 ======")
        print(response)


if __name__ == "__main__":
    main()
