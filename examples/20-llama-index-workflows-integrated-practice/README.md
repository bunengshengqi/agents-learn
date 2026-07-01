# Day20 LlamaIndex Workflows 综合练习

这是一套“综合练习版”代码。它不是把每个概念拆成很小的 demo，而是用 6 个脚本覆盖 Day20 的核心知识点。

适合练习：

- `Workflow`
- `@step`
- `Event`
- `StartEvent`
- `StopEvent`
- 类型提示如何驱动流程
- `Context` 状态
- 分支
- 循环
- fan-out / fan-in
- RAG
- `AgentWorkflow`

## 安装

在项目根目录运行：

```bash
.venv/bin/pip install -r examples/20-llama-index-workflows-integrated-practice/requirements.txt
```

## 练习顺序

```bash
cd /Users/yuyuan/Desktop/agents-learn/examples/20-llama-index-workflows-integrated-practice

python 01_event_pipeline.py
python 02_branch_router.py
python 03_loop_agentic_rag.py
python 04_fanout_fanin_research.py
python 05_rag_with_optional_llm.py
python 05_rag_with_optional_llm.py --use-llm
python 06_agentworkflow_state.py
```

## 文件对应知识点

| 文件 | 综合练习内容 | 覆盖知识点 |
|---|---|---|
| `01_event_pipeline.py` | 用户请求处理流水线 | Workflow、@step、Event、StartEvent、StopEvent、Context |
| `02_branch_router.py` | 客服问题路由 | 分支、多个 StopEvent、Context 记录路由 |
| `03_loop_agentic_rag.py` | 检索不足时自动改写 query | 循环、重试、终止条件、RAG 思路 |
| `04_fanout_fanin_research.py` | 同时查询多个知识源再汇总 | fan-out、fan-in、list Event |
| `05_rag_with_optional_llm.py` | 本地资料检索，可选调用 LLM 生成回答 | RAG、Context、LLM API |
| `06_agentworkflow_state.py` | Agent 调工具并记录调用次数 | AgentWorkflow、工具、Context 共享状态 |

## 哪些需要 API

默认不调用 API：

- `01_event_pipeline.py`
- `02_branch_router.py`
- `03_loop_agentic_rag.py`
- `04_fanout_fanin_research.py`
- `05_rag_with_optional_llm.py`

会调用 API：

- `05_rag_with_optional_llm.py --use-llm`
- `06_agentworkflow_state.py`

API 配置继续读项目根目录 `.env`：

```bash
OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
```

## 练习方法

建议每个脚本都按这 4 个问题去读：

1. 入口 `StartEvent` 里带了什么？
2. 中间定义了哪些自定义 `Event`？
3. 每个 `@step` 接收什么 Event，又返回什么 Event？
4. 最后哪个地方返回 `StopEvent`？

如果你能画出每个脚本的事件流，就说明 Workflow 这节真正吃进去了。
