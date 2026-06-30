# 第19天：LlamaIndex Agents 与 AgentWorkflow 代码

对应课程：

https://huggingface.co/learn/agents-course/zh-CN/unit2/llama-index/agents

## 1. 这一节代码对应什么内容？

第19天是在第18天工具系统之后继续往上走：

```text
第17天：QueryEngine 实现 RAG
第18天：QueryEngineTool / FunctionTool 把能力包装成工具
第19天：AgentWorkflow 让智能体选择和调用工具
```

本目录包含：

| 文件 | 作用 |
|---|---|
| `00_agent_workflow_map.py` | 不调用 API，解释 Day17/18/19 的关系 |
| `01_basic_agent_workflow.py` | 基础 AgentWorkflow + FunctionTool 示例 |
| `02_context_memory_demo.py` | Context 多轮记忆示例 |
| `03_query_engine_tool_agent.py` | QueryEngineTool 创建 Agentic RAG 智能体 |
| `04_multi_agent_workflow.py` | calculator + info_lookup 多智能体 workflow |
| `rag_tools.py` | 构建本地资料 QueryEngineTool |
| `model_config.py` | DeepSeek / OpenAI-compatible LLM 配置 |
| `data/alfred_persona_notes.md` | 本地 RAG 资料 |

## 2. 安装依赖

如果已经安装过 Day16 依赖，大概率已经够用。

```bash
cd /Users/yuyuan/Desktop/agents-learn
.venv/bin/pip install -r examples/19-llama-index-agents-deepseek-final/requirements.txt
```

## 3. 配置 `.env`

继续使用项目根目录的 `.env`：

```bash
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
```

也兼容：

```bash
DEEPSEEK_API_KEY=你的 API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

## 4. 运行顺序

```bash
cd /Users/yuyuan/Desktop/agents-learn/examples/19-llama-index-agents-deepseek-final

python 00_agent_workflow_map.py
python 01_basic_agent_workflow.py
python 02_context_memory_demo.py
python 03_query_engine_tool_agent.py
python 04_multi_agent_workflow.py
```

## 5. 为什么这里用 ReActAgent？

课程里提到两类常见智能体：

```text
FunctionAgent：适合支持 function calling / tool calling API 的模型。
ReActAgent：适合任何具备聊天或文本完成能力的模型。
```

你当前使用 DeepSeek / OpenAI-compatible API。为了更稳，这份代码默认：

```python
build_llm(function_calling=False)
```

这样 `AgentWorkflow.from_tools_or_functions(...)` 会选择 ReActAgent。

如果你确认所用模型和 API 支持函数调用，可以改成：

```python
build_llm(function_calling=True)
```

## 6. 为什么这里用 SummaryIndex？

课程 Notebook 里展示的是向量索引版本，常见写法是：

```python
query_engine = index.as_query_engine(llm=llm, similarity_top_k=3)
```

这通常对应 `VectorStoreIndex`，需要 embedding 模型。

为了让第19天代码更容易在你本地跑起来，本目录使用 `SummaryIndex`：

```text
优点：不需要额外 embedding 依赖
缺点：不适合大规模知识库
```

等你要做正式 Obsidian 笔记助手时，可以再升级到：

```text
VectorStoreIndex + Embedding + Chroma/Qdrant
```

## 7. 今日核心结论

```text
FunctionTool = 普通函数变工具
QueryEngineTool = RAG 查询引擎变工具
AgentWorkflow = 让 Agent 选择和调用工具
Context = 保存多轮状态
Multi-Agent = 多个职责清晰的 Agent 通过 workflow 协作
```

