# Day 03：Thought-Action-Observation Agent Loop

本目录用于练习 Day 3 的核心内容：

```text
Thought → Action → Observation → Final Answer
```

## 文件说明

```text
examples/03-agent-loop/
├── fake_weather_agent.py   # 不调用 API，用假天气数据理解完整流程
├── calculator_agent.py     # 模拟课程图片里的 calculator 工具
├── manual_agent_loop.py    # 使用 OpenAI 兼容 API 手写极简 Agent Loop
└── README.md
```

## 推荐运行顺序

先运行不需要 API 的脚本：

```bash
python examples/03-agent-loop/fake_weather_agent.py
```

再运行计算器工具脚本：

```bash
python examples/03-agent-loop/calculator_agent.py
```

最后运行真实模型版本：

```bash
python examples/03-agent-loop/manual_agent_loop.py
```

## manual_agent_loop.py 需要的环境变量

项目根目录需要有 `.env`：

```text
OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=你的中转站地址
OPENAI_MODEL=你的模型名
```

## 建议测试问题

```text
12 乘以 8 等于多少？
```

```text
今天苏州天气怎么样？
```

## 核心理解

模型并不会自己执行工具。

完整流程是：

```text
用户提问
→ 模型输出 Thought 和 Action
→ Python 解析 Action
→ Python 执行工具
→ 得到 Observation
→ Observation 放回 messages
→ 模型输出 Final Answer
```

## 今日验收

学完后要能解释清楚：

- Thought 是什么
- Action 是什么
- Observation 是什么
- 为什么工具结果要放回 messages
- 为什么真正执行工具的是 Python 程序
- 普通聊天机器人和 Agent 的区别


