---
title: Day 08｜使用 smolagents 创建第一个智能体
date: 2026-06-21
tags:
  - AI-Agent
  - smolagents
  - CodeAgent
  - Tool
  - OpenAI-Compatible
  - Agent-Framework
  - Obsidian
status: in-progress
---

# Day 08｜使用 smolagents 创建第一个智能体

## 一、今天的学习主题

Day 8 的核心主题是：

```text
使用 smolagents 框架创建第一个智能体。
```

前面 7 天我们已经手写了 Agent 的底层逻辑：

```text
messages
→ LLM
→ Thought
→ Action
→ Tool
→ Observation
→ messages
→ Final Answer
```

Day 8 开始使用真正的 Agent 框架：

```text
smolagents
```

今天的重点不是再手写 `extract_action()`、`run_tool()`、`append_observation()`，而是理解：

```text
框架如何帮我们封装这些重复工作。
```

---

# 二、今天最重要的一句话

```text
smolagents 负责调度，工具负责干活，模型负责判断什么时候用哪个工具。
```

也就是说：

```text
模型：负责理解任务和决定下一步
工具：负责真正执行操作
框架：负责把模型、工具、执行循环串起来
```

---

# 三、什么是 smolagents

`smolagents` 是 Hugging Face 推出的轻量级 Agent 框架。

可以理解为：

```text
一个帮你快速构建 Agent 的 Python 工具库。
```

它帮你封装：

```text
模型调用
工具注册
工具选择
工具执行
多步循环
最终答案输出
日志打印
```

你前面 Day 7 自己写的 Dummy Agent 做了这些：

```python
call_llm()
extract_action()
run_tool()
append_observation()
run()
```

而 smolagents 会把这些底层流程封装起来。

---

# 四、smolagents 是不是主流框架

smolagents 是一个很适合学习和快速实验的轻量 Agent 框架。

但如果从企业级主流程度看，目前更常见的还有：

```text
LangGraph
LlamaIndex Agents
AutoGen
CrewAI
Semantic Kernel
OpenAI Agents SDK
```

可以这样理解：

| 框架 | 特点 |
|---|---|
| smolagents | 轻量、简单、适合学习和快速实验 |
| LangGraph | 状态图、多步骤、工程化强 |
| LlamaIndex Agents | RAG、文档、知识库强 |
| AutoGen | 多 Agent 协作 |
| CrewAI | 角色型多 Agent |

所以：

```text
smolagents 不一定是企业里最重型的框架，
但它非常适合现在这个阶段学习 Agent 框架思想。
```

---

# 五、为什么先学 Dummy Agent，再学 smolagents

因为如果直接学框架，很容易出现：

```text
代码能跑，但不知道背后发生了什么。
```

Day 7 的 Dummy Agent 让我们明白：

```text
Agent 框架底层不过是在管理：
messages、工具、模型调用、Action 解析、Observation 回填和循环。
```

Day 8 学 smolagents，就是把手写版换成框架版。

对照关系：

| Day 7 Dummy Agent | Day 8 smolagents |
|---|---|
| 自己管理 messages | 框架管理 |
| 自己解析 Action | 框架处理 |
| 自己执行工具 | 框架调用工具 |
| 自己回填 Observation | 框架管理执行结果 |
| 自己控制循环 | 框架控制 max_steps |

---

# 六、可以不用 Hugging Face API Token 吗

可以。

课程默认使用 Hugging Face 的：

```python
InferenceClientModel
```

并通过 Hugging Face Serverless API 调用模型。

但你可以使用自己的 OpenAI 兼容中转站。

你的配置是：

```text
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://your-api-domain.com/v1
OPENAI_MODEL=your-model-name
```

这和你前面几天的代码一致。

核心理解：

```text
Hugging Face API 是远程模型调用；
你自己的中转站也是远程模型调用；
只要 smolagents 的模型适配类支持 OpenAI 兼容接口，就可以使用。
```

常见思路是使用：

```python
OpenAIServerModel
```

或：

```python
LiteLLMModel
```

具体取决于你本地安装的 smolagents 版本。

---

# 七、课程里的 The Agent 代码怎么理解

课程中的核心代码大概是：

```python
final_answer = FinalAnswerTool()

model = InferenceClientModel(
    max_tokens=2096,
    temperature=0.5,
    model_id="Qwen/Qwen2.5-Coder-32B-Instruct",
)

agent = CodeAgent(
    model=model,
    tools=[final_answer],
    max_steps=6,
    verbosity_level=1,
    prompt_templates=prompt_templates,
)

GradioUI(agent).launch()
```

逐行理解：

## 1. FinalAnswerTool

```python
final_answer = FinalAnswerTool()
```

这是最终答案工具。

它告诉 Agent：

```text
当任务完成时，用这个工具输出最终答案。
```

课程里提醒：

```text
不要删除 final_answer。
```

因为 Agent 最终需要一个明确的结束方式。

---

## 2. model

```python
model = InferenceClientModel(...)
```

这是模型引擎。

课程默认使用：

```text
Qwen/Qwen2.5-Coder-32B-Instruct
```

它是一个比较强的代码模型，适合 CodeAgent。

但如果你用自己的中转站，可以把模型接入方式换成 OpenAI 兼容模型。

---

## 3. CodeAgent

```python
agent = CodeAgent(...)
```

这是创建一个代码智能体。

`CodeAgent` 的特点是：

```text
模型用 Python 代码作为 Action。
```

也就是 Day 5 学过的 Code Agent。

---

## 4. tools

```python
tools=[final_answer]
```

这里是 Agent 能用的工具列表。

如果只有：

```python
tools=[final_answer]
```

那么 Agent 几乎没有额外能力，只能最终回答。

如果加入：

```python
tools=[final_answer, DuckDuckGoSearchTool(), get_current_time_in_timezone]
```

Agent 就拥有：

```text
搜索能力
查时间能力
最终回答能力
```

所以：

```text
给 Agent 添加工具，就是给 Agent 添加能力。
```

---

## 5. max_steps

```python
max_steps=6
```

表示 Agent 最多执行 6 步。

对应 Day 6 学过的：

```text
Agent 不能无限循环，必须有步数限制。
```

---

## 6. GradioUI

```python
GradioUI(agent).launch()
```

这是启动一个网页界面。

你可以理解为：

```text
给 Agent 套一个简单 Web UI，方便用户交互。
```

---

# 八、什么是 CodeAgent

`CodeAgent` 是 smolagents 中的一个核心 Agent 类型。

它的特点是：

```text
让模型生成 Python 代码作为 Action。
```

普通 JSON Agent 可能输出：

```json
{
  "action": "get_current_time_in_timezone",
  "action_input": {
    "timezone": "Asia/Shanghai"
  }
}
```

CodeAgent 更可能生成：

```python
time = get_current_time_in_timezone("Asia/Shanghai")
final_answer(time)
```

它适合：

```text
多步骤任务
循环
条件判断
数据处理
组合多个工具
需要写代码完成的任务
```

缺点是：

```text
安全风险更高
需要限制执行环境
需要日志审计
需要权限控制
模型写错代码时需要调试
```

所以：

```text
学习、实验、内部工具可以用；
银行生产、敏感数据、自动执行必须加沙箱、权限、审计和人工确认。
```

---

# 九、Tool 的意义是什么

Tool 是 Agent 的能力来源。

模型本身只能生成文本。

工具让 Agent 可以：

```text
查询数据
搜索网页
调用 API
读取文件
处理 Excel
执行 RPA
生成图片
查询数据库
```

没有工具的 Agent：

```text
只能回答
```

有工具的 Agent：

```text
可以做事
```

所以：

```text
Agent 的能力 = 模型能力 + 工具能力
```

---

# 十、为什么工具要写类型和 docstring

课程里强调：

```python
@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
```

重点是三个东西：

```text
1. 函数名
2. 输入输出类型
3. docstring 参数说明
```

---

## 1. 函数名

```python
get_current_time_in_timezone
```

模型可以从函数名理解：

```text
这个工具是用来查询某个时区当前时间的。
```

---

## 2. 类型标注

```python
timezone: str -> str
```

含义：

```text
输入 timezone 是字符串；
返回值也是字符串。
```

如果没有类型标注，框架和模型很难判断参数该怎么传。

---

## 3. docstring

```text
timezone: A string representing a valid timezone
```

这是给模型看的参数说明。

模型看到后才知道：

```text
如果用户问“纽约现在几点”，应该传 America/New_York。
```

所以工具定义的三件套是：

```text
函数名清楚
类型标注清楚
docstring 参数说明清楚
```

---

# 十一、这些 Tool 需要自己定义吗

是的。

框架会提供一些现成工具，例如：

```text
DuckDuckGoSearchTool
图片生成工具
网页搜索工具
FinalAnswerTool
```

但真正有业务价值的工具，大量都需要你自己写。

例如你可以写：

```python
@tool
def query_customer_risk(customer_name: str) -> str:
    """查询客户风险信息。
    Args:
        customer_name: 客户名称。
    """
```

或者：

```python
@tool
def read_customer_excel(file_path: str) -> str:
    """读取客户名单 Excel。
    Args:
        file_path: Excel 文件路径。
    """
```

你的判断完全正确：

```text
不同开发场景，可以自主创造不同的 tool。
```

这正是 Agent 真正有价值的地方。

框架负责调度工具。

真正的业务能力，来自你定义的工具。

---

# 十二、你可以实现哪些工具

结合你的方向，可以设计很多工具。

## 1. 学习 / SOP Agent

```python
@tool
def summarize_text(text: str) -> str:
    """总结一段课程文字。
    Args:
        text: 需要总结的课程原文。
    """
```

```python
@tool
def generate_sop(transcript: str) -> str:
    """把视频文稿整理成 SOP。
    Args:
        transcript: 视频转写文字。
    """
```

适合：

```text
BibiGPT → Obsidian → SOP
```

---

## 2. 闲鱼选品 Agent

```python
@tool
def calculate_profit(cost: float, price: float, shipping: float) -> str:
    """计算闲鱼商品利润。
    Args:
        cost: 进货成本。
        price: 售卖价格。
        shipping: 运费。
    """
```

```python
@tool
def score_product(title: str, want_count: int, competitor_count: int) -> str:
    """评估闲鱼商品是否值得上架。
    Args:
        title: 商品标题。
        want_count: 想要人数。
        competitor_count: 竞品数量。
    """
```

---

## 3. 银行 RPA Agent

```python
@tool
def query_bdc_info(cert_no: str) -> str:
    """查询不动产抵押信息。
    Args:
        cert_no: 不动产权证号。
    """
```

```python
@tool
def check_invoice_status(invoice_no: str) -> str:
    """查询发票状态。
    Args:
        invoice_no: 发票号码。
    """
```

```python
@tool
def read_customer_excel(file_path: str) -> str:
    """读取客户名单 Excel。
    Args:
        file_path: Excel 文件路径。
    """
```

---

## 4. 996tokens 运维 Agent

```python
@tool
def check_model_price(model_name: str) -> str:
    """查询模型当前定价。
    Args:
        model_name: 模型名称。
    """
```

```python
@tool
def check_upstream_status(upstream_name: str) -> str:
    """检查上游渠道是否可用。
    Args:
        upstream_name: 上游渠道名称。
    """
```

---

# 十三、Hugging Face Space 是什么

图片中提到复制 Space。

Space 可以理解为：

```text
Hugging Face 上的在线小应用托管平台。
```

它的作用是：

```text
你把 app.py 放上去；
Hugging Face 帮你运行一个网页应用；
别人可以打开网页使用你的 Agent。
```

课程让你 Duplicate Space，是为了：

```text
不用本地搭环境，直接在线体验 Agent。
```

但你现在不一定要用 Space。

你可以本地运行：

```bash
python app.py
```

以后也可以部署到自己的服务器。

---

# 十四、使用你自己的 OpenAI 兼容配置

你的目标配置是：

```text
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://your-api-domain.com/v1
OPENAI_MODEL=your-model-name
```

思路是：

```text
框架用 smolagents；
模型用你自己的 OpenAI 兼容 API；
工具由你自己定义。
```

也就是：

```text
smolagents = Agent 框架
你的中转站 = LLM 引擎
@tool 函数 = Agent 能力
```

这条路线很适合你后面做：

```text
996tokens
闲鱼 Agent
银行 RPA Agent
视频 SOP Agent
```

---

# 十五、Day 8 今天真正要掌握什么

不要被 Space、Hugging Face token、Qwen 模型绕晕。

今天真正要掌握的是：

```text
1. smolagents 是 Agent 框架
2. CodeAgent 用代码作为 Action
3. Tool 是你给 Agent 的能力
4. 工具函数必须写清楚类型和 docstring
5. 你可以根据业务自己创造工具
6. Agent 的能力 = 模型能力 + 工具能力
7. 可以不用 Hugging Face API，改用自己的 OpenAI 兼容 API
```

---

# 十六、Day 8 代码建议

建议目录：

```text
examples/08-smolagents-first-agent/
```

建议文件：

```text
examples/08-smolagents-first-agent/
├── first_smol_agent.py
└── README.md
```

代码目标：

```text
1. 使用 smolagents 创建 CodeAgent
2. 使用你自己的 OpenAI 兼容 API
3. 定义一个自己的工具
4. 让 Agent 调用工具完成任务
```

不要一上来做复杂项目。

先跑通：

```text
用户：现在 Asia/Shanghai 几点？
Agent：调用 get_current_time_in_timezone 工具
工具返回结果
Agent 输出最终答案
```

---

# 十七、Day 8 验收问题

今天结束前，必须能回答：

1. smolagents 是什么？
2. smolagents 和 Dummy Agent 有什么区别？
3. 为什么要使用框架？
4. CodeAgent 是什么？
5. CodeAgent 和 JSON Agent 有什么区别？
6. Tool 在 smolagents 中是什么？
7. 为什么工具函数必须写类型标注？
8. 为什么 docstring 很重要？
9. 工具是不是都要自己定义？
10. 你可以为自己的业务定义哪些工具？
11. Hugging Face Space 是什么？
12. 可以不用 Hugging Face API token，改用自己的 OpenAI 兼容 API 吗？
13. `tools=[final_answer]` 说明什么？
14. 为什么添加工具就等于给 Agent 添加能力？

---

# 十八、今日结论

Day 8 的核心是：

```text
从手写 Agent，进入框架 Agent。
```

最重要的理解：

```text
模型负责判断；
工具负责干活；
smolagents 负责调度。
```

一句话总结：

```text
你以前写过的 RPA 脚本、爬虫、Excel 处理、API 查询，都可以慢慢包装成 smolagents 的 tools。
```

这就是从“脚本工程师”走向“Agent 工程师”的关键一步。

