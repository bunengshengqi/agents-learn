"""
第18天代码 05：Utility Tools 思路演示

Utility Tools 解决的问题：
某些工具返回的数据太多，不能直接全部塞给 LLM。

这里用一个简化例子模拟：
1. 原始工具返回大量日志
2. 把日志变成 Document
3. 建立索引
4. 用 QueryEngine 搜索相关内容

运行：
python 05_utility_tools_demo.py
"""

from llama_index.core import Document, VectorStoreIndex

from model_config import init_models


def get_many_logs() -> str:
    """
    模拟一个会返回大量数据的工具。
    真实场景里，这可能是服务器日志、邮件列表、网页抓取结果等。
    """
    logs = []
    for i in range(1, 101):
        if i % 20 == 0:
            logs.append(f"2026-06-30 10:{i:02d}:00 ERROR 端口 9005 连接失败，目标服务无响应。")
        else:
            logs.append(f"2026-06-30 10:{i:02d}:00 INFO 系统运行正常，任务编号 {i}。")
    return "\n".join(logs)


def main() -> None:
    init_models()

    raw_logs = get_many_logs()

    print("====== 原始工具返回数据 ======")
    print("日志总字符数：", len(raw_logs))
    print("如果直接塞给 LLM，数据可能太多、太杂。")

    document = Document(text=raw_logs)
    index = VectorStoreIndex.from_documents([document])

    query_engine = index.as_query_engine(
        response_mode="tree_summarize",
        similarity_top_k=3,
    )

    question = "请分析 9005 端口连接失败的原因。"
    response = query_engine.query(question)

    print("\n====== Utility Tools 思路：先索引，再查询 ======")
    print(response)


if __name__ == "__main__":
    main()
