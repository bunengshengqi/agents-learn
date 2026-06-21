# Day 06：Observation 整合反馈与反思调整

本目录用于练习 Day 6 的核心内容：

```text
Observation 是工具执行后的现实反馈。
Observation 必须放回 messages，模型才能根据真实结果继续思考。
```

## 文件说明

```text
examples/06-observations/
├── observation_success_failure.py  # 演示成功/失败 Observation 如何进入 messages
├── observation_loop_demo.py        # 演示工具失败后根据 Observation 切换策略
└── README.md
```

## 运行方式

```bash
python examples/06-observations/observation_success_failure.py
```

```bash
python examples/06-observations/observation_loop_demo.py
```

如果你的环境使用 `python3`：

```bash
python3 examples/06-observations/observation_success_failure.py
python3 examples/06-observations/observation_loop_demo.py
```

## 核心理解

完整链路：

```text
Thought
→ Action
→ Execute
→ Observation
→ Append to messages
→ Updated Thought
→ Next Action 或 Final Answer
```

## Observation 的三种状态

```text
success：工具成功返回完整数据
error：工具失败，例如超时、权限错误、参数错误
partial_success：部分成功，例如查到数据但缺少关键字段
```

## 工程重点

- Observation 不是 Final Answer。
- Observation 是工具返回的原始结果。
- Final Answer 是模型整理后给用户的答案。
- Observation 最好结构化，包含 status、tool、message、retryable 等字段。
- 错误可以重试，但必须有次数限制。
- Action + Observation 是 Agent 的操作日志，适合审计。

## 今日验收

学完后要能解释：

- Observation 是什么
- Observation 为什么要放回 messages
- Observation 和 Final Answer 的区别
- 工具失败后为什么要 Updated Thought
- 什么错误可以自动重试
- 什么错误应该交给人工处理


