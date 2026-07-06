# Day24 LangGraph Document Analysis Agent

这组代码配套 `notes/Day24-LangGraph文档分析智能体.md`。

第 24 天重点是构建一个能调用工具的文档分析 Agent：

```text
START
  -> assistant
  -> tools_condition
  -> tools
  -> assistant
  -> END
```

这个结构体现了课程里的 4 个原则：

- 定义清晰的工具：`extract_text`、`divide`
- 创建强大的状态跟踪器：`AgentState`
- 考虑错误处理：工具返回清晰错误信息
- 保持上下文感知：`messages: Annotated[..., add_messages]`

## 安装依赖

```bash
pip install -r examples/24-langgraph-document-analysis-agent/requirements.txt
```

如果你已经安装了仓库根目录依赖，通常不需要重复安装。

## 运行顺序

先跑不需要 API Key 的规则版：

```bash
python examples/24-langgraph-document-analysis-agent/01_document_agent_rule_based.py
```

再看工具错误处理：

```bash
python examples/24-langgraph-document-analysis-agent/03_tool_error_handling_demo.py
```

再输出 Mermaid 图：

```bash
python examples/24-langgraph-document-analysis-agent/04_mermaid_visualization.py
```

如果 `.env` 已经配置好 OpenAI 兼容接口，再跑 LLM 版：

```bash
python examples/24-langgraph-document-analysis-agent/02_document_agent_with_llm.py
```

## `.env` 示例

```env
OPENAI_API_KEY=你的真实key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `01_document_agent_rule_based.py` | 不调用真实 LLM，但使用 LangGraph 的 `ToolNode` 和 `tools_condition` 模拟 ReAct 工具循环 |
| `02_document_agent_with_llm.py` | 调用 OpenAI 兼容接口，让 LLM 自己决定是否调用工具 |
| `03_tool_error_handling_demo.py` | 演示工具失败时如何返回清晰错误信息 |
| `04_mermaid_visualization.py` | 输出 Mermaid 图，方便粘贴到 Obsidian |
| `data/alfred_invoice.txt` | 示例文档 |

## 学习建议

先理解这条循环：

```text
assistant 产生 tool call
  -> ToolNode 执行工具
  -> 工具结果追加到 messages
  -> assistant 再次读取 messages
```

这是后面做内容运营 Agent、音频生成 Agent、发布助手 Agent 的重要基础。
