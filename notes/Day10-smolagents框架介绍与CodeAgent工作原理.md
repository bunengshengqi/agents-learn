
## 一、今天学习目标

今天进入 Hugging Face Agents Course 的第 2.1 单元：smolagents 框架。

今天重点不是把整个 smolagents 学完，而是先搞清楚：

- smolagents 是什么
- smolagents 有哪些智能体类型
- CodeAgent 和 JSON Agent 的区别
- CodeAgent 是如何工作的
- 如何构建一个代码智能体
- 自定义工具怎么给 Agent 使用
- 写好的 Agent 后面怎么使用、部署和变现

---

## 二、smolagents 是什么？

smolagents 是 Hugging Face 提供的一个轻量级 Agent 框架。

它的作用是帮助我们快速构建智能体，让大模型不仅能回答问题，还能：

- 调用工具
- 执行代码
- 处理多步骤任务
- 根据执行结果继续调整
- 最后输出答案

我前面 Day03-Day08 是手写 Agent 的底层流程。

比如：

```text
Thought → Action → Observation → Final Answer
```

到了 smolagents 阶段，这些流程开始由框架帮我组织。

---

## 三、为什么使用 smolagents？

smolagents 的特点：

- 轻量
- 代码少
- 容易理解
- 适合教学
- 适合快速做 Demo
- 适合理解 Agent 的底层运行机制
- Hugging Face 生态支持比较好

我的理解：

```text
smolagents 不是为了做最复杂的大系统，
而是为了让我快速理解和构建 Agent。
```

它适合我从“手写 Agent”过渡到“框架化 Agent”。

---

## 四、smolagents 有哪些智能体类型？

目前重点先记住两类：

| 智能体类型 | 英文 | Action 形式 | 适合场景 |
|---|---|---|---|
| 代码智能体 | CodeAgent | Python 代码 | 多步骤计算、复杂逻辑、数据处理 |
| 工具调用智能体 | ToolCallingAgent / JSON Agent | JSON 工具调用 | 简单工具选择、结构化 API 调用 |

划分标准：

```text
看模型输出的 Action 是什么形式。
```

如果模型输出的是 Python 代码，就是 CodeAgent。

如果模型输出的是 JSON 工具调用，就是 JSON Agent。

---

## 五、CodeAgent 和 JSON Agent 的区别

### 1. JSON Agent 是什么？

JSON Agent 的 Action 通常长这样：

```json
{
  "tool": "search",
  "arguments": {
    "query": "苏州天气"
  }
}
```

它的特点是：

```text
模型每次输出一个工具调用指令，
程序根据 JSON 去调用对应工具。
```

适合：

- 简单工具调用
- API 查询
- 天气查询
- 搜索
- 单步或少量步骤任务

### 2. CodeAgent 是什么？

CodeAgent 的 Action 是 Python 代码。

比如模型可能会生成：

```python
weather = get_weather(city="苏州")
final_answer(weather)
```

它的特点是：

```text
模型不是只输出一个 JSON，
而是直接写一段 Python 代码来完成任务。
```

适合：

- 多步骤计算
- 循环处理
- 数据分析
- 表格计算
- 多个工具组合
- 复杂业务逻辑

### 3. 二者核心区别

| 对比项 | JSON Agent | CodeAgent |
|---|---|---|
| Action 形式 | JSON | Python 代码 |
| 工具调用方式 | 一次通常调用一个工具 | 一段代码里可以调用多个工具 |
| 多步骤任务 | 需要多轮交互 | 可以一段代码完成 |
| 循环和判断 | 不方便 | Python 原生支持 |
| 数据处理 | 较弱 | 较强 |
| 适合任务 | 简单 API 调用 | 复杂任务执行 |

一句话总结：

```text
JSON Agent 是“模型发工具调用指令”。
CodeAgent 是“模型写 Python 代码来完成任务”。
```

---

## 六、第一张图怎么理解？

第一张图对比的是：

```text
传统 Text/JSON Agent
和
CodeAgent
```

任务是：

```text
判断在哪个国家购买 CodeAct 1 手机最划算。
需要比较 USA、Japan、Germany、India。
```

可用工具包括：

```text
lookup_rates(country)
lookup_phone_price(model, country)
convert_and_tax(price, exchange_rate, tax_rate)
estimate_shipping(country)
estimate_final_price(converted_price, shipping_cost)
```

### 1. 左边 Text/JSON Agent 的工作方式

左边是传统 JSON Agent。

它大概这样工作：

```text
先查德国汇率
再查德国手机价格
再计算德国税后价格
再查德国运费
再计算德国最终价格

然后查日本
然后查美国
然后查印度

最后比较哪个国家最便宜
```

也就是说，它要一步一步调用很多次工具。

缺点：

- 步骤多
- 交互轮次多
- 每次只能做一点
- 循环处理很麻烦

### 2. 右边 CodeAgent 的工作方式

右边是 CodeAgent。

它可以直接写一段 Python 代码：

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
- 计算运费
- 计算最终价格
- 找出最低价格

所以图里强调：

```text
CodeAgent 需要更少的 Action。
```

因为 Python 代码天然支持：

- for 循环
- if 判断
- 变量保存
- 字典
- 列表
- min/max 等内置函数

我的理解：

```text
JSON Agent 像是一条一条下命令。
CodeAgent 像是直接写一个小程序去完成任务。
```

---

## 七、第二张图怎么理解？

第二张图讲的是：

```text
CodeAgent.run() 是如何工作的。
```

核心流程如下：

```text
用户输入任务
      ↓
创建 TaskStep
      ↓
写入 logs
      ↓
根据 logs 生成 messages
      ↓
发送给大模型
      ↓
模型生成 Python 代码
      ↓
框架提取代码
      ↓
执行代码
      ↓
代码调用工具
      ↓
得到执行结果或错误
      ↓
写入 ActionStep
      ↓
如果没有 final_answer，继续循环
      ↓
如果调用 final_answer，返回最终答案
```

---

## 八、CodeAgent 内部几个关键对象

| 名称 | 含义 |
|---|---|
| logs | Agent 的运行日志，记录每一步发生了什么 |
| SystemPromptStep | 系统提示词步骤 |
| TaskStep | 用户任务步骤 |
| ActionStep | 每一次行动和执行结果 |
| model | 大模型，负责生成下一步代码 |
| tools | 工具列表，Agent 可以调用的函数 |
| final_answer | 结束任务并返回结果的工具 |

我的理解：

```text
logs 就像 Agent 的记忆本。
model 负责想下一步。
tools 是 Agent 能用的工具。
ActionStep 是每一次行动记录。
```

---

## 九、CodeAgent 的工作流程

CodeAgent 的核心流程可以理解为：

```text
1. 用户给任务
2. Agent 把任务写入 logs
3. Agent 把 logs 转成 messages
4. messages 发给模型
5. 模型生成 Python 代码
6. 框架执行 Python 代码
7. 代码里调用工具
8. 工具返回结果
9. 结果写入 logs
10. 如果没有完成，就继续下一轮
11. 如果调用 final_answer，就结束
```

这和前面学的 Thought-Action-Observation 是对应的。

| 前面手写 Agent | CodeAgent 中的表现 |
|---|---|
| Thought | 模型生成代码前的推理 |
| Action | 模型生成的 Python 代码 |
| Observation | 代码执行结果、工具返回结果、错误日志 |
| Final Answer | final_answer 工具返回的内容 |

---

## 十、如何构建一个代码智能体？

一个最小的 CodeAgent 大概由三部分组成：

```text
模型 model
工具 tools
智能体 agent
```

示例：

```python
from smolagents import CodeAgent, LiteLLMModel

model = LiteLLMModel(
    model_id="openai/gpt-4o-mini",
    api_key="你的 API Key",
    api_base="你的 Base URL",
)

agent = CodeAgent(
    tools=[],
    model=model,
)

result = agent.run("请计算 12 * 8 + 30")
print(result)
```

执行流程：

```text
1. 创建 model
2. 创建 CodeAgent
3. 调用 agent.run()
4. Agent 让模型生成代码
5. 框架执行代码
6. 返回最终结果
```

---

## 十一、如何给 Agent 添加自定义工具？

工具本质上就是一个 Python 函数。

使用 `@tool` 装饰器，把普通函数注册成 Agent 可以调用的工具。

示例：天气工具

```python
from smolagents import tool

@tool
def get_weather(city: str) -> str:
    """
    查询城市天气。

    Args:
        city: 城市名称
    """
    data = {
        "苏州": "晴，28度",
        "上海": "小雨，24度",
        "北京": "晴，22度",
    }
    return data.get(city, "暂无数据")
```

然后把工具放进 Agent：

```python
agent = CodeAgent(
    tools=[get_weather],
    model=model,
)
```

使用：

```python
answer = agent.run("今天苏州天气怎么样？")
print(answer)
```

这时候 Agent 就可以自己决定是否调用：

```python
get_weather(city="苏州")
```

---

## 十二、自定义工具“准备菜单”怎么理解？

“准备菜单”可以理解成：

```text
我提前告诉 Agent：
你可以使用哪些工具。
```

比如做一个点菜推荐 Agent：

```python
from smolagents import tool

@tool
def get_menu() -> str:
    """
    获取今日菜单。
    """
    return """
    今日菜单：
    1. 红烧牛肉饭 28元
    2. 番茄鸡蛋面 18元
    3. 黑椒鸡胸沙拉 22元
    4. 酸菜鱼套餐 36元
    """

@tool
def recommend_food(preference: str) -> str:
    """
    根据用户偏好推荐菜品。

    Args:
        preference: 用户口味偏好，比如清淡、减脂、重口味
    """
    if "减脂" in preference:
        return "推荐黑椒鸡胸沙拉"
    if "重口味" in preference:
        return "推荐酸菜鱼套餐"
    return "推荐番茄鸡蛋面"
```

注册工具：

```python
agent = CodeAgent(
    tools=[get_menu, recommend_food],
    model=model,
)
```

调用：

```python
agent.run("我今天想吃减脂一点的，有什么推荐？")
```

Agent 可能会自己执行：

```python
menu = get_menu()
recommendation = recommend_food(preference="减脂")
final_answer(recommendation)
```

我的理解：

```text
tools 就是给 Agent 准备的工具菜单。
Agent 不能凭空调用工具。
我给它什么工具，它才能使用什么工具。
```

---

## 十三、在智能体内部使用 Python 导入

CodeAgent 会执行模型生成的 Python 代码。

但是为了安全，默认不会让它随便导入所有 Python 库。

如果想让 Agent 使用某些库，需要显式授权。

示例：

```python
agent = CodeAgent(
    tools=[get_weather],
    model=model,
    additional_authorized_imports=["math", "statistics", "datetime"]
)
```

这样模型生成的代码里就可以使用：

```python
import math
import statistics
from datetime import datetime
```

比如：

```python
import statistics

nums = [12, 15, 18, 20]
mean = statistics.mean(nums)
final_answer(mean)
```

注意：

不要随便开放危险库，比如：

```text
os
subprocess
shutil
```

因为 CodeAgent 可以执行代码，如果权限太大，会有安全风险。

---

## 十四、我写好了一个 Agent，怎么使用？

分三种情况。

### 1. 自己本地使用

不需要部署。

直接写 Python 脚本运行：

```python
result = agent.run("帮我分析这个商品能不能上闲鱼")
print(result)
```

适合：

- 自己学习
- 本地调试
- 做内部工具
- 做自动化脚本

### 2. 做成接口给别人用

需要部署。

可以用 FastAPI 包一层：

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class AgentRequest(BaseModel):
    question: str

@app.post("/agent/run")
def run_agent(req: AgentRequest):
    answer = agent.run(req.question)
    return {"answer": answer}
```

别人就可以通过 HTTP 请求调用：

```text
POST /agent/run
{
  "question": "帮我生成闲鱼商品标题"
}
```

适合：

- 做网站
- 做小程序后端
- 做内部 API
- 做 SaaS 服务

### 3. 做成产品或服务卖钱

不要直接卖“Agent 代码”。

更适合卖：

```text
用 Agent 解决某个具体问题的服务。
```

比如：

| 方向 | 可以卖什么 |
|---|---|
| 闲鱼 Agent | 选品、标题、文案、客服辅助 |
| 视频转 SOP Agent | 课程整理、SOP 生成、知识库搭建 |
| 996tokens | 报错诊断助手、模型选择助手、接入教程助手 |
| 银行 RPA + Agent | 自动化流程增强、异常判断、报告生成 |
| Obsidian 知识库 Agent | 个人知识库整理和问答 |

我的落地路径：

```text
1. 先本地脚本跑通
2. 再做成 FastAPI 接口
3. 再接一个简单网页
4. 最后包装成具体服务
```

---

## 十五、这一天和我前面学习内容的关系

前面 Day03-Day08：

```text
我手写 Thought、Action、Observation。
```

现在 Day10：

```text
smolagents 帮我封装这些流程。
```

以前：

```python
action = {
    "action": "get_weather",
    "action_input": {
        "city": "苏州"
    }
}
```

现在 CodeAgent 可能直接生成：

```python
weather = get_weather(city="苏州")
final_answer(weather)
```

以前是我手动决定调用哪个函数。

现在是：

```text
模型决定写什么代码，
框架执行代码，
工具返回结果，
Agent 继续下一步。
```

---

## 十六、今日核心总结

今天最重要的是搞清楚：

```text
smolagents 是一个轻量 Agent 框架。
CodeAgent 的 Action 是 Python 代码。
JSON Agent 的 Action 是 JSON 工具调用。
CodeAgent 更适合复杂、多步骤、需要循环和计算的任务。
tools 是提前注册给 Agent 使用的函数。
agent.run() 是启动智能体执行任务的入口。
```

一句话总结：

```text
JSON Agent 是模型发工具调用指令。
CodeAgent 是模型写 Python 代码来调用工具和完成任务。
```

---

## 十七、今日金句

我前面是在学习 Agent 的底层动作。

今天开始，我是在学习如何用框架把这些动作组织成真正可用的智能体。
