"""Day26 示例 2：创建宾客信息检索工具。"""  # 说明这个脚本演示检索工具。 

from __future__ import annotations  # 启用延迟类型注解。 

import json  # 导入 JSON 模块用于读取数据。 
import re  # 导入正则模块用于简单分词。 
from dataclasses import dataclass  # 导入 dataclass 用于定义文档结构。 
from pathlib import Path  # 导入 Path 用于处理文件路径。 

DATA_FILE = Path(__file__).parent / "data" / "invitees.json"  # 定义宾客数据文件路径。 


@dataclass  # 使用 dataclass 简化类定义。 
class Document:  # 定义简化版文档对象。 
    page_content: str  # 保存可检索文本。 
    metadata: dict[str, str]  # 保存文档元数据。 


class GuestInfoRetrieverTool:  # 定义宾客信息检索工具类。 
    name = "guest_info_retriever"  # 定义工具名称，Agent 会通过名称识别工具。 
    description = "Retrieves detailed information about gala guests based on name or relation."  # 定义工具描述，帮助 Agent 判断何时使用。 
    stopwords = {"what", "is", "the", "our", "guest", "named", "tell", "me", "about", "who", "my", "from", "email"}  # 定义检索时忽略的通用词。 

    def __init__(self, documents: list[Document]) -> None:  # 定义初始化方法并接收文档列表。 
        self.documents = documents  # 保存文档列表到实例属性。 

    def tokenize(self, text: str) -> set[str]:  # 定义简单分词函数。 
        raw_words = re.findall(r"[a-zA-Z0-9@.']+", text.lower())  # 从文本中提取候选词片段。 
        cleaned_words = [word.strip(".,!?;:'\"()[]") for word in raw_words]  # 去掉每个词首尾标点。 
        filtered_words = [word for word in cleaned_words if word and word not in self.stopwords]  # 过滤空词和通用停用词。 
        return set(filtered_words)  # 返回去重后的词集合。 

    def score_document(self, query: str, document: Document) -> int:  # 定义文档打分函数。 
        query_tokens = self.tokenize(query)  # 将查询文本分词。 
        document_tokens = self.tokenize(document.page_content)  # 将文档正文分词。 
        overlap = query_tokens & document_tokens  # 计算查询词和文档词的交集。 
        return len(overlap)  # 使用交集词数量作为简单相关性分数。 

    def forward(self, query: str, limit: int = 3) -> str:  # 定义工具调用入口，模拟 smolagents 的 forward。 
        scored_documents = []  # 创建列表保存打分后的文档。 
        for document in self.documents:  # 遍历所有文档。 
            score = self.score_document(query, document)  # 计算当前文档相关性分数。 
            if score > 0:  # 只保留有关键词命中的文档。 
                scored_documents.append((score, document))  # 保存分数和文档对象。 
        scored_documents.sort(key=lambda item: item[0], reverse=True)  # 按分数从高到低排序。 
        top_documents = [document for _, document in scored_documents[:limit]]  # 取最相关的前几篇文档。 
        if not top_documents:  # 判断是否没有任何匹配结果。 
            return "No matching guest information found."  # 返回无匹配提示。 
        return "\n\n".join(document.page_content for document in top_documents)  # 拼接命中文档正文并返回。 


def load_invitees() -> list[dict[str, str]]:  # 定义函数加载原始宾客数据。 
    raw_text = DATA_FILE.read_text(encoding="utf-8")  # 读取 JSON 文件文本。 
    invitees = json.loads(raw_text)  # 解析 JSON 为 Python 对象。 
    return invitees  # 返回宾客记录列表。 


def invitee_to_document(invitee: dict[str, str]) -> Document:  # 定义函数将宾客记录转为 Document。 
    page_content = "\n".join(  # 将字段拼接成多行检索文本。 
        [  # 创建文本行列表。 
            f"Name: {invitee['name']}",  # 添加姓名字段。 
            f"Relation: {invitee['relation']}",  # 添加关系字段。 
            f"Description: {invitee['description']}",  # 添加描述字段。 
            f"Email: {invitee['email']}",  # 添加邮箱字段。 
        ]  # 结束文本行列表。 
    )  # 完成正文拼接。 
    metadata = {"name": invitee["name"]}  # 用姓名构造元数据。 
    return Document(page_content=page_content, metadata=metadata)  # 返回文档对象。 


def build_tool() -> GuestInfoRetrieverTool:  # 定义函数构建检索工具。 
    invitees = load_invitees()  # 加载宾客数据。 
    documents = [invitee_to_document(invitee) for invitee in invitees]  # 将每条数据转成文档。 
    tool = GuestInfoRetrieverTool(documents)  # 用文档列表初始化检索工具。 
    return tool  # 返回工具实例。 


def main() -> None:  # 定义脚本入口函数。 
    tool = build_tool()  # 创建宾客检索工具。 
    queries = ["Ada Lovelace", "old friend from university", "radioactivity"]  # 定义测试查询列表。 
    for query in queries:  # 遍历每个查询。 
        print("=" * 80)  # 打印分隔线。 
        print("Query:", query)  # 打印当前查询。 
        print(tool.forward(query))  # 调用工具并打印结果。 


if __name__ == "__main__":  # 判断是否直接运行脚本。 
    main()  # 执行主函数。 
