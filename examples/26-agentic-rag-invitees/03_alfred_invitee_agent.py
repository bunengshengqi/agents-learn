"""Day26 示例 3：模拟 Alfred 调用宾客检索工具。"""  # 说明这个脚本模拟 Agent 集成。 

from __future__ import annotations  # 启用延迟类型注解。 

import json  # 导入 JSON 模块用于读取宾客数据。 
import re  # 导入正则模块用于分词和姓名抽取。 
from dataclasses import dataclass  # 导入 dataclass 用于定义文档。 
from pathlib import Path  # 导入 Path 用于处理文件路径。 

DATA_FILE = Path(__file__).parent / "data" / "invitees.json"  # 定义数据文件路径。 


@dataclass  # 使用 dataclass 自动生成初始化方法。 
class Document:  # 定义文档对象。 
    page_content: str  # 保存文档正文。 
    metadata: dict[str, str]  # 保存文档元数据。 


class GuestInfoRetrieverTool:  # 定义宾客信息检索工具。 
    name = "guest_info_retriever"  # 定义工具名称。 
    description = "Retrieves detailed information about gala guests based on name or relation."  # 定义工具描述。 
    stopwords = {"what", "is", "the", "our", "guest", "named", "tell", "me", "about", "who", "my", "from", "email"}  # 定义检索时忽略的通用词。 

    def __init__(self, documents: list[Document]) -> None:  # 定义初始化方法。 
        self.documents = documents  # 保存文档列表。 

    def tokenize(self, text: str) -> set[str]:  # 定义文本分词方法。 
        raw_words = re.findall(r"[a-zA-Z0-9@.']+", text.lower())  # 提取文本中的候选词元。 
        cleaned_words = [word.strip(".,!?;:'\"()[]") for word in raw_words]  # 去除候选词首尾标点。 
        filtered_words = [word for word in cleaned_words if word and word not in self.stopwords]  # 过滤空词和通用停用词。 
        return set(filtered_words)  # 返回词元集合。 

    def score_document(self, query: str, document: Document) -> int:  # 定义文档打分方法。 
        query_tokens = self.tokenize(query)  # 对查询分词。 
        document_tokens = self.tokenize(document.page_content)  # 对文档分词。 
        return len(query_tokens & document_tokens)  # 返回关键词交集数量。 

    def forward(self, query: str, limit: int = 3) -> str:  # 定义工具调用方法。 
        scored = [(self.score_document(query, document), document) for document in self.documents]  # 计算每篇文档分数。 
        positive = [(score, document) for score, document in scored if score > 0]  # 过滤掉零分文档。 
        positive.sort(key=lambda item: item[0], reverse=True)  # 按分数降序排序。 
        selected = [document for _, document in positive[:limit]]  # 选择前几篇文档。 
        if not selected:  # 判断是否没有匹配结果。 
            return "No matching guest information found."  # 返回无匹配提示。 
        return "\n\n".join(document.page_content for document in selected)  # 拼接结果文本。 


def load_invitees() -> list[dict[str, str]]:  # 定义函数加载宾客数据。 
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))  # 读取并解析 JSON 数据。 


def invitee_to_document(invitee: dict[str, str]) -> Document:  # 定义函数把记录转成 Document。 
    page_content = "\n".join(  # 构造多行正文。 
        [  # 创建正文行列表。 
            f"Name: {invitee['name']}",  # 写入姓名。 
            f"Relation: {invitee['relation']}",  # 写入关系。 
            f"Description: {invitee['description']}",  # 写入描述。 
            f"Email: {invitee['email']}",  # 写入邮箱。 
        ]  # 结束正文行列表。 
    )  # 完成正文拼接。 
    return Document(page_content=page_content, metadata={"name": invitee["name"]})  # 返回文档对象。 


def build_guest_tool() -> GuestInfoRetrieverTool:  # 定义函数创建宾客工具。 
    invitees = load_invitees()  # 加载宾客数据。 
    documents = [invitee_to_document(invitee) for invitee in invitees]  # 将数据转成文档。 
    return GuestInfoRetrieverTool(documents)  # 返回检索工具。 


def alfred_should_use_guest_tool(question: str) -> bool:  # 定义函数判断是否需要宾客工具。 
    keywords = ["guest", "friend", "relation", "email", "ada", "tesla", "curie", "who"]  # 定义触发工具的关键词。 
    normalized = question.lower()  # 将问题转小写方便匹配。 
    return any(keyword in normalized for keyword in keywords)  # 只要命中关键词就使用工具。 


def alfred_answer(question: str, tool: GuestInfoRetrieverTool) -> str:  # 定义 Alfred 的回答函数。 
    if not alfred_should_use_guest_tool(question):  # 判断问题是否不需要宾客工具。 
        return "Sir, this question does not appear to require the guest database."  # 返回无需检索的回答。 
    observation = tool.forward(question)  # 调用宾客检索工具获取观察结果。 
    if observation.startswith("No matching"):  # 判断检索是否没有结果。 
        return "Sir, I could not find matching guest information in the invitee database."  # 返回无匹配回答。 
    return "Sir, I found the following guest information:\n\n" + observation  # 将检索结果组织成 Alfred 的回答。 


def main() -> None:  # 定义脚本入口函数。 
    tool = build_guest_tool()  # 构建宾客检索工具。 
    questions = [  # 定义模拟晚会现场问题列表。 
        "Tell me about our guest named Ada Lovelace.",  # 查询 Ada Lovelace。 
        "Who is my old friend from university days?",  # 查询大学时代老朋友。 
        "What is Marie Curie's email?",  # 查询 Marie Curie 邮箱。 
    ]  # 结束问题列表。 
    for question in questions:  # 遍历所有问题。 
        print("=" * 80)  # 打印分隔线。 
        print("Question:", question)  # 打印问题。 
        print(alfred_answer(question, tool))  # 打印 Alfred 的回答。 


if __name__ == "__main__":  # 判断脚本是否直接执行。 
    main()  # 执行主函数。 
