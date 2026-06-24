# Day13-smolagents 检索智能体与 Agentic RAG 练习项目

这个目录对应 Hugging Face Agents Course 第 2.1 单元的 `检索智能体` 章节：

[构建智能驱动的 RAG 系统](https://huggingface.co/learn/agents-course/zh-CN/unit2/smolagents/retrieval_agents)

Day13 的重点是：

- RAG 是什么。
- observation 为什么会进入 Agent 上下文。
- 传统 RAG 和 Agentic RAG 有什么区别。
- 如何把本地知识库封装成 Agent 可调用的检索工具。
- 智能体如何自己决定检索什么、检索几次、如何综合结果。

## 第一步：安装依赖

```bash
pip install -r examples/13-smolagents-retrieval-agent-practice/requirements.txt
```

## 第二步：配置真实 API

在项目根目录创建 `.env`：

```env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=你的中转站地址，例如 https://xxx.com/v1
OPENAI_MODEL=你的模型名称
```

## 第三步：先看不调用模型的 RAG 流程

```bash
cd examples/13-smolagents-retrieval-agent-practice
python retrieval_flow_demo.py
```

这个脚本展示：

- 传统 RAG：检索一次。
- Agentic RAG：拆成多个查询，多次检索。

## 第四步：运行真实检索智能体

```bash
python first_agent.py
```

这个脚本会调用你的真实模型 API。它使用的是本地知识库作为检索数据源，
这样能稳定观察 observation 如何进入 Agent 上下文。

里面有三个练习：

1. 本地知识库检索问答。
2. Agentic RAG 多步检索。
3. 迁移到 Obsidian 和 996tokens 这类个人项目。

## 第五步：可选，运行真实网页检索示例

```bash
python duckduckgo_agent_example.py
```

这个脚本呼应课程页中的 DuckDuckGo 示例，会同时使用：

- 你的真实模型 API。
- DuckDuckGo 真实网页检索。

它需要网络，并需要安装 `ddgs` 依赖。

## 文件说明

- `knowledge_base.py`：准备模拟知识库，并实现简化检索算法。
- `tools.py`：把本地知识库检索封装成 smolagents Tool。
- `retrieval_flow_demo.py`：不调用模型，演示传统 RAG 和 Agentic RAG 的流程差异。
- `first_agent.py`：创建真实 CodeAgent，让 Agent 自己调用检索工具。
- `duckduckgo_agent_example.py`：真实 DuckDuckGo 网页搜索示例。
- `model_config.py`：读取 API 配置，创建模型对象。

## 今日核心结论

RAG 是让大模型先查资料，再基于资料回答。

Agentic RAG 是让智能体自己决定：

- 要不要查。
- 查哪里。
- 查什么关键词。
- 查几次。
- 结果够不够。
- 最后如何综合成答案。
