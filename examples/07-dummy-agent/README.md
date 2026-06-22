# Day 07：Dummy Agent Library

本目录用于练习 Day 7 的核心内容：

```text
把前 6 天的 LLM、messages、Thought、Action、Observation 封装成一个最小可运行 Agent。
```

## 文件说明

```text
examples/07-dummy-agent/
├── dummy_agent.py  # 教学版 DummyAgent 类
├── tools.py        # 工具函数和工具说明
└── README.md
```

## 运行前准备

项目根目录需要有 `.env`：

```text
OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=你的中转站地址
OPENAI_MODEL=你的模型名
```

## 运行方式

在项目根目录执行：

```bash
python examples/07-dummy-agent/dummy_agent.py
```

如果你的环境使用 `python3`：

```bash
python3 examples/07-dummy-agent/dummy_agent.py
```

## 推荐测试问题

```text
3 乘以 4 等于多少？
```

```text
今天苏州天气怎么样？
```

## 知识点对应关系

| 文件/函数 | 对应知识点 |
|---|---|
| `DummyAgent.__init__()` | 初始化 Agent，保存 messages 和工具 |
| `_build_system_prompt()` | system prompt，定义身份、工具、输出格式 |
| `call_llm()` | 调用模型，使用 messages |
| `extract_action()` | Stop and Parse，解析 JSON Action |
| `run_tool()` | 根据 Action 执行工具 |
| `append_observation()` | 把 Observation 放回 messages |
| `run()` | Agent Loop：Thought -> Action -> Observation |
| `tools.py` | 工具函数，本质是普通 Python 函数 |

## 完整链路

```text
User
→ messages
→ LLM 输出 Thought + Action
→ Stop and Parse
→ run_tool()
→ Observation
→ append_observation()
→ LLM 继续
→ Final Answer
```

## 为什么叫 Dummy Agent

`Dummy Agent` 不是生产级框架。

它是一个教学版最小 Agent，用来帮助理解真正框架底层做了什么。

真正框架，例如 `smolagents`、`LangGraph`、`LlamaIndex Agents`，会提供更多能力：

```text
工具注册
状态管理
错误处理
日志追踪
多轮循环
记忆管理
权限控制
评估监控
```

但底层核心仍然是：

```text
messages
→ LLM
→ Action
→ Tool
→ Observation
→ messages
```


