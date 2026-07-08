# Day28 Agentic RAG Agent

这组代码配套 `notes/Day28-创建Gala智能体端到端AgenticRAG.md`。

第 28 天目标是把前几天的工具组合成完整 Alfred：

- 宾客资料工具
- 网络搜索工具
- 天气工具
- Hugging Face Hub 统计工具
- 对话记忆

## 运行方式

这些脚本默认使用离线 mock 数据，不需要 API Key，也不需要访问外网。

```bash
python3 examples/28-agentic-rag-agent/01_smolagents_end_to_end_agent.py
python3 examples/28-agentic-rag-agent/02_llama_index_end_to_end_agent.py
python3 examples/28-agentic-rag-agent/03_langgraph_end_to_end_agent.py
python3 examples/28-agentic-rag-agent/04_compare_end_to_end_agents.py
python3 examples/28-agentic-rag-agent/05_memory_demo.py
python3 examples/28-agentic-rag-agent/06_end_to_end_flow_map.py
```

如果你已经在项目根目录 `.env` 配置了真实 API，也可以运行真实大模型版本：

```bash
python3 examples/28-agentic-rag-agent/07_real_openai_compatible_alfred.py
```

它会读取：

```bash
OPENAI_API_KEY
OPENAI_BASE_URL
OPENAI_MODEL
```

这个脚本会真实调用你的 OpenAI-compatible 模型接口，并尝试调用真实的天气、Hugging Face Hub、DuckDuckGo Instant Answer 接口。

## 文件说明

| 文件 | 说明 |
|---|---|
| `common_alfred_tools.py` | 离线版工具和公共 Agent 逻辑 |
| `01_smolagents_end_to_end_agent.py` | smolagents 风格端到端 Alfred |
| `02_llama_index_end_to_end_agent.py` | LlamaIndex 风格端到端 Alfred |
| `03_langgraph_end_to_end_agent.py` | LangGraph 风格端到端 Alfred |
| `04_compare_end_to_end_agents.py` | 对比三种实现 |
| `05_memory_demo.py` | 多轮记忆演示 |
| `06_end_to_end_flow_map.py` | 输出 Mermaid 流程图 |
| `07_real_openai_compatible_alfred.py` | 真实 OpenAI-compatible API 版 Alfred |

## 说明

用户要求代码每行都加注释，所以 Python 文件中的每一行非空代码都带有解释性注释。
