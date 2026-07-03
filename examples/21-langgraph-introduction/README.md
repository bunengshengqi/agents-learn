# Day21 LangGraph Introduction

这组代码配套 `notes/Day21-LangGraph入门与生产级Agent流程控制.md`。

示例默认不调用真实 LLM，也不需要 API Key。它们用普通 Python 函数模拟分类、检索、起草回复等动作，重点是理解 LangGraph 的结构：

- State：流程中的共享状态
- Node：一个独立处理步骤
- Edge：固定流转
- Conditional Edge：条件分支
- Command：节点主动决定下一步
- Interrupt：暂停流程，等待人工输入

## 安装依赖

```bash
pip install -r examples/21-langgraph-introduction/requirements.txt
```

如果你已经安装了仓库根目录的 `requirements.txt`，通常不需要重复安装。

## 运行顺序

```bash
python examples/21-langgraph-introduction/01_basic_state_graph.py
python examples/21-langgraph-introduction/02_document_router_graph.py
python examples/21-langgraph-introduction/03_email_triage_graph.py
python examples/21-langgraph-introduction/04_human_interrupt_demo.py
python examples/21-langgraph-introduction/05_visualize_mermaid.py
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `01_basic_state_graph.py` | 最小 LangGraph：State、Node、Edge |
| `02_document_router_graph.py` | 文档类型条件路由：文本 / 表格 / 图片 |
| `03_email_triage_graph.py` | 邮件分拣工作流：分类、检索、工单、人工审核 |
| `04_human_interrupt_demo.py` | `interrupt()` 人类介入和恢复执行示例 |
| `05_visualize_mermaid.py` | 输出 Mermaid 图，帮助理解可视化 |

## 学习建议

先不要急着接入真实大模型。先看懂：

```text
输入状态 -> 节点处理 -> 更新状态 -> 路由到下一个节点
```

等这个结构熟了，再把示例里的规则函数替换成真实 LLM 调用。
