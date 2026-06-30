"""
第17天：LlamaIndex 组件流程演示

运行：
python component_flow_demo.py
"""

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter

from model_config import init_models


def main() -> None:
    init_models()

    document = Document(
        text=(
            "Alfred 是一个智能管家。"
            "他需要根据主人和客人的偏好来安排晚宴。"
            "Alice 不吃辣，Bob 对花生过敏。"
            "上次家庭晚宴中，香草烤鸡和南瓜汤很受欢迎。"
            "如果是周五晚上，建议选择轻松、不费力的菜单。"
        )
    )

    print("====== 1. 原始 Document ======")
    print(document.text)

    splitter = SentenceSplitter(
        chunk_size=80,
        chunk_overlap=10,
    )
    nodes = splitter.get_nodes_from_documents([document])

    print("\n====== 2. 切分后的 Nodes ======")
    for i, node in enumerate(nodes, start=1):
        print(f"\n--- Node {i} ---")
        print(node.text)

    index = VectorStoreIndex(nodes)
    print("\n====== 3. 已创建 VectorStoreIndex ======")

    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        similarity_top_k=3,
    )
    print("\n====== 4. 已创建 QueryEngine ======")

    question = "周五晚宴应该准备什么？需要避开什么？"
    response = query_engine.query(question)

    print("\n====== 5. QueryEngine 回答 ======")
    print(response)


if __name__ == "__main__":
    main()
