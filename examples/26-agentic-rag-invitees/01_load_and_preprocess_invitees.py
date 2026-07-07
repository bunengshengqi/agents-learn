"""Day26 示例 1：加载并预处理宾客数据。"""  # 说明这个脚本的学习目标。

from __future__ import annotations  # 让类型注解在运行时更轻量。 

import json  # 导入 JSON 模块用于读取本地数据文件。 
from dataclasses import dataclass  # 导入 dataclass 用于定义简单文档结构。 
from pathlib import Path  # 导入 Path 用于跨平台处理文件路径。 

DATA_FILE = Path(__file__).parent / "data" / "invitees.json"  # 定义本地宾客数据文件路径。 


@dataclass  # 使用 dataclass 自动生成初始化方法。 
class Document:  # 定义一个简化版 Document，模拟 LangChain/LlamaIndex 的文档对象。 
    page_content: str  # 保存可检索的正文内容。 
    metadata: dict[str, str]  # 保存文档元数据，例如宾客姓名。 


def load_invitees() -> list[dict[str, str]]:  # 定义函数用于加载原始宾客数据。 
    raw_text = DATA_FILE.read_text(encoding="utf-8")  # 读取 JSON 文件的文本内容。 
    invitees = json.loads(raw_text)  # 将 JSON 文本解析为 Python 列表。 
    return invitees  # 返回原始宾客记录列表。 


def invitee_to_document(invitee: dict[str, str]) -> Document:  # 定义函数把一条宾客记录转成文档。 
    page_content = "\n".join(  # 把多个字段拼成适合检索的多行文本。 
        [  # 创建需要拼接的文本行列表。 
            f"Name: {invitee['name']}",  # 把宾客姓名写入文档正文。 
            f"Relation: {invitee['relation']}",  # 把宾客关系写入文档正文。 
            f"Description: {invitee['description']}",  # 把宾客描述写入文档正文。 
            f"Email: {invitee['email']}",  # 把宾客邮箱写入文档正文。 
        ]  # 结束文本行列表。 
    )  # 完成多行文本拼接。 
    metadata = {"name": invitee["name"]}  # 创建元数据，用姓名标识文档来源。 
    return Document(page_content=page_content, metadata=metadata)  # 返回标准化后的文档对象。 


def build_documents(invitees: list[dict[str, str]]) -> list[Document]:  # 定义函数批量转换记录。 
    documents = [invitee_to_document(invitee) for invitee in invitees]  # 使用列表推导式转换所有宾客。 
    return documents  # 返回文档列表。 


def main() -> None:  # 定义脚本入口函数。 
    invitees = load_invitees()  # 加载原始宾客数据。 
    documents = build_documents(invitees)  # 将原始数据转换为文档对象。 
    print(f"Loaded invitees: {len(invitees)}")  # 打印加载到的宾客数量。 
    print(f"Built documents: {len(documents)}")  # 打印转换后的文档数量。 
    for document in documents:  # 遍历每个文档用于展示。 
        print("=" * 80)  # 打印分隔线方便阅读。 
        print(document.page_content)  # 打印文档正文。 
        print("metadata:", document.metadata)  # 打印文档元数据。 


if __name__ == "__main__":  # 判断当前文件是否被直接运行。 
    main()  # 调用主函数执行示例。 
