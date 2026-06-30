"""
第17天：构建第一个本地 RAG 索引

运行：
python first_index.py
"""

from pathlib import Path
import shutil

import chromadb
from llama_index.core import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore

from model_config import init_models


DATA_DIR = "./data"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "alfred_day17"


def build_index(reset: bool = False) -> VectorStoreIndex:
    init_models()

    if reset and Path(CHROMA_PATH).exists():
        shutil.rmtree(CHROMA_PATH)
        print(f"已删除旧向量库：{CHROMA_PATH}")

    documents = SimpleDirectoryReader(input_dir=DATA_DIR).load_data()
    print(f"加载文档数量：{len(documents)}")

    splitter = SentenceSplitter(
        chunk_size=256,
        chunk_overlap=30,
    )
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"切分 Node 数量：{len(nodes)}")

    db = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = db.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex(
        nodes,
        storage_context=storage_context,
    )

    print(f"索引构建完成，向量库路径：{CHROMA_PATH}")
    return index


def main() -> None:
    index = build_index(reset=True)

    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        similarity_top_k=3,
    )

    question = "周五晚上家庭晚宴应该准备什么菜单？需要注意哪些饮食禁忌？"
    response = query_engine.query(question)

    print("\n====== 测试问题 ======")
    print(question)

    print("\n====== QueryEngine 回答 ======")
    print(response)


if __name__ == "__main__":
    main()
