## 一、今天学习目标

今天进入 Hugging Face Agents Course 的第 2.1 单元中关于 ToolCallingAgent 的内容。

今天重点是搞清楚：

- ToolCallingAgent 是什么
- 为什么 Agent 的 Action 可以写成 JSON 结构
- ToolCallingAgent 和 CodeAgent 的区别
- 课程图片中 Text/JSON Agent 和 CodeAgent 的对比是什么意思
- ToolCallingAgent 的真实意义是不是只是“转成 JSON”
- 什么场景适合 ToolCallingAgent，什么场景适合 CodeAgent

---

## 二、一句话理解 ToolCallingAgent

ToolCallingAgent 是 smolagents 中的一种智能体类型。

它的特点是：

```text
模型不直接生成 Python 代码，
而是生成 JSON 结构的工具调用指令。
```

也就是说，ToolCallingAgent 的 Action 通常不是：

```python
result = web_search("苏州天气")
```

而是类似：

```json
{
  "name": "web_search",
  "arguments": {
    "query": "苏州天气"
  }
}
```

框架拿到这个 JSON 后，再去调用真正的工具函数。

---

## 三、操作编写为代码片段或 JSON 结构是什么意思？

Agent 要行动时，必须告诉程序两件事：

```text
1. 我要调用哪个工具
2. 我要传什么参数
```

这个“行动指令”可以有两种表达方式：

- Python 代码片段
- JSON 工具调用结构

---

## 四、CodeAgent 的 Action：Python 代码片段

CodeAgent 的 Action 是 Python 代码。

例如：

```python
for query in [
    "Best catering services in Gotham City",
    "Party theme ideas for superheroes",
]:
    print(web_search(f"Search for: {query}"))
```

这段代码的意思是：

```text
模型直接生成一段 Python 代码。
框架执行这段代码。
代码里调用 web_search 工具。
```

CodeAgent 的特点是：

- 可以写 for 循环
- 可以写 if 判断
- 可以保存变量
- 可以处理列表和字典
- 可以组合多个工具
- 适合复杂任务

---

## 五、ToolCallingAgent 的 Action：JSON 结构

ToolCallingAgent 的 Action 是 JSON 工具调用结构。

例如：

```json
[
  {
    "name": "web_search",
    "arguments": {
      "query": "Best catering services in Gotham City"
    }
  },
  {
    "name": "web_search",
    "arguments": {
      "query": "Party theme ideas for superheroes"
    }
  }
]
```

这段 JSON 的意思是：

```text
第一次调用 web_search，参数是 Best catering services in Gotham City。
第二次调用 web_search，参数是 Party theme ideas for superheroes。
```

框架看到 JSON 后，会解析：

```text
name -> 工具名称
arguments -> 工具参数
```

然后真正执行对应工具。

---

## 六、为什么要有 JSON 工具调用？

很多大模型厂商都支持工具调用格式。

比如 OpenAI、Anthropic、DeepSeek 的部分兼容接口，都可以让模型输出结构化工具调用。

JSON 工具调用的好处：

| 优点 | 说明 |
|---|---|
| 结构清晰 | 明确告诉程序调用哪个工具、传什么参数 |
| 更安全 | 不执行任意 Python 代码 |
| 更标准 | 很多模型 API 原生支持 tool calling |
| 易解析 | 程序可以稳定读取工具名和参数 |
| 适合简单工具调用 | 比如搜索、天气、数据库查询、API 查询 |

JSON 工具调用的缺点：

```text
不擅长复杂循环、复杂计算、复杂数据处理。
```

比如要比较多个国家的手机最终价格，JSON Agent 可能要多轮调用工具，而 CodeAgent 可以用一段 Python 循环完成。

---

## 七、第二张图说明了什么？

第二张图对比的是：

```text
Text/JSON Agent
和
CodeAgent
```

任务是：

```text
判断在哪个国家购买 CodeAct 1 手机最划算。
候选国家包括 USA、Japan、Germany、India。
```

可用 API 包括：

```text
lookup_rates(country)
lookup_phone_price(model, country)
convert_and_tax(price, exchange_rate, tax_rate)
estimate_shipping(country)
estimate_final_price(converted_price, shipping_cost)
```

---

## 八、左边 Text/JSON Agent 的工作方式

左边是 Text/JSON Agent。

它的工作方式大概是：

```text
1. 查 Germany 的汇率和税率
2. 查 Germany 的手机价格
3. 计算 Germany 的税后价格
4. 查 Germany 的运费
5. 计算 Germany 的最终价格
6. 再查 Japan
7. 再查 USA
8. 再查 India
9. 最后比较哪个国家最便宜
```

它的问题是：

```text
每一步都要单独发一次 Action。
步骤多，轮次多。
```

所以 JSON Agent 在复杂任务中可能会显得比较啰嗦。

---

## 九、右边 CodeAgent 的工作方式

右边是 CodeAgent。

它可以直接生成一段 Python 代码：

```python
countries = ["USA", "Japan", "Germany", "India"]
final_prices = {}

for country in countries:
    exchange_rate, tax_rate = lookup_rates(country)
    local_price = lookup_phone_price("CodeAct 1", country)
    converted_price = convert_and_tax(local_price, exchange_rate, tax_rate)
    shipping_cost = estimate_shipping(country)
    final_price = estimate_final_price(converted_price, shipping_cost)
    final_prices[country] = final_price

most_cost_effective_country = min(final_prices, key=final_prices.get)
```

这段代码一次性完成了：

- 遍历多个国家
- 查询汇率
- 查询价格
- 计算税费
- 查询运费
- 计算最终价格
- 找出最低价格

所以图里的大于号表达的是：

```text
在复杂任务中，CodeAgent 通常比 Text/JSON Agent 更高效。
```

---

## 十、ToolCallingAgent 的意义只是转换成 JSON 吗？

不是。

ToolCallingAgent 不只是“转换成 JSON”。

更准确地说：

```text
ToolCallingAgent 是让模型用标准化 JSON 工具调用格式，
安全、稳定地调用外部工具。
```

它做的事情包括：

```text
1. 把工具描述提供给模型
2. 让模型判断该调用哪个工具
3. 让模型生成 JSON 工具调用结构
4. 框架解析 JSON
5. 框架执行对应工具
6. 把工具执行结果返回给模型
7. 模型继续思考或输出最终答案
```

所以：

```text
JSON 只是 ToolCallingAgent 的 Action 表达形式。
```

真正意义是：

```text
让工具调用标准化、可解析、可控。
```

---

## 十一、CodeAgent 和 ToolCallingAgent 怎么选？

| 场景 | 更适合 |
|---|---|
| 简单查天气 | ToolCallingAgent |
| 简单搜索 | ToolCallingAgent |
| 查数据库某条记录 | ToolCallingAgent |
| 调一个 API 返回结果 | ToolCallingAgent |
| 多步骤计算 | CodeAgent |
| 需要 for 循环 | CodeAgent |
| 需要处理表格、列表、字典 | CodeAgent |
| 需要组合多个工具并比较结果 | CodeAgent |
| 更关注安全，不想执行 Python 代码 | ToolCallingAgent |
| 更关注复杂任务表达能力 | CodeAgent |

一句话理解：

```text
ToolCallingAgent 更像“结构化工具调用器”。
CodeAgent 更像“会写小程序完成任务的 Agent”。
```

---

## 十二、和前面 Day10 的关系

Day10 学的是 CodeAgent。

CodeAgent 的 Action 是：

```text
Python 代码
```

Day11 学的是 ToolCallingAgent。

ToolCallingAgent 的 Action 是：

```text
JSON 工具调用结构
```

它们都属于 Agent。

区别不是“谁能不能调用工具”，而是：

```text
它们用什么形式表达 Action。
```

---

## 十三、我的理解

CodeAgent 更适合复杂任务。

例如：

- 多步骤计算
- 循环处理多个对象
- 比较多个方案
- 处理表格数据
- 组合多个工具完成一件事

ToolCallingAgent 更适合简单、明确、安全的工具调用。

例如：

- 搜索一次
- 查天气
- 查数据库
- 调接口
- 获取某个固定信息

所以我不能只记住：

```text
ToolCallingAgent = JSON
```

更应该记住：

```text
ToolCallingAgent = 标准化、结构化、安全的工具调用方式。
```

---

## 十四、今日核心总结

今天要掌握的核心：

```text
1. Agent 的 Action 可以用代码表达，也可以用 JSON 表达。
2. CodeAgent 使用 Python 代码作为 Action。
3. ToolCallingAgent 使用 JSON 工具调用结构作为 Action。
4. JSON 结构更标准、更安全、更容易解析。
5. CodeAgent 更适合复杂任务和多步骤数据处理。
6. ToolCallingAgent 更适合简单、明确、稳定的工具调用。
```

---

## 十五、今日金句

```text
CodeAgent 是让模型写代码行动。
ToolCallingAgent 是让模型输出 JSON 指令行动。
```

