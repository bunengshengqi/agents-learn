---
title: Day 05｜Action：智能体动作与环境交互
date: 2026-06-20
tags:
  - AI-Agent
  - Action
  - JSON-Agent
  - Code-Agent
  - Stop-and-Parse
  - Tool-Calling
  - Python
  - Obsidian
status: in-progress
---

# Day 05｜Action：智能体动作与环境交互

## 一、今天的学习主题

Day 5 的核心主题是：

```text
Action：使智能体能够与环境交互
```

前几天的关系是：

```text
Day 1：LLM 是什么
Day 2：messages 是什么
Day 3：Thought → Action → Observation 完整循环
Day 4：深入理解 Thought，模型怎么推理和规划
Day 5：深入理解 Action，模型怎么把想法变成可执行动作
```

Day 5 的重点不是模型怎么想，而是：

```text
模型想完以后，怎么把“我要做什么”变成程序可以执行的指令。
```

---

# 二、今天最重要的一句话

```text
Action 是 Agent 把想法变成可执行指令的方式。
```

Day 4 的 Thought 是：

```text
我应该查天气。
```

Day 5 的 Action 是：

```json
{
  "action": "get_weather",
  "action_input": {
    "city": "苏州"
  }
}
```

所以：

```text
Thought 是“我要做什么”；
Action 是“我具体怎么做”。
```

---

# 三、Action 是什么

Action 是 AI Agent 与外部环境交互的具体步骤。

外部环境可以是：

```text
网页
数据库
API
Excel
文件系统
浏览器
业务系统
RPA 页面
搜索引擎
天气服务
企业微信
飞书
```

Action 可以包括：

```text
查天气
查数据库
读取 Excel
调用 API
搜索网页
执行 Python 代码
发送邮件
打开浏览器
查询企业风险
```

一句话：

```text
Action 是 Agent 从“会说话”变成“能做事”的关键。
```

---

# 四、为什么 Action 要结构化

因为程序要能读懂模型的输出。

如果模型只说：

```text
我去查一下苏州天气。
```

Python 程序不好执行。

但如果模型输出：

```json
{
  "action": "get_weather",
  "action_input": {
    "city": "苏州"
  }
}
```

程序就能解析出：

```text
工具名：get_weather
参数：city=苏州
```

然后真正执行：

```python
get_weather("苏州")
```

所以 Action 结构化的意义是：

```text
让模型输出变成程序可以执行的指令。
```

---

# 五、智能体动作的两种主要类型

Day 5 重点理解两种 Action 表达方式：

```text
JSON Agent
Code Agent
```

| 类型 | 输出形式 | 适合场景 |
|---|---|---|
| JSON Agent | JSON | 单次工具调用、参数明确、安全要求高 |
| Code Agent | Python 等代码 | 多步骤、循环、数据分析、复杂逻辑 |

---

# 六、JSON Agent 是什么

JSON Agent 是让模型用 JSON 表达动作。

例如：

```json
{
  "action": "calculator",
  "action_input": {
    "a": 3,
    "b": 4
  }
}
```

程序解析后执行：

```python
calculator(3, 4)
```

---

## JSON Agent 的特点

```text
结构清晰
参数明确
容易解析
安全边界更好控制
适合调用单个工具或 API
```

---

## JSON Agent 的适用场景

```text
查天气
查汇率
查订单
查客户信息
调用单个 API
查询单个数据库接口
执行固定函数
```

---

## JSON Agent 示例：查天气

模型输出：

```json
{
  "action": "get_weather",
  "action_input": {
    "city": "苏州"
  }
}
```

程序执行：

```python
get_weather("苏州")
```

返回：

```text
苏州今天晴，28°C。
```

---

## JSON Agent 示例：计算乘法

模型输出：

```json
{
  "action": "calculator",
  "action_input": {
    "a": 3,
    "b": 4
  }
}
```

程序执行：

```python
calculator(3, 4)
```

返回：

```text
12
```

这就是 Day 3 写过的 `calculator_agent.py` 的核心逻辑。

---

# 七、Code Agent 是什么

Code Agent 是让模型直接生成一段可执行代码作为动作。

JSON Agent 输出的是：

```json
{
  "action": "get_weather",
  "action_input": {
    "city": "New York"
  }
}
```

Code Agent 输出的是：

```python
result = get_weather("New York")
print(result)
```

所以：

```text
JSON Agent 像是在填表调用工具；
Code Agent 像是在写一段小程序完成任务。
```

---

# 八、Code Agent 的应用场景

Code Agent 适合：

```text
步骤多
逻辑复杂
需要循环
需要条件判断
需要数据处理
需要组合多个 API
需要复用函数
```

---

## 场景一：数据分析

用户说：

```text
读取 sales.xlsx，按月份统计销售额，找出增长最快的产品。
```

Code Agent 可以生成：

```python
import pandas as pd

df = pd.read_excel("sales.xlsx")
monthly_sales = df.groupby(["month", "product"])["amount"].sum()
print(monthly_sales)
```

这种任务用 JSON 一步步调用会很麻烦，但用代码很自然。

---

## 场景二：多接口组合

用户说：

```text
帮我比较美国、日本、德国、印度哪个国家买手机最便宜。
```

它需要：

```text
查汇率
查当地价格
计算税费
估算运费
比较最终价格
```

Code Agent 可以写一个 `for` 循环，把所有国家跑一遍。

---

## 场景三：银行 RPA 批量处理

用户说：

```text
读取 Excel 里的客户名单，逐个查询风险接口，把结果写回 Excel。
```

Code Agent 可能生成：

```python
for customer in customers:
    risk = query_risk(customer)
    write_result(customer, risk)
```

这比 JSON Agent 一次一次输出动作更方便。

---

## 场景四：复杂计算

用户说：

```text
根据贷款本金、利率、期限，生成每月还款计划。
```

Code Agent 可以用循环直接计算每月金额。

---

## 场景五：文件处理

用户说：

```text
批量读取一个文件夹里的 PDF，提取关键字段，生成汇总表。
```

这种批量文件处理也适合 Code Agent。

---

# 九、图片一：JSON Agent 与 Code Agent 对比

图片一最能体现的是：

```text
Code Agent 在复杂、多步骤任务中，比 JSON Agent 更高效。
```

任务是：

```text
比较美国、日本、德国、印度哪个国家购买某手机最划算。
```

这个任务需要多个步骤：

```text
查汇率
查当地手机价格
换算税费
估算运费
计算最终价格
比较最低价格
```

---

## JSON Agent 的方式

JSON Agent 会一轮一轮调用工具：

```text
Action: lookup_rates Germany
Observation: 得到汇率和税率

Action: lookup_phone_price Germany
Observation: 得到手机价格

Action: convert_and_tax
Observation: 得到换算价格

Action: estimate_shipping_cost
Observation: 得到运费

Action: estimate_final_price
Observation: 得到最终价格

然后换 Japan、USA、India 再重复一遍
```

问题是：

```text
动作轮次很多
上下文变长
速度变慢
更容易中间出错
```

---

## Code Agent 的方式

Code Agent 可以直接生成一段代码：

```python
countries = ["USA", "Japan", "Germany", "India"]
final_prices = {}

for country in countries:
    exchange_rate, tax_rate = lookup_rates(country)
    local_price = lookup_phone_price("CodeAct 1", country)
    converted_price = convert_and_tax(local_price, exchange_rate, tax_rate)
    shipping_cost = estimate_shipping_cost(country)
    final_price = estimate_final_price(converted_price, shipping_cost)
    final_prices[country] = final_price

most_cost_effective_country = min(final_prices, key=final_prices.get)
print(most_cost_effective_country, final_prices[most_cost_effective_country])
```

这段代码里有：

```text
循环
变量
函数调用
结果保存
比较最小值
最终输出
```

这就是 Code Agent 的优势：

```text
表达能力强
能处理复杂逻辑
动作次数更少
可以复用代码结构
更容易调试
```

---

# 十、图片二：天气 Code Agent 示例

图片二展示的是一个 Code Agent 如何完成“查询天气”的任务。

它不是输出：

```json
{
  "action": "get_weather",
  "city": "New York"
}
```

而是生成 Python 代码：

```python
def get_weather(city):
    import requests
    api_url = f"https://api.weather.com/v1/location/{city}?apiKey=YOUR_API_KEY"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get("weather", "No weather information available")
    else:
        return "Error: Unable to fetch weather data."

result = get_weather("New York")
final_answer = f"The current weather in New York is: {result}"
print(final_answer)
```

---

## 这个例子体现了什么

### 1. Action 是代码，不是 JSON

这个 Action 是一整段 Python 代码。

---

### 2. 代码里可以包含完整流程

代码中包含：

```text
定义函数
导入 requests
拼接 API URL
发起 HTTP 请求
判断状态码
解析 JSON
返回结果
print 最终答案
```

这比单个 JSON Action 表达能力更强。

---

### 3. print 是结束信号

图片中提到：

```text
通过 print(final_answer) 表明执行完成
```

对 Code Agent 来说：

```text
print(final_answer)
```

就是告诉外部系统：

```text
代码执行完了，最终答案在这里。
```

---

# 十一、Stop and Parse 是什么

Stop and Parse 是 Agent 工程里非常重要的方法。

人话版：

```text
模型生成到 Action 的时候，程序先让它停下来；
然后程序解析它输出的 Action；
解析成功后，程序执行工具或代码；
执行结果再反馈给模型。
```

完整流程：

```text
用户问题
→ 模型输出 Thought + Action
→ 程序检测到 Action
→ 停止模型继续生成
→ 解析 Action
→ 执行工具或代码
→ 得到结果
→ 作为 Observation 回填 messages
→ 再让模型继续
```

---

# 十二、为什么要 Stop

因为如果不停止，模型可能会自己幻想工具结果。

例如：

```text
Action: get_weather("New York")
Observation: New York is sunny.
Final Answer: ...
```

但这个 Observation 可能是模型编的，不是真工具返回的。

所以必须：

```text
模型输出 Action 后停住；
程序真正执行 Action；
真实结果回来后，再让模型继续。
```

这就是 Stop and Parse 的意义。

---

# 十三、Stop and Parse 在 JSON Agent 里的体现

模型输出：

```text
Thought: 我需要查询苏州天气。
Action:
{
  "action": "get_weather",
  "action_input": {
    "city": "苏州"
  }
}
```

程序做三件事：

---

## 1. Stop

看到 `Action:` 后，不让模型继续瞎写。

---

## 2. Parse

解析 JSON：

```python
action = {
    "action": "get_weather",
    "action_input": {
        "city": "苏州"
    }
}
```

---

## 3. Execute

执行：

```python
get_weather("苏州")
```

得到：

```text
苏州今天晴，28°C。
```

然后把结果作为 Observation 放回：

```text
Observation: 苏州今天晴，28°C。
```

---

# 十四、Stop and Parse 在 Code Agent 里的体现

Code Agent 输出：

```python
result = get_weather("New York")
final_answer = f"The current weather in New York is: {result}"
print(final_answer)
```

程序做四件事：

---

## 1. Stop

检测到完整代码块结束，或者检测到：

```python
print(final_answer)
```

---

## 2. Parse

把代码块提取出来。

---

## 3. Execute

在受控环境里执行代码。

---

## 4. Capture output

捕获 `print()` 输出：

```text
The current weather in New York is: cloudy, 15°C.
```

这就是 Code Agent 的 Observation 或最终结果。

---

# 十五、JSON Agent 与 Code Agent 怎么选择

| 场景 | 更适合 |
|---|---|
| 单次工具调用 | JSON Agent |
| 参数明确的 API | JSON Agent |
| 安全要求高 | JSON Agent |
| 流程固定 | JSON Agent |
| 批量处理 | Code Agent |
| 数据分析 | Code Agent |
| 多步骤计算 | Code Agent |
| 需要循环和条件判断 | Code Agent |
| 需要组合多个函数 | Code Agent |

对银行 RPA 场景来说：

```text
单个客户查询 → JSON Agent
批量客户查询 + Excel 汇总 → Code Agent
```

---

# 十六、银行 RPA 场景示例

## 示例一：单个客户查询，适合 JSON Agent

用户说：

```text
查询客户 A 的不动产抵押信息。
```

JSON Action：

```json
{
  "action": "query_bdc_info",
  "action_input": {
    "customer_name": "客户A",
    "cert_no": "苏房权证xxxx"
  }
}
```

程序执行：

```python
query_bdc_info(customer_name="客户A", cert_no="苏房权证xxxx")
```

---

## 示例二：批量客户查询，适合 Code Agent

用户说：

```text
读取 Excel 中所有客户，批量查询不动产抵押信息，并生成汇总表。
```

Code Action：

```python
import pandas as pd

df = pd.read_excel("客户名单.xlsx")
results = []

for _, row in df.iterrows():
    result = query_bdc_info(row["客户名称"], row["产权证号"])
    results.append(result)

out = pd.DataFrame(results)
out.to_excel("不动产查询结果.xlsx", index=False)

print("批量查询完成，已生成不动产查询结果.xlsx")
```

这种任务如果用 JSON Agent，会需要很多轮单独查询。

用 Code Agent，一段代码就能表达完整流程。

---

# 十七、Code Agent 的优势

## 1. 表达能力强

代码可以表达：

```text
循环
条件判断
函数调用
变量保存
异常处理
数据结构
```

比 JSON 更灵活。

---

## 2. 模块化和可复用

生成的代码可以包含函数：

```python
def calculate_final_price(...):
    ...
```

后续任务可以复用。

---

## 3. 更容易调试

代码可以打印中间变量，也可以通过报错定位问题。

例如：

```python
print(final_prices)
```

---

## 4. 更适合复杂任务

对于多步骤、多数据源、多函数组合任务，Code Agent 更自然。

---

# 十八、Code Agent 的风险

Code Agent 很强，但风险也大。

因为它生成的是代码。

如果不限制，可能出现危险操作：

```python
import os
os.remove("重要文件.xlsx")
```

或者：

```python
requests.post("外部地址", data=客户信息)
```

所以真正工程落地必须加：

```text
沙箱执行
权限限制
只允许白名单函数
禁止危险库
禁止文件删除
执行超时
日志审计
人工确认
敏感数据脱敏
```

银行场景尤其不能让 Code Agent 随便执行。

---

# 十九、Day 5 和前三天的关系

## Day 3

学的是完整循环：

```text
Thought → Action → Observation
```

---

## Day 4

深入 Thought：

```text
模型怎么推理、规划、决策。
```

---

## Day 5

深入 Action：

```text
模型怎么把想法变成结构化、可解析、可执行的动作。
```

这三天串起来就是：

```text
模型先 Thought
→ 生成 JSON 或代码形式的 Action
→ 程序 Stop and Parse
→ 程序执行动作
→ 得到 Observation
```

---

# 二十、Day 5 代码建议

建议目录：

```text
examples/05-actions/
```

建议文件：

```text
examples/05-actions/
├── json_action_parser.py
├── code_action_demo.py
└── README.md
```

重点练两个东西：

```text
1. 模型输出 JSON Action，Python 解析并执行
2. 模型输出代码片段，Python 演示 Code Agent 的风险和边界
```

今天不需要写复杂 Agent。

重点是理解：

```text
Action 必须能被程序解析和执行。
```

---

# 二十一、Day 5 验收问题

今天结束前，必须能回答下面问题：

1. Action 是什么？
2. Action 和 Thought 有什么区别？
3. 为什么 Action 要结构化？
4. JSON Agent 是什么？
5. Code Agent 是什么？
6. JSON Agent 和 Code Agent 有什么区别？
7. 什么场景适合 JSON Agent？
8. 什么场景适合 Code Agent？
9. Stop and Parse 是什么？
10. 为什么模型输出 Action 后要停下来？
11. Stop and Parse 在 JSON Agent 中怎么体现？
12. Stop and Parse 在 Code Agent 中怎么体现？
13. Code Agent 为什么表达能力更强？
14. Code Agent 有哪些安全风险？
15. 银行 RPA 中哪些场景适合 JSON Agent？
16. 银行 RPA 中哪些场景适合 Code Agent？

---

# 二十二、今日结论

Day 5 的核心是：

```text
Action 是 Agent 把想法变成可执行指令的方式。
```

JSON Agent 是：

```text
用 JSON 表达动作。
```

Code Agent 是：

```text
用代码表达动作。
```

Stop and Parse 是：

```text
模型输出动作后先停下来，由程序解析并真实执行，防止模型自己编造结果。
```

一句话总结：

```text
Day 4 学的是 Agent 怎么想；
Day 5 学的是 Agent 怎么把想法变成程序能执行的动作。
```

