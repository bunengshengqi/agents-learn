---
title: Day 06｜Observation：整合反馈与反思调整
date: 2026-06-21
tags:
  - AI-Agent
  - Observation
  - Messages
  - Tool-Calling
  - Agent-Loop
  - Error-Handling
  - Obsidian
status: in-progress
---

# Day 06｜Observation：整合反馈与反思调整

## 一、今天的学习主题

Day 6 的核心主题是：

```text
Observation：观察，整合反馈以及反思和调整
```

前几天的关系是：

```text
Day 3：完整看 Thought → Action → Observation
Day 4：深入学 Thought，智能体怎么想
Day 5：深入学 Action，智能体怎么行动
Day 6：深入学 Observation，智能体怎么接收结果、反思和调整
```

Day 6 是 Agent Loop 的第三块：

```text
Thought → Action → Observation
```

也就是：

```text
模型想完以后去行动；
行动执行完以后，必须把真实结果带回来；
模型再根据真实结果决定下一步。
```

---

# 二、今天最重要的一句话

```text
Observation 是 Agent 的现实反馈。
```

没有 Observation，Agent 就是在自说自话。

有了 Observation，Agent 才能根据真实结果调整下一步。

完整闭环是：

```text
Thought
→ Action
→ Stop and Parse
→ Execute
→ Observation
→ Append to messages
→ Updated Thought
→ Next Action 或 Final Answer
```

---

# 三、Observation 是什么

Observation 是智能体感知其行动结果的方式。

更具体地说：

```text
Observation = 工具、API、系统、页面、文件、数据库返回给 Agent 的执行结果。
```

它可以是：

```text
API 返回的数据
错误信息
状态码
数据库查询结果
文件读取结果
浏览器页面内容
RPA 执行日志
系统日志
计算输出
定时任务完成通知
```

例如：

```text
Action: get_weather("苏州")
Observation: 苏州晴，28°C，湿度55%
```

---

# 四、Observation 是不是要放到 messages 里

是的，必须放。

Day 6 最关键的一句话：

```text
Observation 必须重新放回 messages，模型才知道工具真实执行结果。
```

因为模型本身不知道工具执行成功还是失败。

例如模型输出：

```json
{
  "action": "get_weather",
  "action_input": {
    "city": "苏州"
  }
}
```

Python 执行：

```python
get_weather("苏州")
```

返回：

```text
苏州晴，28°C，湿度55%
```

如果这个结果不放回 `messages`，模型是不知道的。

所以要追加：

```python
messages.append({
    "role": "tool",
    "content": "Observation: 苏州晴，28°C，湿度55%"
})
```

教学版也可以简化成：

```python
messages.append({
    "role": "user",
    "content": "Observation: 苏州晴，28°C，湿度55%"
})
```

重点不是 role 名称，而是：

```text
工具结果必须进入上下文。
```

---

# 五、完整路径是什么样的

完整路径如下：

```text
User
→ messages
→ LLM 生成 Thought + Action
→ 程序解析 Action
→ 程序执行工具
→ 得到 Observation
→ Observation 放回 messages
→ LLM 读取更新后的 messages
→ Updated Thought
→ Final Answer 或继续 Action
```

---

## 天气 Demo

初始 messages：

```python
messages = [
    {
        "role": "system",
        "content": "你是一个天气 Agent，可以调用 get_weather 工具。"
    },
    {
        "role": "user",
        "content": "今天苏州天气怎么样？"
    }
]
```

模型第一次输出：

```text
Thought: 用户问的是实时天气，我需要调用天气工具。
Action:
{
  "action": "get_weather",
  "action_input": {
    "city": "苏州"
  }
}
```

Python 程序解析并执行：

```python
observation = get_weather("苏州")
```

工具返回：

```text
苏州晴，28°C，湿度55%
```

然后把 Observation 放回 messages：

```python
messages.append({
    "role": "assistant",
    "content": """
Thought: 用户问的是实时天气，我需要调用天气工具。
Action:
{
  "action": "get_weather",
  "action_input": {
    "city": "苏州"
  }
}
"""
})

messages.append({
    "role": "tool",
    "content": "Observation: 苏州晴，28°C，湿度55%"
})
```

此时完整上下文变成：

```text
system：你是天气 Agent，可以调用 get_weather 工具
user：今天苏州天气怎么样？
assistant：Thought + Action
tool：Observation: 苏州晴，28°C，湿度55%
```

然后再次调用模型。

模型第二次看到 Observation 后输出：

```text
Thought: 我已经拿到苏州天气数据，可以回答用户。
Final Answer: 苏州今天晴，温度 28°C，湿度 55%。天气较热，出门注意防晒。
```

---

# 六、Observation 和 Final Answer 的区别

这个非常重要。

```text
Observation 是工具返回的原始结果；
Final Answer 是模型整理后给用户的答案。
```

例如：

```text
Observation: {"weather": "sunny", "temp": 28, "humidity": 55}
```

Final Answer 应该是：

```text
苏州今天晴，28°C，湿度 55%，天气偏热，出门注意防晒。
```

也就是说：

```text
Observation 是原材料；
Final Answer 是加工后的答案。
```

---

# 七、Observation 的常见类型

| 观察类型 | 示例 |
|---|---|
| 系统反馈 | 错误信息、成功通知、状态码 |
| 数据变更 | 数据库更新、文件系统修改、状态变更 |
| 环境数据 | 传感器读数、系统指标、资源使用情况 |
| 响应分析 | API 响应、查询结果、计算输出 |
| 基于时间的事件 | 截止时间到达、定时任务完成 |
| 日志反馈 | 工具执行日志、RPA 执行结果 |

在银行 RPA 场景中，下面这些都算 Observation：

```text
接口返回 200
接口返回 500
数据库查无数据
Excel 写入成功
Selenium 找不到元素
验证码识别失败
页面加载超时
RPA 执行日志
文件下载成功
文件下载失败
```

---

# 八、Observation 要尽量结构化

不要只写：

```text
查询失败。
```

最好写清楚：

```json
{
  "status": "error",
  "tool": "get_weather",
  "error_type": "timeout",
  "message": "主天气接口请求超时",
  "retryable": true
}
```

这样模型才知道：

```text
能不能重试
要不要换工具
是不是需要人工介入
```

工程里 Observation 越清晰，Agent 越稳定。

---

# 九、Observation 要区分成功、失败、部分成功

真实业务中不要只分成功和失败。

至少要区分三类：

```text
成功：查到了完整数据
失败：接口超时、权限错误、页面错误
部分成功：查到一部分字段，但缺少关键字段
```

例如银行 RPA：

```text
Observation: 查询成功，但缺少抵押金额字段。
```

这时候 Agent 不应该直接输出最终结论，而应该：

```text
Thought: 缺少关键字段，无法判断风险等级，需要继续查询或提示人工复核。
```

---

# 十、错误情况如何处理

原则上，只要 Observation 里出现异常，Agent 就应该：

```text
先 Thought 分析错误
再决定下一个 Action
```

但不是每个错误都无限重试。

要根据错误类型决定：

```text
1. 可自动修复 → Thought 后继续 Action
2. 信息不足 → Thought 后追问用户
3. 高风险或不可恢复 → 停止，交给人工
```

---

## 常见错误类型

| 错误类型 | Observation 示例 | Agent 应该怎么 Thought |
|---|---|---|
| 参数错误 | 缺少 city 参数 | 需要让用户补充城市，或从上下文提取城市 |
| 工具不存在 | 未知工具 get_weatherr | 工具名可能写错，应改用 get_weather |
| API 超时 | request timeout | 可以重试一次，或切换备用接口 |
| 权限错误 | 401 Unauthorized | API Key 可能无效，需要提示人工检查配置 |
| 服务错误 | 500 Internal Server Error | 服务端异常，可以稍后重试或切换备用服务 |
| 数据为空 | 没有查询到结果 | 可能参数不准，需要确认输入或换查询方式 |
| 格式错误 | JSON 解析失败 | 需要重新输出合法 JSON Action |
| 业务失败 | 未找到客户信息 | 需要提示客户不存在或让用户核对信息 |
| 页面错误 | Selenium 找不到元素 | 页面结构变化，可能需要截图或人工介入 |
| 安全拦截 | 操作涉及敏感数据 | 停止执行，要求人工确认 |

---

# 十一、错误处理 Demo

## Demo 1：参数缺失

用户问：

```text
帮我查天气。
```

模型输出 Action：

```json
{
  "action": "get_weather",
  "action_input": {}
}
```

工具返回 Observation：

```text
Observation: 缺少必要参数 city。
```

Agent 下一步 Thought：

```text
我没有城市名称，无法查询天气。需要向用户追问城市。
```

Final Answer：

```text
请告诉我你要查询哪个城市的天气？
```

这里不应该继续乱调用工具。

---

## Demo 2：API 超时

Action：

```json
{
  "action": "get_weather",
  "action_input": {
    "city": "苏州"
  }
}
```

Observation：

```text
Observation: 主天气 API 请求超时。
```

Updated Thought：

```text
主接口超时，我可以尝试备用天气接口。
```

Next Action：

```json
{
  "action": "get_backup_weather",
  "action_input": {
    "city": "苏州"
  }
}
```

Observation：

```text
Observation: 苏州晴，28°C，湿度55%。
```

Final Answer：

```text
苏州今天晴，28°C，湿度55%。
```

---

## Demo 3：JSON 格式错误

模型输出：

```text
Action:
{
  "action": "calculator",
  "action_input": {
    "a": 3,
    "b": 4,
  }
}
```

这里最后多了一个逗号，JSON 解析失败。

Observation：

```text
Observation: JSONDecodeError，Action 不是合法 JSON。
```

Updated Thought：

```text
我需要重新输出合法 JSON，去掉多余逗号。
```

Next Action：

```json
{
  "action": "calculator",
  "action_input": {
    "a": 3,
    "b": 4
  }
}
```

---

## Demo 4：银行 RPA 页面元素找不到

Action：

```json
{
  "action": "click_button",
  "action_input": {
    "selector": "#queryBtn"
  }
}
```

Observation：

```text
Observation: Selenium NoSuchElementException，未找到 #queryBtn。
```

Updated Thought：

```text
页面结构可能变化，或者按钮还没加载。我应该先等待页面加载，再尝试备用选择器。
```

Next Action：

```json
{
  "action": "wait_and_click",
  "action_input": {
    "selector": "button[data-action='query']",
    "timeout": 10
  }
}
```

如果还失败：

```text
Observation: 备用选择器仍未找到。
```

Final Answer：

```text
查询按钮未找到，页面结构可能已变化，建议人工检查页面或更新选择器。
```

这里不要无限重试。

---

# 十二、Observation 不能无限追加

Day 2 学过 `messages` 成本问题。

Day 6 这里又出现了。

每次工具返回都放进 messages，如果结果很长，比如网页全文、PDF 全文、日志全文，会导致：

```text
token 变多
成本变高
响应变慢
上下文被污染
重要信息被淹没
```

所以工程上通常要做：

```text
原始结果保存到文件或数据库
messages 里只放摘要、关键字段、状态码、错误原因
```

例如不要放整段日志，而是放：

```text
Observation: 登录失败，错误码 401，原因：token 过期。
```

---

# 十三、Observation 需要控制重试次数

错误要分析，但不能无限重试。

要设置边界：

```text
最多重试 2 次
超过次数就停止
高风险操作不自动重试
权限错误不重试，直接提示人工检查
```

例如：

```text
Observation: 接口超时
→ 可以重试
```

```text
Observation: API Key 无效
→ 不要重试，提示检查配置
```

```text
Observation: 页面结构变化
→ 可以尝试备用选择器一次
→ 仍失败就人工介入
```

---

# 十四、Observation 是审计日志的重要来源

对企业系统来说，不能只看最终答案。

还要能追溯：

```text
调用了哪个工具
传了什么参数
工具返回了什么
有没有异常
模型为什么得出这个结论
```

所以：

```text
Action + Observation = Agent 的操作日志。
```

这对银行、金融、风控、RPA 场景尤其重要。

最终报告不能只写：

```text
该客户中风险。
```

还要能追溯：

```text
query_company_info 返回经营状态正常
query_judicial_risk 返回 2 条被执行记录
query_abnormal_operation 返回无经营异常
因此判断为中风险，建议人工复核
```

---

# 十五、结果如何被附加

执行操作后，框架一般按以下步骤处理：

```text
1. 解析操作，识别要调用的函数和参数
2. 执行操作
3. 将结果附加为 Observation
4. 把 Observation 放回 messages
5. 让模型基于更新后的 messages 继续思考
```

对应 Day 5 和 Day 6：

```text
Day 5：Stop and Parse，解析并执行 Action
Day 6：把执行结果作为 Observation 放回上下文
```

---

# 十六、Day 6 代码建议

建议目录：

```text
examples/06-observations/
```

建议文件：

```text
examples/06-observations/
├── observation_success_failure.py
├── observation_loop_demo.py
└── README.md
```

重点练两个东西：

```text
1. 工具成功时，Observation 如何进入 messages
2. 工具失败时，Agent 如何根据 Observation 换策略
```

示例流程：

```text
Action: query_primary_weather_api("苏州")
Observation: 主接口超时

Thought: 主接口失败，尝试备用接口
Action: query_backup_weather_api("苏州")
Observation: 苏州晴，28°C

Final Answer: 苏州当前天气晴，28°C
```

---

# 十七、Day 6 验收问题

今天结束前，必须能回答下面问题：

1. Observation 是什么？
2. Observation 和 Action 有什么区别？
3. Observation 和 Final Answer 有什么区别？
4. 为什么工具结果要放回 `messages`？
5. Observation 可以有哪些类型？
6. 为什么 Observation 要尽量结构化？
7. 什么是成功、失败、部分成功？
8. 工具成功时，Agent 下一步通常做什么？
9. 工具失败时，Agent 下一步通常做什么？
10. Observation 如何帮助 Agent 反思和调整？
11. 为什么 Observation 不能无限追加？
12. 为什么需要控制重试次数？
13. 在银行 RPA 场景里，什么可以算 Observation？
14. API 返回 `500` 算不算 Observation？
15. Selenium 页面找不到元素算不算 Observation？
16. Observation 为什么对审计很重要？

---

# 十八、今日结论

Day 6 不只是：

```text
把工具结果塞回 messages
```

更重要的是：

```text
把现实反馈整理成模型能理解、能判断、能继续行动的上下文。
```

完整理解是：

```text
1. Observation 是工具执行结果
2. Observation 必须放回 messages
3. Observation 不是 Final Answer
4. Observation 最好结构化
5. Observation 有成功、失败、部分成功
6. Observation 太长要摘要
7. Observation 错误要有重试边界
8. Observation 是审计日志的重要来源
```

一句话总结：

```text
Day 4 学 Agent 怎么想；
Day 5 学 Agent 怎么行动；
Day 6 学 Agent 怎么看行动结果，并根据结果调整下一步。
```

