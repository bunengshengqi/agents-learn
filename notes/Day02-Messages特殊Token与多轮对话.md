---
title: Day 02｜Messages、特殊 Token 与多轮对话
date: 2026-06-19
tags:
  - AI-Agent
  - LLM
  - Messages
  - System-Prompt
  - 多轮对话
  - Chat-Template
  - Python
  - Obsidian
status: in-progress
---

# Day 02｜Messages、特殊 Token 与多轮对话

## 一、今天的学习主题

Day 2 的核心主题是：

```text
Messages、多轮对话与上下文记忆
```

对应 Hugging Face AI Agents Course Unit 1 中的这一节：

```text
消息和特殊 Tokens（Messages and Special Tokens）
```

今天不急着学习 Tool Calling，也不急着进入 ReAct 或 Agent Loop。

今天要先搞懂一个底层问题：

> 为什么模型在多轮对话中好像能“记住”前面说过的话？

---

# 二、今天最重要的一句话

```text
模型不是自己长期记住了你说过什么，而是程序把历史 messages 保存下来，并在下一次请求时重新发送给模型。
```

这句话是 Day 2 的核心。

Day 1 的程序是：

```text
用户输入一次
→ 模型回答一次
→ 程序结束
```

Day 2 要升级为：

```text
用户连续输入
→ 程序保存历史 messages
→ 每次请求都带上历史上下文
→ 模型基于上下文继续回答
→ 输入 exit 后退出
```

---

# 三、Messages 是什么

## 1. Messages 的基本结构

在大模型聊天 API 中，`messages` 通常是一个列表。

每一条消息一般包含两个字段：

```text
role：这句话是谁说的
content：这句话的具体内容
```

示例：

```python
messages = [
    {
        "role": "system",
        "content": "你是一名 AI Agent 学习助手。"
    },
    {
        "role": "user",
        "content": "什么是 AI Agent？"
    },
    {
        "role": "assistant",
        "content": "AI Agent 是一种可以理解目标、调用工具并完成任务的智能系统。"
    }
]
```

可以把 `messages` 理解成：

> 一份对话记录本。

---

# 四、常见的 role

## 1. system

`system` 是系统消息。

它不是用户的问题，而是开发者给模型设置的身份、规则和行为边界。

例如：

```python
{
    "role": "system",
    "content": "你是一名严谨的 AI Agent 学习助手，请用中文、一步一步解释。"
}
```

可以理解为：

```text
给模型安排岗位职责
```

以后做 Agent 时，`system` 里通常会写：

- 你是谁；
- 你的任务是什么；
- 你有哪些限制；
- 什么时候必须拒绝；
- 输出格式是什么；
- 可以调用哪些工具；
- 遇到不确定信息怎么处理；
- 哪些操作必须人工确认。

例如未来的银行风险 Agent：

```python
system_message = {
    "role": "system",
    "content": """
你是一名银行企业风险分析助手。
你只能基于工具返回的数据和制度文档回答。
如果信息不足，必须说明无法判断。
涉及高风险结论时，必须提示人工复核。
"""
}
```

核心理解：

> system 是 Agent 的“岗位说明书 + 行为约束”。

---

## 2. user

`user` 是用户输入的问题或任务。

例如：

```python
{
    "role": "user",
    "content": "查询测试科技有限公司的风险情况。"
}
```

在 Day 2 的代码里，每次用户在终端输入一句话，程序就应该把它保存进 `messages`：

```python
messages.append({
    "role": "user",
    "content": user_input
})
```

核心理解：

> user 表示用户当前想让模型做什么。

---

## 3. assistant

`assistant` 是模型之前生成的回答。

例如：

```python
{
    "role": "assistant",
    "content": "测试科技有限公司目前存在 2 条司法风险记录，建议人工复核。"
}
```

在 Day 2 的代码里，模型每回答一次，也要把回答保存进 `messages`：

```python
messages.append({
    "role": "assistant",
    "content": answer
})
```

为什么要保存 assistant？

因为用户下一轮可能会追问：

```text
那它和普通聊天机器人有什么区别？
```

如果程序没有保存上一轮模型回答，模型就不知道“它”指的是什么。

核心理解：

> assistant 是模型自己之前说过的话，也属于上下文的一部分。

---

## 4. tool

`tool` 是工具返回给模型的结果。

Day 2 暂时不练 `tool`，但需要提前知道它的存在。

后面 Day 3、Day 4 做 Tool Calling 时会用到。

例如：

```python
{
    "role": "tool",
    "content": "查询结果：该企业存在 2 条司法风险记录。"
}
```

核心理解：

> tool 是外部工具执行后的结果，用来告诉模型真实世界发生了什么。

---

# 五、多轮对话的本质

很多人以为：

```text
模型自己记住了前面聊天内容
```

这是不准确的。

更准确的说法是：

```text
程序保存历史 messages
→ 每次请求时重新发送给模型
→ 模型基于完整上下文生成新回答
```

例如第一轮：

```text
用户：我叫鲁迪。
助手：好的，我记住了，你叫鲁迪。
```

程序保存：

```python
messages = [
    {"role": "system", "content": "你是一名 AI Agent 学习助手。"},
    {"role": "user", "content": "我叫鲁迪。"},
    {"role": "assistant", "content": "好的，我记住了，你叫鲁迪。"}
]
```

第二轮用户问：

```text
我叫什么名字？
```

程序真正发给模型的是：

```python
messages = [
    {"role": "system", "content": "你是一名 AI Agent 学习助手。"},
    {"role": "user", "content": "我叫鲁迪。"},
    {"role": "assistant", "content": "好的，我记住了，你叫鲁迪。"},
    {"role": "user", "content": "我叫什么名字？"}
]
```

所以模型能回答：

```text
你叫鲁迪。
```

不是因为模型永久记住了你，而是因为这次请求中包含了历史消息。

---

# 六、Chat Template 是什么

你在代码里写的是结构化 messages：

```python
messages = [
    {"role": "system", "content": "你是助手"},
    {"role": "user", "content": "你好"}
]
```

但模型底层真正接收的不是 Python 列表，而是经过聊天模板转换后的 prompt。

大致类似：

```text
<|im_start|>system
你是助手<|im_end|>
<|im_start|>user
你好<|im_end|>
<|im_start|>assistant
```

不同模型可能使用不同格式。

你不需要死记这些特殊符号。

需要理解的是：

> Chat Template 的作用，是把标准 messages 转换成具体模型能理解的 prompt 格式。

---

# 七、特殊 Token 是什么

特殊 Token 是模型用来识别结构的标记。

普通文本是内容，例如：

```text
你好，我想学习 Agent。
```

特殊 Token 是结构标记，例如：

```text
<|im_start|>
<|im_end|>
<|eot_id|>
<|assistant|>
<|user|>
```

它们的作用是告诉模型：

```text
这里是 system
这里是 user
这里是 assistant
这一轮结束了
现在该 assistant 继续生成了
```

作为应用开发者，通常不用手写特殊 Token。

使用 OpenAI 兼容 API 时，只需要传标准 messages：

```python
client.chat.completions.create(
    model=model,
    messages=messages,
)
```

API 服务端会负责处理聊天模板和特殊 Token。

---

# 八、Base Model 与 Instruct Model

## 1. Base Model

Base Model 是基础语言模型。

它主要擅长：

```text
续写文本
预测下一个 token
```

例如输入：

```text
春眠不觉晓
```

它可能继续生成：

```text
处处闻啼鸟
```

但让它严格按照指令输出 JSON、调用工具、遵守格式，它不一定稳定。

---

## 2. Instruct Model

Instruct Model 是经过指令微调的模型。

它更适合：

- 回答问题；
- 遵循指令；
- 多轮对话；
- 按格式输出；
- 执行任务；
- Tool Calling；
- Agent 场景。

以后做 Agent，应优先选择：

```text
chat / instruct / tool-calling 支持较好的模型
```

不要直接拿 Base Model 做 Agent 应用。

---

# 九、Messages to Prompt

在 Hugging Face Transformers 中，有时需要手动调用：

```python
tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
```

它的作用是：

```text
messages
→ chat template
→ prompt
→ 模型输入
```

但当前学习阶段使用 OpenAI 兼容 API，不需要自己调用 `apply_chat_template()`。

现在代码只需要：

```python
response = client.chat.completions.create(
    model=model,
    messages=messages,
)
```

背后流程是：

```text
messages
→ API 服务端套用 chat template
→ 转成模型 prompt
→ 模型生成 assistant 回复
```

---

# 十、这一节和代码的对应关系

## 1. system message

课程概念对应代码：

```python
messages = [
    {
        "role": "system",
        "content": "你是一名 AI Agent 学习助手。"
    }
]
```

## 2. user message

课程概念对应代码：

```python
messages.append({
    "role": "user",
    "content": user_input
})
```

## 3. assistant message

课程概念对应代码：

```python
messages.append({
    "role": "assistant",
    "content": answer
})
```

## 4. conversation history

课程概念对应代码：

```python
messages
```

整个列表就是对话历史。

## 5. messages to prompt

课程概念对应代码：

```python
response = client.chat.completions.create(
    model=model,
    messages=messages,
)
```

你把 messages 交给 API，API 后端负责转成模型能处理的 prompt。

---

# 十一、今天最容易混淆的地方

## 混淆一：模型真的记住了我？

不准确。

正确理解：

```text
程序保存了历史 messages，并在下一次请求时重新发给模型，所以模型表现得像记住了。
```

## 混淆二：messages 就是 prompt 吗？

不完全是。

你写的是结构化 messages：

```python
[
    {"role": "user", "content": "你好"}
]
```

模型实际接收的是聊天模板转出来的 prompt。

在 API 层通常只需要关心 messages。

## 混淆三：system 是不是用户说的话？

不是。

system 是开发者给模型的行为规则。

user 才是用户输入。

## 混淆四：assistant 要不要保存？

要保存。

否则下一轮模型不知道自己上一轮回答了什么，追问时上下文会断。

## 混淆五：messages 可以无限保存吗？

不建议。

因为：

```text
messages 越长
→ token 越多
→ 成本越高
→ 响应越慢
→ 超过上下文窗口后可能报错或被截断
```

所以 Day 2 需要练习限制历史长度。

---

# 十二、Day 2 代码练习目标

## 今日代码目录

在仓库根目录创建：

```text
examples/02-messages/
```

建议包含：

```text
examples/02-messages/
├── single_turn.py
├── multi_turn.py
└── README.md
```

---

## 练习一：single_turn.py

目标：

> 复习 Day 1 的单轮问答，但改成显式 messages 结构。

要点：

- 创建 messages；
- 包含 system；
- 包含 user；
- 调用模型；
- 输出 assistant 回答。

练习结果：

```text
用户输入一次
→ 模型回答一次
→ 程序结束
```

---

## 练习二：multi_turn.py

目标：

> 实现真正的多轮对话。

要求：

1. 程序启动时创建 system message；
2. 使用 while True 支持连续输入；
3. 输入 `exit` / `quit` / `q` 时退出；
4. 每次用户输入后，将内容 append 到 messages；
5. 调用模型；
6. 将模型回答 append 到 messages；
7. 打印当前 messages 数量；
8. 限制历史对话长度。

核心代码逻辑：

```python
messages = [
    {"role": "system", "content": "你是一名 AI Agent 学习助手。"}
]

while True:
    user_input = input("用户：").strip()

    if user_input.lower() in {"exit", "quit", "q"}:
        break

    messages.append({
        "role": "user",
        "content": user_input
    })

    answer = call_llm(messages)

    messages.append({
        "role": "assistant",
        "content": answer
    })

    print(answer)
```

---

## 练习三：测试上下文记忆

### 测试 1：名字记忆

输入：

```text
我叫鲁迪。
```

再输入：

```text
我叫什么名字？
```

预期：

```text
你叫鲁迪。
```

---

### 测试 2：职业记忆

输入：

```text
我在银行做 RPA 自动化开发。
```

再输入：

```text
我的工作是什么？
```

预期：

```text
你在银行做 RPA 自动化开发。
```

---

### 测试 3：连续追问

输入：

```text
什么是 AI Agent？
```

继续输入：

```text
那它和普通大模型有什么区别？
```

继续输入：

```text
用我银行 RPA 的经历举个例子。
```

预期：

模型能基于前文解释，而不是每一轮都像全新的问题。

---

## 练习四：限制 messages 长度

需要实现一个函数：

```python
def trim_messages(messages: list[dict[str, str]], max_rounds: int = 5) -> list[dict[str, str]]:
    ...
```

目标：

- 保留 system message；
- 只保留最近几轮 user / assistant 历史；
- 避免 messages 无限增长。

原因：

- 降低 token 成本；
- 避免上下文过长；
- 避免响应变慢；
- 为后续 Agent Memory 做准备。

---

## 练习五：System Prompt 对比

创建两个不同的 system prompt：

### Prompt A：严谨技术老师

```text
你是一名严谨的技术老师，请用结构化、准确、适合初学者的方式回答。
```

### Prompt B：幽默脱口秀演员

```text
你是一名幽默的脱口秀演员，请用轻松、风趣的方式解释技术概念。
```

对同一个问题提问：

```text
什么是 AI Agent？
```

观察回答差异。

目标：

> 理解 system prompt 如何影响模型的身份、语气和输出风格。

---

# 十三、Day 2 代码验收标准

今天结束前，代码必须达到以下标准：

- [ ] 创建 `examples/02-messages/`
- [ ] 完成 `single_turn.py`
- [ ] 完成 `multi_turn.py`
- [ ] 使用 `messages` 保存对话历史
- [ ] 支持连续输入
- [ ] 支持 `exit` 退出
- [ ] 每轮追加 user message
- [ ] 每轮追加 assistant message
- [ ] 能正确回答“我叫什么名字”
- [ ] 能正确回答“我的工作是什么”
- [ ] 能完成连续追问
- [ ] 能限制 messages 历史长度
- [ ] 能对比不同 system prompt 的效果
- [ ] 完成 `examples/02-messages/README.md`
- [ ] 完成 `notes/day02.md`
- [ ] 提交 GitHub

---

# 十四、Day 2 验收问题

今天结束时，必须能回答下面问题：

1. `system` 是什么？
2. `user` 是什么？
3. `assistant` 是什么？
4. `messages` 是什么？
5. 为什么模型能回答“我叫什么名字”？
6. 模型是真的永久记住了吗？
7. Chat Template 是什么？
8. 特殊 Token 是什么？
9. Base Model 和 Instruct Model 有什么区别？
10. 为什么不能无限保存全部 messages？
11. 为什么每轮都要把历史 messages 重新发给模型？
12. 多轮对话和后面的 Agent Loop 有什么关系？

---

# 十五、Day 2 薄弱点预警

根据 Day 1 暴露的问题，Day 2 需要特别注意：

## 1. 不要只复制代码

要重点理解：

```python
messages.append(...)
```

每一次 append 都代表“把这句话加入上下文”。

## 2. 不要误以为模型有永久记忆

只要程序关闭，内存中的 messages 就会消失。

如果要长期保存，需要后面学习：

- 文件保存；
- 数据库；
- Memory；
- Checkpoint；
- 向量库。

## 3. 不要无限追加 messages

无限追加会导致：

- token 变多；
- 成本变高；
- 速度变慢；
- 超过上下文窗口；
- 历史信息干扰当前任务。

## 4. 注意运行路径

建议在仓库根目录运行：

```bash
python examples/02-messages/multi_turn.py
```

因为 `.env` 位于仓库根目录。

## 5. 注意 API 调用次数

多轮对话每输入一次，都会调用一次 API。

测试时不要无限闲聊，要围绕今天的测试目标进行。

---

# 十六、Day 2 推荐执行顺序

```text
复习 Day 1
→ 阅读 Hugging Face “消息和特殊 Tokens”
→ 创建 examples/02-messages
→ 编写 single_turn.py
→ 编写 multi_turn.py
→ 测试名字记忆
→ 测试职业记忆
→ 测试连续追问
→ 测试 system prompt 对比
→ 写 README
→ 写 notes/day02.md
→ git commit
→ git push
```

---

# 十七、Day 2 与后续 Agent 的关系

Day 2 学的是 Agent 的底层消息系统。

后面做 Tool Calling 时，messages 会变成：

```text
system
user
assistant
tool
assistant
```

后面做 Agent Loop 时，本质就是：

```text
模型生成下一步
→ 程序执行动作
→ 把动作结果写回 messages
→ 模型继续生成下一步
```

所以 Day 2 不是简单聊天练习，而是在为后面的 Agent Loop 打基础。

---

# 十八、今日结论

Day 2 的核心不是写复杂代码，而是彻底理解：

```text
Messages 是大模型对话的底层结构。
多轮对话不是模型天然记忆，而是程序保存并重新发送历史上下文。
Chat Template 负责把 messages 转换成模型真正能理解的 prompt。
System Prompt 决定模型的身份和行为边界。
```

只要能理解并写出多轮对话程序，就为 Day 3 的 Tool Calling 打好了基础。
