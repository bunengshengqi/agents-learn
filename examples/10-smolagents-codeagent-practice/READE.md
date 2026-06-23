# Day10-smolagents CodeAgent 练习项目

这个目录是第 10 天的配套代码，用来练习：

- 如何配置真实 API
- 如何创建 `CodeAgent`
- 如何准备工具菜单 `tools`
- `agent.run()` 如何启动智能体
- CodeAgent 如何通过 Python 代码调用工具
- CodeAgent 为什么比 JSON Agent 更适合多步骤任务

## 目录结构

```text
10-smolagents-codeagent-practice/
├── README.md
├── requirements.txt
├── model_config.py
├── tools.py
└── first_agent.py
```

## 第一步：安装依赖

```bash
pip install -r requirements.txt
```

## 第二步：配置真实 API

推荐使用环境变量，不要把 API Key 写死在代码里。

如果你用的是 OpenAI 官方：

```bash
export OPENAI_API_KEY="你的 API Key"
export OPENAI_MODEL="openai/gpt-4o-mini"
```

如果你用的是自己的中转站，例如 996tokens 或其他兼容 OpenAI 的 API：

```bash
export OPENAI_API_KEY="你的中转站 API Key"
export OPENAI_BASE_URL="https://你的中转站域名/v1"
export OPENAI_MODEL="openai/gpt-4o-mini"
```

注意：`OPENAI_MODEL` 的值要和你的上游/中转站支持的模型名称一致。

## 第三步：运行第一个 CodeAgent

```bash
python first_agent.py
```

## 你应该重点看哪里？

### 1. `model_config.py`

负责读取 API Key、Base URL、模型名称，然后创建 `LiteLLMModel`。

### 2. `tools.py`

这里是工具菜单。

Agent 不能凭空调用工具，你在 `tools.py` 里定义什么工具，它才能使用什么工具。

### 3. `first_agent.py`

这里创建 `CodeAgent`，然后通过：

```python
agent.run("你的任务")
```

启动智能体。

## 今日核心理解

以前 Day03-Day08 是你手写：

```text
Thought -> Action -> Observation -> Final Answer
```

现在 smolagents 帮你组织这个流程。

CodeAgent 的特点是：

```text
模型生成 Python 代码作为 Action，
框架执行代码，
代码调用工具，
最后返回 final_answer。
```


