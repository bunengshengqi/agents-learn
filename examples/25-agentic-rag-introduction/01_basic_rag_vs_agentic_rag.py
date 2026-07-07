"""Day25 示例 1：普通 RAG vs Agentic RAG。"""  # 文件说明：这个脚本用来对比普通 RAG 和 Agentic RAG

# 这个脚本只用 Python 标准库，不依赖 LangChain、LlamaIndex、向量数据库等第三方库
# 目的是先把“普通 RAG”和“Agentic RAG”的核心概念跑通
# 普通 RAG：不管用户问什么，都去检索同一个知识库
# Agentic RAG：先判断用户问题类型，再决定调用哪个工具或知识源


from __future__ import annotations  # 启用延迟类型注解，避免某些类型提示在运行时立即求值

import json  # 导入 json 模块，用来读取和解析 JSON 数据
from pathlib import Path  # 导入 Path，用来更方便地处理文件路径


DATA_FILE = Path(__file__).parent / "data" / "gala_knowledge.json"  # 定义知识库文件路径，表示当前脚本目录下的 data/gala_knowledge.json


def load_knowledge() -> dict:  # 定义加载知识库的函数，返回值类型是字典
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))  # 读取 JSON 文件内容，并把 JSON 字符串解析成 Python 字典


def simple_keyword_search(question: str, documents: list[str]) -> list[str]:  # 定义简单关键词检索函数，输入问题和文档列表，返回匹配到的文档列表
    tokens = {token.lower().strip("?.!,") for token in question.split()}  # 把问题按空格切分成单词，转小写并去掉简单标点，最后放入集合去重

    scored = []  # 创建空列表，用来保存每篇文档的匹配分数和文档内容

    for document in documents:  # 遍历文档列表中的每一篇文档
        doc_tokens = {token.lower().strip("?.!,") for token in document.split()}  # 把当前文档也切分成单词，转小写并去掉简单标点
        score = len(tokens & doc_tokens)  # 计算问题单词集合和文档单词集合的交集数量，交集越多代表越相关

        if score > 0:  # 如果匹配分数大于 0，说明这篇文档至少命中了一个关键词
            scored.append((score, document))  # 把分数和文档内容作为一个元组加入 scored 列表

    scored.sort(reverse=True)  # 按分数从高到低排序，因为元组第一位是 score，所以会优先按 score 排序

    return [document for _, document in scored[:3]]  # 取分数最高的前 3 篇文档，并只返回文档内容，不返回分数


def build_flat_documents(knowledge: dict) -> list[str]:  # 定义函数：把结构化知识库拍平成普通文档列表
    documents: list[str] = []  # 创建一个空列表，用来保存所有文本化后的文档

    for guest in knowledge["guest_profiles"]:  # 遍历知识库里的宾客资料列表
        documents.append(  # 把当前宾客信息拼接成一条普通文本，并加入 documents 列表
            f"{guest['name']} interests: {', '.join(guest['interests'])}. "  # 拼接宾客姓名和兴趣爱好
            f"Achievement: {guest['achievement']} "  # 拼接宾客成就信息
            f"Tips: {guest['conversation_tips']}"  # 拼接和该宾客聊天的建议
        )  # 当前宾客文档拼接结束

    documents.append("Menu: " + ", ".join(knowledge["menu"]))  # 把菜单列表拼接成一条普通文本，加入 documents 列表

    documents.append(  # 把活动日程拼接成一条普通文本，加入 documents 列表
        "Schedule: "  # 日程文本的开头
        + "; ".join(f"{item['time']} {item['event']}" for item in knowledge["schedule"])  # 遍历日程列表，把每个时间和事件拼成字符串
    )  # 日程文档拼接结束

    documents.extend(knowledge["party_rules"])  # 把派对规则列表直接追加到 documents 中，每条规则作为一篇文档

    return documents  # 返回拍平后的普通文档列表


def traditional_rag_answer(question: str, knowledge: dict) -> str:  # 定义普通 RAG 回答函数，输入问题和知识库，返回回答文本
    """Traditional RAG always searches the same flattened document list."""  # 函数说明：普通 RAG 总是检索同一个拍平后的文档列表

    documents = build_flat_documents(knowledge)  # 先把结构化知识库转换成普通文档列表

    hits = simple_keyword_search(question, documents)  # 使用简单关键词检索，从普通文档列表中找相关内容

    if not hits:  # 如果没有检索到任何相关文档
        return "Traditional RAG: I could not find relevant information."  # 返回未找到相关信息的提示

    return "Traditional RAG retrieved:\n" + "\n".join(f"- {hit}" for hit in hits)  # 把检索到的文档拼接成普通 RAG 的回答


def agentic_rag_answer(question: str, knowledge: dict) -> str:  # 定义 Agentic RAG 回答函数，输入问题和知识库，返回回答文本
    """Agentic RAG first decides which information source to use."""  # 函数说明：Agentic RAG 会先判断该使用哪个信息源

    normalized = question.lower()  # 把用户问题转成小写，方便后续做关键词判断

    if "weather" in normalized or "fireworks" in normalized:  # 如果问题中包含 weather 或 fireworks，说明问题可能和天气或烟花有关
        return (  # 返回 Agentic RAG 选择天气工具和日程工具后的结果
            "Agentic RAG chose weather/schedule tools:\n"  # 说明 Agentic RAG 选择了天气和日程工具
            "- Weather tool: clear sky, low wind, suitable for fireworks.\n"  # 模拟天气工具返回的结果
            "- Schedule tool: fireworks are planned at 22:00."  # 模拟日程工具返回的烟花时间
        )  # 天气和日程回答结束

    if "menu" in normalized or "vegetarian" in normalized or "food" in normalized:  # 如果问题中包含菜单、素食或食物关键词
        return "Agentic RAG chose menu tool:\n- " + "\n- ".join(knowledge["menu"])  # 返回菜单工具的结果，并把菜单项逐行列出来

    if "alice" in normalized or "bob" in normalized or "clara" in normalized:  # 如果问题中包含具体宾客名字
        guests = [  # 创建 guests 列表，用来保存匹配到的宾客
            guest  # 如果当前 guest 符合条件，就把它加入 guests 列表
            for guest in knowledge["guest_profiles"]  # 遍历知识库中的所有宾客资料
            if guest["name"].split()[0].lower() in normalized  # 判断宾客名字的第一个单词是否出现在用户问题中
        ]  # 宾客匹配列表生成结束

        return "Agentic RAG chose guest profile tool:\n" + "\n".join(  # 返回宾客资料工具的结果
            f"- {guest['name']}: {guest['conversation_tips']}" for guest in guests  # 把每个宾客的名字和聊天建议拼接成一行
        )  # 宾客资料回答结束

    return traditional_rag_answer(question, knowledge)  # 如果没有匹配到特定工具，就退回普通 RAG 的检索方式


if __name__ == "__main__":  # 判断当前脚本是否是被直接运行，而不是被其他 Python 文件导入
    knowledge = load_knowledge()  # 加载 gala_knowledge.json 知识库数据

    questions = [  # 定义测试问题列表
        "What should I talk about with Alice?",  # 测试问题 1：询问应该和 Alice 聊什么
        "Is the weather good for fireworks?",  # 测试问题 2：询问天气是否适合放烟花
        "What vegetarian food is available?",  # 测试问题 3：询问有哪些素食
    ]  # 测试问题列表结束

    for question in questions:  # 遍历每一个测试问题
        print("=" * 80)  # 打印 80 个等号作为分隔线，方便区分不同问题的输出

        print("Question:", question)  # 打印当前问题

        print()  # 打印一个空行，让输出更清晰

        print(traditional_rag_answer(question, knowledge))  # 调用普通 RAG，并打印普通 RAG 的回答

        print()  # 再打印一个空行，分隔普通 RAG 和 Agentic RAG 的输出

        print(agentic_rag_answer(question, knowledge))  # 调用 Agentic RAG，并打印 Agentic RAG 的回答