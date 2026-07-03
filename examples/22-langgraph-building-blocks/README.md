# Day22 LangGraph Building Blocks

这组代码配套 `notes/Day22-LangGraph核心构建模块.md`。

第 22 天重点理解 LangGraph 的四个构建模块：

- State：流程中的共享状态
- Node：处理某一步任务的 Python 函数
- Edge：连接节点，决定流程路径
- StateGraph：容纳整个工作流的图容器

## 安装依赖

```bash
pip install -r examples/22-langgraph-building-blocks/requirements.txt
```

如果你已经安装了仓库根目录的依赖，通常不需要重复安装。

## 运行顺序

```bash
python examples/22-langgraph-building-blocks/01_course_mood_graph.py
python examples/22-langgraph-building-blocks/02_state_design_principles.py
python examples/22-langgraph-building-blocks/03_state_updates_and_reducers.py
python examples/22-langgraph-building-blocks/04_email_workflow_blocks.py
python examples/22-langgraph-building-blocks/05_mermaid_visualization.py
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `01_course_mood_graph.py` | 复现课程里的 Node 1 -> Node 2 / Node 3 -> END |
| `02_state_design_principles.py` | 用邮件 Agent 展示 State 怎么从流程推导出来 |
| `03_state_updates_and_reducers.py` | 演示默认覆盖更新和 reducer 追加更新 |
| `04_email_workflow_blocks.py` | 用 State、Node、Edge、StateGraph 组成小型邮件工作流 |
| `05_mermaid_visualization.py` | 输出 Mermaid 图，方便粘贴到 Obsidian |

## 学习建议

先看懂这个公式：

```text
StateGraph = State + Nodes + Edges
```

再去思考更大的问题：

```text
State 里到底应该保存什么？
```

答案不是凭空猜，而是从工作流反推：每个节点需要读什么、写什么，哪些数据会被后续节点继续使用。
