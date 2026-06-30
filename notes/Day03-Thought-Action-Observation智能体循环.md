---
title: Day 03｜Thought-Action-Observation 智能体循环
date: 2026-06-19
tags:
  - AI-Agent
  - Thought-Action-Observation
  - Tool-Calling
  - System-Prompt
  - Messages
  - ReAct
  - Python
  - Obsidian
status: in-progress
---

# Day 03｜Thought-Action-Observation 智能体循环

## 一、今天的学习主题

Day 3 的核心主题是：

```text
Thought → Action → Observation
思考 → 行动 → 观察
```

这是 AI Agent 最核心的工作流程。

Day 1 学的是：

```text
LLM 是什么
```

Day 2 学的是：

```text
messages 是什么，多轮对话为什么能记住上下文
```

Day 3 开始进入真正的 Agent 骨架：

```text
模型不只是回答问题，而是先判断下一步该做什么，
必要时调用工具，
拿到工具结果后再继续思考，
最后给出答案。
```

---

# 二、今天最重要的一句话

```text
Agent 不是直接回答，而是通过 Thought、Action、Observation 的循环，一步一步完成任务。
```

普通聊天机器人：

```text
用户提问
→ 模型回答
```

AI Agent：

```text
用户提问
→ 模型思考下一步
→ 模型决定是否调用工具
→ 程序执行工具
→ 工具结果返回给模型
→ 模型继续思考
→ 最终回答用户
```

这就是两者最大的区别。

---

# 三、如何在系统提示中向 Agent 提供工具

## 1. 什么叫“向智能体提供工具”

“提供工具”不是说模型自己真的拥有工具。

更准确地说，是在 `system message` 里告诉模型：

```text
你有哪些工具可以用；
每个工具叫什么名字；
工具是干什么的；
调用工具时需要哪些参数；
工具返回什么结果；
什么时候应该调用工具；
调用工具时必须输出什么格式。
```

例如：

```text
You have access to the following tools:

Tool Name: calculator
Description: Multiply two integers.
Arguments: a: int, b: int
Outputs: int
```

翻译成人话就是：

```text
你现在不是普通聊天机器人。
你有一个工具叫 calculator。
它可以做两个整数相乘。
调用它的时候，你必须提供 a 和 b 两个整数。
它会返回一个整数结果。
```

这就是“在系统提示中向 Agent 提供工具”。

---

## 2. 重点理解

模型看到工具说明后，只是知道：

```text
我可以使用这个工具。
```

但真正执行工具的不是模型，而是你的程序。

例如模型输出：

```json
{
  "action": "calculator",
  "action_input": {
    "a": 12,
    "b": 8
  }
}
```

Python 程序看到后，才真正执行：

```python
calculator(12, 8)
```

所以要记住：

```text
LLM 负责判断要不要调用工具；
Python 程序负责真正执行工具；
工具结果再返回给 LLM。
```

---

# 四、为什么 Agent 需要工具

大模型本身有几个明显短板。

## 1. 不能直接获取实时信息

例如用户问：

```text
今天纽约天气怎么样？
```

如果不调用天气 API，模型只能靠训练数据猜。

它不知道当前真实天气。

---

## 2. 不能直接操作外部系统

例如：

```text
查询数据库
读取 Excel
下载 PDF
调用银行接口
发送邮件
打开网页
操作浏览器
查询企业风险
```

这些事情模型自己做不了。

它必须通过工具完成。

---

## 3. 计算、查询、执行类任务容易出错

例如：

```text
23789 * 4567
```

模型可能算错。

但是计算器工具不会算错。

---

## 4. 工具的本质

工具的本质是：

```text
让大模型从“只会说话”，变成“可以做事”。
```

没有工具的 LLM：

```text
只能回答
```

有工具的 Agent：

```text
可以查询、计算、读取、调用、执行、反馈
```

---

# 五、工具是现成的吗，还是要自己写

两种都有。

## 1. 现成工具

很多框架或平台会提供现成工具。

例如：

```text
搜索工具
计算器工具
天气工具
网页浏览工具
文件读取工具
数据库查询工具
代码执行工具
邮件发送工具
```

后面学习 `smolagents`、`LangGraph` 这些框架时，会遇到一些封装好的工具。

---

## 2. 自己写工具

真正落地项目时，大量工具需要自己写。

例如银行 RPA 场景：

```python
def query_customer_risk(customer_name: str) -> str:
    """查询客户风险信息"""
    ...
```

```python
def read_excel(file_path: str) -> str:
    """读取 Excel 文件"""
    ...
```

```python
def query_bdc_info(cert_no: str) -> str:
    """查询不动产登记信息"""
    ...
```

这些函数都可以包装成 Agent 的工具。

所以：

```text
工具可以是现成的，也可以是你自己写的函数、API、脚本、RPA 流程。
```

你以后真正有价值的地方，就是把业务系统、RPA、数据接口封装成 Agent 可以调用的工具。

---

# 六、AI Agent 是如何推理、规划并与环境交互的系统

这句话可以拆成三层。

---

## 1. 推理

这里的推理不是玄学。

它的意思是：

```text
模型根据当前任务、历史 messages、工具说明，判断下一步该干什么。
```

例如用户问：

```text
帮我查一下测试科技有限公司有没有风险。
```

Agent 可能判断：

```text
这个问题不能直接回答。
我需要先查工商信息。
再查司法风险。
再查经营异常。
最后汇总结果。
```

这就是推理。

---

## 2. 规划

规划就是把大任务拆成小步骤。

例如：

```text
任务：分析企业风险
```

拆成：

```text
第一步：查询企业基本信息
第二步：查询司法风险
第三步：查询经营异常
第四步：查询新闻舆情
第五步：生成风险报告
```

这就是规划。

---

## 3. 与环境交互

环境就是模型外面的真实世界。

例如：

```text
网页
数据库
API
Excel
文件系统
浏览器
业务系统
RPA 页面
天气服务
搜索引擎
支付接口
企业微信
飞书
```

模型通过工具和这些环境交互。

所以这句话最接地气的理解是：

```text
AI Agent 是一个会看任务、会拆步骤、会调用外部工具、会根据工具结果继续调整的系统。
```

---

# 七、Thought / Action / Observation 的定义

Day 3 可以把这三个概念当成 Agent Loop 的核心定义。

| 名称 | 中文 | 谁负责 | 作用 |
|---|---|---|---|
| Thought | 思考 | LLM | 判断下一步做什么 |
| Action | 行动 | LLM 输出动作，程序执行 | 调用工具 |
| Observation | 观察 | 工具返回结果 | 把外部结果反馈给模型 |

---

## 1. Thought：思考

Thought 是模型判断：

```text
我现在需要什么信息？
我是否需要调用工具？
我应该调用哪个工具？
我应该传什么参数？
```

例如：

```text
用户问天气。
我无法直接知道实时天气。
我需要调用 get_weather 工具。
地点是 New York。
```

---

## 2. Action：行动

Action 是模型决定调用工具，并输出工具调用参数。

例如：

```json
{
  "action": "get_weather",
  "action_input": {
    "location": "New York"
  }
}
```

注意：

```text
Action 是模型发出的工具调用意图。
真正执行 Action 的是程序。
```

---

## 3. Observation：观察

Observation 是工具执行后的返回结果。

例如：

```text
纽约当前天气：多云，15°C，湿度60%。
```

这个结果要重新放回 `messages`。

原因是：

```text
模型只有看到 Observation，才知道工具查到了什么。
```

---

# 八、“规则和指南嵌入到系统提示中”怎么理解

这句话原文有点拗口。

可以直接理解为：

```text
system prompt 就是 Agent 的工作制度。
```

就像你安排一个新人干活，不能只说：

```text
你去干活。
```

你需要告诉他：

```text
你是谁；
你的目标是什么；
你能用哪些工具；
遇到问题怎么处理；
输出格式是什么；
什么时候调用工具；
什么时候停止；
什么时候继续；
什么时候必须人工确认。
```

对 Agent 也是一样。

---

## 图片 demo 中的 system prompt 定义了什么

图片中的 system prompt 主要定义了三件事。

---

## 1. 定义 Agent 的身份

```text
You are an AI assistant designed to help users efficiently and accurately.
```

意思是：

```text
你是一个帮助用户高效、准确完成任务的 AI 助手。
```

---

## 2. 定义 Agent 可以使用的工具

```text
Tool Name: calculator
Description: Multiply two integers.
Arguments: a: int, b: int
Outputs: int
```

意思是：

```text
你可以使用 calculator 工具。
它能做两个整数相乘。
调用时需要 a 和 b 两个整数。
返回值是整数。
```

---

## 3. 定义 Agent 的工作流程

```text
You should think step by step...
Thought/Action/Observation steps...
```

意思是：

```text
你必须按 Thought → Action → Observation 的流程工作。
```

如果需要调用工具，就输出：

```text
Action: {JSON_BLOB}
```

如果已经可以回答，就输出：

```text
Final Answer: ...
```

---

## 4. 和 Day 2 的关系

Day 2 学的是：

```python
messages = [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
]
```

Day 3 只是把 `system` 写得更复杂。

Day 2 的 system 可能是：

```text
你是一个中文学习助手。
```

Day 3 的 system 变成：

```text
你是一个 Agent。
你有这些工具。
你必须按 Thought/Action/Observation 工作。
你需要时输出 JSON 调用工具。
拿到工具结果后再回答用户。
```

所以 Day 3 不是推翻 Day 2，而是在 Day 2 的 `messages` 基础上升级。

---

# 九、图片 demo 的完整流程

假设用户问：

```text
12 乘以 8 等于多少？
```

Agent 不应该随便直接回答，而是按照系统提示走流程。

---

## 1. User

```text
User: 12 乘以 8 等于多少？
```

---

## 2. Thought

模型思考：

```text
我需要计算 12 * 8。
我可以使用 calculator 工具。
```

---

## 3. Action

模型输出：

```json
{
  "action": "calculator",
  "action_input": {
    "a": 12,
    "b": 8
  }
}
```

---

## 4. Python 执行工具

程序执行：

```python
calculator(12, 8)
```

返回：

```text
96
```

---

## 5. Observation

程序把结果放回上下文：

```text
Observation: 96
```

---

## 6. Final Answer

模型看到 Observation 后回答：

```text
Final Answer: 12 乘以 8 等于 96。
```

完整链路：

```text
User
→ Thought
→ Action
→ Python 执行工具
→ Observation
→ Final Answer
```

---

# 十、阿尔弗雷德天气智能体例子

阿尔弗雷德是一个天气 Agent。

它的任务是回答：

```text
今天纽约天气怎么样？
```

普通聊天机器人可能直接编一个答案。

但 Agent 不能瞎编，它要调用天气工具。

---

## 1. 用户提问

```text
User: 今天纽约天气怎么样？
```

这条消息进入 `messages`：

```python
{"role": "user", "content": "今天纽约天气怎么样？"}
```

---

## 2. Thought：思考

模型判断：

```text
用户问的是实时天气。
我的训练数据不一定知道当前天气。
我需要调用 get_weather 工具。
地点是 New York。
```

这就是 Thought。

---

## 3. Action：行动

模型输出工具调用指令：

```json
{
  "action": "get_weather",
  "action_input": {
    "location": "New York"
  }
}
```

注意：

```text
模型只是提出要调用工具。
真正调用工具的是 Python 程序。
```

---

## 4. Python 执行工具

程序拿到 action 后执行：

```python
get_weather("New York")
```

假设返回：

```text
纽约当前天气：多云，15°C，湿度60%。
```

---

## 5. Observation：观察

程序把工具结果放回 `messages`：

```python
{
    "role": "tool",
    "content": "纽约当前天气：多云，15°C，湿度60%。"
}
```

或者在简化版中写成：

```text
Observation: 纽约当前天气：多云，15°C，湿度60%。
```

这一步非常关键。

如果不把 Observation 放回 `messages`，模型就不知道工具查到了什么。

---

## 6. Updated Thought：更新思考

模型看到工具结果后判断：

```text
我已经拿到纽约天气了，现在可以给用户最终回答。
```

---

## 7. Final Answer：最终回答

模型输出：

```text
纽约今天多云，温度约 15°C，湿度 60%。出门建议带一件外套。
```

这就是完整 Agent 工作流。

---

# 十一、为什么 Observation 要重新放回 messages

Day 2 已经学过：

```text
模型没有永久记忆。
模型每次只能看到本次请求传进去的 messages。
```

所以工具返回结果后，必须加入上下文。

否则模型不知道工具执行结果。

完整过程是：

```text
用户问题进入 messages
→ 模型输出 Action
→ 程序执行工具
→ 工具结果作为 Observation 加入 messages
→ 再次请求模型
→ 模型基于 Observation 生成 Final Answer
```

这就是 Day 2 和 Day 3 的连接点。

---

# 十二、为什么 Agent 需要 while 循环

因为很多任务不是一次工具调用就能完成。

例如企业风险分析：

```text
查工商信息
→ 查司法风险
→ 查经营异常
→ 查舆情
→ 汇总报告
```

每一步都可能需要一个工具。

所以 Agent 的本质可以理解为：

```python
while 任务还没完成:
    模型思考下一步
    如果需要工具:
        调用工具
        把工具结果放回 messages
    否则:
        输出最终答案
        break
```

这就是 Agent Loop。

---

# 十三、用银行 RPA 场景理解 Agent

假设用户问：

```text
帮我查一下某客户的不动产抵押信息，并判断是否存在异常。
```

Agent 可以这样工作：

---

## 1. Thought

```text
我需要先查询不动产系统。
```

---

## 2. Action

```json
{
  "action": "query_bdc_info",
  "action_input": {
    "cert_no": "某产权证号"
  }
}
```

---

## 3. Observation

```text
返回抵押金额、登记时间、权利人、坐落等信息。
```

---

## 4. Updated Thought

```text
我需要判断抵押金额是否超过阈值。
```

---

## 5. Action

```json
{
  "action": "check_mortgage_amount",
  "action_input": {
    "amount": 5000000
  }
}
```

---

## 6. Observation

```text
金额超过阈值，需要人工复核。
```

---

## 7. Final Answer

```text
该客户存在一笔抵押记录，金额较高，建议人工复核。
```

这就是 Agent 对 RPA 的升级：

```text
以前 RPA 是人写死流程；
Agent 是模型根据任务和工具结果，动态决定下一步。
```

但在银行生产环境中，不能让 Agent 完全自动乱跑，必须有：

```text
权限控制
日志记录
人工复核
异常处理
敏感操作确认
```

---

# 十四、今天需要写的代码

建议目录：

```text
examples/03-agent-loop/
```

建议文件：

```text
examples/03-agent-loop/
├── fake_weather_agent.py
├── calculator_agent.py
├── manual_agent_loop.py
└── README.md
```

今天代码不追求复杂。

目标是跑通：

```text
用户输入
→ 模型判断 Action
→ Python 执行工具
→ 得到 Observation
→ Observation 放回 messages
→ 模型输出 Final Answer
```

---

# 十五、Day 3 代码核心伪代码

```python
messages = [
    {"role": "system", "content": system_prompt}
]

while True:
    user_input = input("用户：")

    messages.append({
        "role": "user",
        "content": user_input
    })

    assistant_message = call_llm(messages)

    if assistant_message contains Action:
        action = parse_action(assistant_message)
        observation = run_tool(action)

        messages.append({
            "role": "assistant",
            "content": assistant_message
        })

        messages.append({
            "role": "tool",
            "content": observation
        })

        final_answer = call_llm(messages)
        print(final_answer)

    else:
        print(assistant_message)
```

---

# 十六、Day 3 推荐执行顺序

```text
复习 Day 2 messages
→ 阅读 Thought-Action-Observation 这一节
→ 理解 system prompt 如何描述工具
→ 理解 calculator demo
→ 理解阿尔弗雷德天气 Agent
→ 手动画出 Agent Loop
→ 写 fake_weather_agent.py
→ 写 calculator_agent.py
→ 写 manual_agent_loop.py
→ 测试 Action JSON
→ 测试 Observation 回填 messages
→ 写 README
→ 写 notes/day03.md
→ git commit
→ git push
```

---

# 十七、Day 3 验收问题

今天结束前，必须能回答下面问题：

1. 为什么 Agent 需要工具？
2. 工具是模型自己执行的吗？
3. 工具是现成的还是自己写的？
4. 什么是 Thought？
5. 什么是 Action？
6. 什么是 Observation？
7. Observation 为什么要放回 `messages`？
8. 什么是 Updated Thought？
9. 什么是 Final Answer？
10. 为什么 Agent 需要 while 循环？
11. 普通聊天机器人和 Agent 最大区别是什么？
12. system prompt 在 Agent 中起什么作用？
13. 如何在 system prompt 中描述一个工具？
14. 用银行 RPA 举一个 Thought-Action-Observation 的例子。

---

# 十八、Day 3 薄弱点预警

## 1. 不要以为工具是模型自己执行的

模型只是输出：

```text
我要调用哪个工具，以及参数是什么。
```

真正执行工具的是程序。

---

## 2. 不要跳过 Observation

工具返回结果后，必须加回 `messages`。

否则模型无法基于结果继续回答。

---

## 3. 不要急着学习框架

今天先不要急着进入：

```text
smolagents
LangGraph
LlamaIndex
```

先把手写 Agent Loop 搞明白。

框架只是帮你封装流程。

但底层逻辑还是：

```text
Thought → Action → Observation
```

---

## 4. 不要让 Agent 随意执行高风险操作

涉及真实业务系统时，必须有：

```text
人工确认
权限控制
日志记录
异常处理
敏感操作拦截
```

尤其是银行、支付、征信、客户数据等场景。

---

# 十九、今日结论

Day 3 的核心不是框架，也不是复杂代码。

今天只需要彻底理解：

```text
工具是 Agent 的手和脚。
system prompt 是 Agent 的工作制度。
Thought-Action-Observation 是 Agent 做事的循环。
```

阿尔弗雷德天气 Agent 的本质不是天气。

它真正想说明的是：

```text
Agent 不应该瞎答实时问题。
它应该判断需要工具，调用工具，观察结果，再给最终答案。
```

只要你理解了这一点，就真正摸到了 AI Agent 的门。

