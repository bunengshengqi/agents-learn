# 第20天：LlamaIndex Workflows 配套练习代码

这组代码对应 Hugging Face Agents Course 的 LlamaIndex Workflows 章节，以及本地笔记：

`notes/Day20_LlamaIndex_Workflows.md`

核心目标：

- 理解 `Workflow / @step / Event / StartEvent / StopEvent / Context`
- 会写最小工作流、多步骤工作流、分支、循环、状态、fan-out/fan-in
- 把 Workflow 思想用于一个简化 RAG 流程
- 看懂 `AgentWorkflow` 如何和状态结合

## 安装

在项目根目录或本目录都可以：

```bash
pip install -r examples/20-llama-index-workflows-deepseek-final/requirements.txt
```

如果你使用项目里的 `.venv`：

```bash
.venv/bin/pip install -r examples/20-llama-index-workflows-deepseek-final/requirements.txt
```

## API 配置

只有 `07_rag_workflow_with_llm.py` 默认会调用 LLM，`08_agent_workflow_state_demo.py` 一定会调用 LLM。

继续使用项目根目录 `.env`：

```bash
OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
```

也兼容：

```bash
DEEPSEEK_API_KEY=你的 key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

## 练习顺序

```bash
cd examples/20-llama-index-workflows-deepseek-final

python 00_workflow_map.py
python 01_minimal_workflow.py
python 02_multi_step_events.py
python 03_branch_workflow.py
python 04_loop_workflow.py
python 05_context_state_workflow.py
python 06_fan_out_fan_in_workflow.py
python 07_rag_workflow_with_llm.py --no-llm
python 07_rag_workflow_with_llm.py
python 08_agent_workflow_state_demo.py
python 09_visualize_workflow_optional.py
```

## 每个文件练什么

| 文件 | 重点 |
|---|---|
| `00_workflow_map.py` | 先把核心概念和练习路线跑一遍 |
| `01_minimal_workflow.py` | 最小可运行 Workflow |
| `02_multi_step_events.py` | Step 之间通过自定义 Event 传递数据 |
| `03_branch_workflow.py` | 根据条件返回不同 Event，形成分支 |
| `04_loop_workflow.py` | 返回同类 Event，形成循环和重试 |
| `05_context_state_workflow.py` | 用 `ctx.store` 在多个 Step 之间共享状态 |
| `06_fan_out_fan_in_workflow.py` | 一个任务拆成多个子任务，再统一汇总 |
| `07_rag_workflow_with_llm.py` | 本地资料检索 + 可选 LLM 生成，一个简化 RAG Workflow |
| `08_agent_workflow_state_demo.py` | Day19 的 AgentWorkflow + Day20 的 Context 状态 |
| `09_visualize_workflow_optional.py` | 可选：安装额外包后生成 workflow 图 |

## 学习抓手

写 Workflow 时先问 4 个问题：

1. 入口参数是什么？放进 `StartEvent`。
2. 中间要拆成几个步骤？每个步骤写成一个 `@step`。
3. 每个步骤之间传什么数据？定义成自定义 `Event`。
4. 什么时候结束？返回 `StopEvent(result=...)`。

一句话记忆：

`Workflow` 不是把函数顺序写死，而是用 `Event` 把步骤串起来。这样分支、循环、并发、状态和多智能体协作都会更清楚。
