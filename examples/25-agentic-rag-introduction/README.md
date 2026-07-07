# Day25 Agentic RAG Introduction

这组代码配套 `notes/Day25-Agentic-RAG用例介绍.md`。

第 25 天主要是 Unit 3 的开场，教材本身没有复杂代码，所以这里用本地可运行示例把概念跑出来：

- 普通 RAG：固定检索一个知识库
- Agentic RAG：根据问题动态选择工具

## 运行方式

这些示例只依赖 Python 标准库，不需要 API Key。

```bash
python examples/25-agentic-rag-introduction/01_basic_rag_vs_agentic_rag.py
python examples/25-agentic-rag-introduction/02_agentic_rag_tool_router.py
python examples/25-agentic-rag-introduction/03_agentic_rag_flow_map.py
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `01_basic_rag_vs_agentic_rag.py` | 对比普通 RAG 和 Agentic RAG 的流程差异 |
| `02_agentic_rag_tool_router.py` | 模拟 Alfred 根据问题选择宾客资料、天气、菜单、新闻等工具 |
| `03_agentic_rag_flow_map.py` | 输出 Mermaid 流程图 |
| `data/gala_knowledge.json` | 晚会示例知识库 |

## 学习重点

记住这个区别：

```text
普通 RAG = 每次都检索固定知识库
Agentic RAG = Agent 自己决定查什么、用什么工具、查几次
```
