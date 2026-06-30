---
title: Day 08 补充｜Day 7 手写 Agent 与 Day 8 smolagents 对比
date: 2026-06-21
tags:
  - AI-Agent
  - smolagents
  - Dummy-Agent
  - CodeAgent
  - Tool
  - Obsidian
status: done
---

# Day 08 补充｜Day 7 手写 Agent 与 Day 8 smolagents 对比

## 一、这两天到底在学什么

Day 7 和 Day 8 学的是同一个东西的两个层次。

```text
Day 7：自己手写一个最小 Agent，理解底层执行流程。
Day 8：使用 smolagents 框架，把这些底层流程封装起来。
```

可以这样理解：

```text
Day 7 是拆发动机。
Day 8 是开一辆已经组装好的车。
```

Day 7 的价值不是为了以后所有 Agent 都自己手写，而是为了看懂框架背后到底在做什么。

Day 8 的价值是开始使用真实框架，提高开发效率。

---

## 二、核心区别一句话

```text
Day 7 让你看懂 Agent 是怎么跑的。
Day 8 让你开始用框架快速做 Agent。
```

更具体一点：

```text
Day 7：你自己写 Agent Loop。
Day 8：smolagents 帮你管理 Agent Loop。
```

---

## 三、完整对比表

| 对比维度 | Day 7：Dummy Agent | Day 8：smolagents |
|---|---|---|
| 学习目标 | 理解 Agent 底层执行机制 | 学会用框架创建第一个 Agent |
| 核心对象 | 自己写的 `DummyAgent` 类 | 框架提供的 `CodeAgent` 类 |
| 模型调用 | 自己写 `call_llm()` | 交给 `model` 对象处理 |
| 消息管理 | 自己维护 `messages` | 框架内部维护上下文 |
| 工具说明 | 自己写进 system prompt | 框架根据工具函数自动整理 |
| 工具调用 | 模型输出 JSON，程序解析 JSON | CodeAgent 生成并执行 Python 代码 |
| Action 表达形式 | JSON Action | Code Action |
| Observation | 自己 append 到 messages | 框架把执行结果写回上下文 |
| 循环控制 | 自己写 `for step in range(max_steps)` | 设置 `max_steps` |
| 终止条件 | 自己判断是否出现 Final Answer | 框架处理最终答案 |
| 适合阶段 | 学原理、打基础 | 做项目、快速实验 |

---

## 四、从执行链路上比较

### Day 7 的执行链路

Day 7 中，Agent 的每一步都要自己写。

```text
用户问题
→ 放入 messages
→ 调用 LLM
→ LLM 输出 Thought + Action
→ 程序解析 Action JSON
→ 程序执行工具
→ 得到 Observation
→ 把 Observation 放回 messages
→ 再次调用 LLM
→ 输出 Final Answer
```

对应代码大概是：

```python
messages.append({"role": "user", "content": question})

assistant_output = call_llm(messages)
messages.append({"role": "assistant", "content": assistant_output})

action = extract_action(assistant_output)
observation = run_tool(action)

messages.append({
    "role": "user",
    "content": f"Observation: {observation}"
})

final_answer = call_llm(messages)
```

这里所有关键步骤都暴露在你面前。

所以 Day 7 的重点是：

```text
你要亲眼看到 Agent Loop 是怎么循环起来的。
```

---

### Day 8 的执行链路

Day 8 使用 smolagents 后，很多步骤被框架接管。

你主要写：

```python
agent = CodeAgent(
    model=model,
    tools=[get_current_time_in_timezone],
    max_steps=6,
)

result = agent.run("现在 Asia/Shanghai 是几点？")
print(result)
```

框架内部大致做了这些事情：

```text
接收用户问题
→ 组织 prompt
→ 把可用工具说明给模型
→ 模型决定下一步 Action
→ 生成可执行代码
→ 执行代码
→ 得到 Observation
→ 把结果放回上下文
→ 继续循环
→ 输出最终答案
```

Day 8 表面上代码少了，但底层仍然是：

```text
Thought → Action → Observation → Final Answer
```

只是这些流程被框架封装起来了。

---

## 五、为什么 Day 7 必须先学

如果直接学 Day 8，很容易只会复制代码：

```python
agent = CodeAgent(...)
agent.run(...)
```

但是不知道里面发生了什么。

Day 7 先手写一遍后，你就能看懂：

| Day 7 概念 | Day 8 框架中的对应 |
|---|---|
| system prompt | 框架自动生成或加载 prompt template |
| tools 描述 | `tools=[...]` |
| Action JSON | CodeAgent 生成的 Python 代码 |
| run_tool() | 框架执行工具函数 |
| Observation | 工具返回值进入上下文 |
| max_steps 循环 | `max_steps=6` |
| Final Answer | 最终返回结果 |

所以 Day 7 是理解框架的基础。

---

## 六、为什么 Day 8 要用框架

如果真实项目全部手写 Agent，会遇到很多工程问题：

- prompt 组织容易乱；
- 工具描述容易写错；
- JSON 解析容易失败；
- 工具执行异常要自己处理；
- 上下文越来越长要自己管理；
- 每一步日志要自己记录；
- 多工具、多轮循环很快变复杂；
- UI、部署、调试都要自己做。

smolagents 的意义是：

```text
把 Agent 的通用流程封装起来，让你把注意力放到模型和工具能力上。
```

也就是：

```text
你不再每次都重复造 Agent Loop。
你只需要定义模型、工具和任务。
```

---

## 七、JSON Agent 和 CodeAgent 的区别

Day 7 更接近 JSON Agent。

模型输出：

```json
{
  "action": "get_weather",
  "action_input": {
    "location": "London"
  }
}
```

程序负责解析 JSON，然后调用工具。

Day 8 的 `CodeAgent` 更接近 Code Agent。

模型可能生成类似代码：

```python
time = get_current_time_in_timezone("Asia/Shanghai")
final_answer(time)
```

框架执行这段代码，拿到结果。

两者的区别：

| 类型 | 优点 | 缺点 |
|---|---|---|
| JSON Agent | 结构清晰、安全边界更容易控制 | 表达复杂逻辑比较麻烦 |
| CodeAgent | 表达能力强，适合循环、条件、计算、多步骤任务 | 执行代码有安全风险，需要限制环境 |

---

## 八、怎么真正看出 Day 7 和 Day 8 的差别

最好的办法是用同一个任务分别实现一遍。

### 任务一：计算 3 乘以 4

Day 7 的做法：

```text
模型输出 JSON Action
→ 程序解析 calculator
→ 执行 calculator(a=3, b=4)
→ Observation: 12
→ 模型输出 Final Answer
```

Day 8 的做法：

```text
给 CodeAgent 一个计算工具
→ Agent 自己生成代码调用工具
→ 框架执行
→ 返回答案
```

这个任务很简单，主要用来看清楚流程差异。

---

### 任务二：查询当前时区时间

Day 7 的做法：

```text
手写工具描述
→ 模型输出：
{
  "action": "get_current_time_in_timezone",
  "action_input": {"timezone": "Asia/Shanghai"}
}
→ 程序解析 JSON
→ 执行工具
→ Observation 放回 messages
→ 模型回答
```

Day 8 的做法：

```python
@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """Fetch the current local time in a specified timezone.
    Args:
        timezone: A valid timezone name, e.g. 'Asia/Shanghai'.
    """
    ...
```

然后：

```python
agent.run("现在 Asia/Shanghai 是几点？")
```

框架会根据函数名、类型标注和 docstring，把工具能力提供给 Agent。

---

## 九、工程上的意义

Day 7 的工程意义：

```text
你能自己排查 Agent 为什么不调用工具、为什么 JSON 解析失败、为什么 Observation 没进入上下文。
```

它解决的是“看懂底层”的问题。

Day 8 的工程意义：

```text
你可以开始把 Agent 用到真实业务里，而不是每次从零写循环。
```

它解决的是“提高开发效率”的问题。

对于你的实际项目，可以这样映射：

| 项目场景 | Day 7 价值 | Day 8 价值 |
|---|---|---|
| 闲鱼 Agent | 看懂客服/选品/定价工具怎么被调用 | 快速把选品、利润、文案工具挂进去 |
| 银行 RPA Agent | 看懂工具执行结果如何回到上下文 | 把查询、核验、报告生成封装成工具 |
| 视频 SOP Agent | 看懂总结结果如何进入下一轮任务 | 把转写、摘要、提纲、SOP 生成作为工具 |
| 996tokens 运维 Agent | 看懂状态查询和错误反馈怎么循环 | 把余额、模型状态、价格查询封装为工具 |

---

## 十、这两天应该形成的认知

学完 Day 7，你应该能回答：

```text
一个 Agent 不神秘。
它就是：
LLM 生成下一步动作
→ 程序执行动作
→ 把执行结果放回上下文
→ LLM 再继续判断
```

学完 Day 8，你应该能回答：

```text
框架不是替代 Agent 原理。
框架是把 Agent 原理封装成更好用的开发接口。
```

所以不要把 smolagents 当成黑盒魔法。

它本质上仍然是在做：

```text
Prompt 组织
→ 工具注册
→ 动作生成
→ 动作执行
→ 观察回填
→ 多步循环
→ 最终回答
```

---

## 十一、最终结论

```text
Day 7 是 Agent 的底层手工版。
Day 8 是 Agent 的框架封装版。
```

Day 7 学的是：

```text
Agent 为什么能工作。
```

Day 8 学的是：

```text
如何用框架更快地构建 Agent。
```

如果以后代码出问题，先用 Day 7 的视角排查：

- 模型有没有收到正确的工具说明？
- 模型有没有输出正确的 Action？
- 程序有没有成功解析 Action？
- 工具有没有真实执行？
- Observation 有没有放回上下文？
- Agent 有没有根据 Observation 继续调整？

如果要快速做业务 Demo，就用 Day 8 的方式：

- 选模型；
- 写工具；
- 注册工具；
- 创建 Agent；
- 设置最大步骤；
- 运行任务；
- 查看日志。

这就是从“理解 Agent”走向“使用 Agent 框架”的关键一步。

