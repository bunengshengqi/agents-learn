"""
Day13: knowledge_base.py

这个文件准备一个小型本地知识库。

真实 RAG 项目通常会把 PDF、网页、Markdown、数据库记录切块后放进检索系统。
这里为了学习清晰，直接用一组 Python 字典模拟文档块。
"""

from __future__ import annotations

from dataclasses import dataclass
import math
import re


@dataclass(frozen=True)
class KnowledgeDocument:
    """表示一个可检索的知识库片段。"""

    title: str
    source: str
    content: str


KNOWLEDGE_BASE: list[KnowledgeDocument] = [
    KnowledgeDocument(
        title="豪华超级英雄派对装饰方案",
        source="party_decoration.md",
        content=(
            "豪华超级英雄主题派对可以使用金色装饰、天鹅绒帘幕、城市天际线投影、"
            "超级英雄徽标灯牌和黑金配色。入口可以设计成 Gotham Manor 风格，"
            "让客人进入时就感到正式和沉浸。"
        ),
    ),
    KnowledgeDocument(
        title="超级英雄主题餐饮方案",
        source="party_catering.md",
        content=(
            "餐饮可以设计成英雄主题菜单，例如 Hulk 绿色能量饮、Iron Man 能量牛排、"
            "Wonder Woman 金色甜点和 Gotham 黑巧克力塔。豪华版本应包含无酒精鸡尾酒、"
            "小份精致主菜和清晰的过敏原标识。"
        ),
    ),
    KnowledgeDocument(
        title="超级英雄派对娱乐流程",
        source="party_entertainment.md",
        content=(
            "娱乐环节可以安排主题 DJ、英雄入场秀、反派假面互动、VR 英雄训练挑战和团队解谜。"
            "如果场地较大，可以把娱乐分成主舞台表演、自由体验区和拍照互动区。"
        ),
    ),
    KnowledgeDocument(
        title="派对预算控制清单",
        source="party_budget.md",
        content=(
            "预算控制建议先确定场地、餐饮、装饰、娱乐和摄影五个大项。"
            "如果预算有限，应优先保证餐饮质量和核心视觉装饰，减少一次性小道具。"
        ),
    ),
    KnowledgeDocument(
        title="Obsidian 学习笔记 RAG 方案",
        source="obsidian_rag.md",
        content=(
            "Obsidian 知识库可以按课程、项目、主题切块，建立检索工具。"
            "智能体先检索相关笔记，再综合成学习总结、复习清单或行动计划。"
        ),
    ),
    KnowledgeDocument(
        title="996tokens 客服知识库方案",
        source="support_rag.md",
        content=(
            "996tokens 客服 Agent 可以检索模型价格、充值说明、接口报错、base_url 配置和常见问题。"
            "当用户问题涉及最新价格或账户状态时，应优先调用实时 API 或人工确认。"
        ),
    ),
    KnowledgeDocument(
        title="Agentic RAG 高级策略",
        source="agentic_rag_strategy.md",
        content=(
            "Agentic RAG 不只是检索一次。智能体可以改写查询、多步检索、多源整合、验证结果，"
            "并在检索失败时使用后备策略。复杂问题通常需要拆成多个查询分别检索。"
        ),
    ),
]


def tokenize(text: str) -> list[str]:
    """
    把文本切成检索 token。

    这个函数不是专业分词器，只是为了教学演示：
    - 英文按单词切分。
    - 中文按连续中文片段和少量关键词命中处理。
    """
    lowered = text.lower()
    words = re.findall(r"[a-z0-9]+|[\u4e00-\u9fff]+", lowered)

    extra_keywords = [
        "装饰",
        "餐饮",
        "娱乐",
        "预算",
        "派对",
        "超级英雄",
        "豪华",
        "检索",
        "知识库",
        "客服",
        "价格",
        "报错",
        "obsidian",
        "rag",
        "agentic",
    ]
    hits = [keyword for keyword in extra_keywords if keyword.lower() in lowered]
    return words + hits


def score_document(query: str, document: KnowledgeDocument) -> float:
    """用一个简化 BM25 风格的算法给文档打分。"""
    query_tokens = tokenize(query)
    document_text = f"{document.title} {document.source} {document.content}"
    document_tokens = tokenize(document_text)
    document_token_set = set(document_tokens)

    score = 0.0
    for token in query_tokens:
        if token in document_token_set:
            frequency = document_tokens.count(token)
            score += 1.0 + math.log(1 + frequency)

    if query.lower() in document_text.lower():
        score += 3.0

    return round(score, 4)


def search_knowledge_base(query: str, top_k: int = 3) -> list[tuple[KnowledgeDocument, float]]:
    """在本地知识库中检索最相关的文档片段。"""
    scored_docs = [
        (document, score_document(query, document))
        for document in KNOWLEDGE_BASE
    ]
    ranked_docs = sorted(scored_docs, key=lambda item: item[1], reverse=True)
    return [(document, score) for document, score in ranked_docs[:top_k] if score > 0]


def format_retrieval_results(results: list[tuple[KnowledgeDocument, float]]) -> str:
    """把检索结果格式化成适合作为 observation 返回给 Agent 的字符串。"""
    if not results:
        return "没有检索到相关资料。"

    blocks = ["检索结果："]
    for index, (document, score) in enumerate(results, start=1):
        blocks.append(
            "\n".join(
                [
                    f"\n===== 文档 {index} =====",
                    f"标题：{document.title}",
                    f"来源：{document.source}",
                    f"相关分数：{score}",
                    f"内容：{document.content}",
                ]
            )
        )
    return "\n".join(blocks)

