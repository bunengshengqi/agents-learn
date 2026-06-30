# 第19天：LlamaIndex 智能体与 AgentWorkflow

> 对应课程：Hugging Face Agents Course / Unit 2.2 / LlamaIndex Agents  
> 课程链接：https://huggingface.co/learn/agents-course/zh-CN/unit2/llama-index/agents  
> 主题：FunctionAgent、ReActAgent、AgentWorkflow、QueryEngineTool、Agentic RAG、多智能体系统  
> 日期：2026-06-30

---

## 0. 这一节到底在讲什么？

第17天我们学的是：

```text
LlamaIndex 组件
  ↓
Reader 读取文档
  ↓
切分与 embedding
  ↓
Index / VectorStoreIndex
  ↓
QueryEngine
  ↓
RAG 问答
```

第18天我们学的是：

```text
把能力包装成工具

FunctionTool
QueryEngineTool
ToolSpecs
Utility Tools
```

第19天继续往前走：

```text
工具已经准备好了
  ↓
现在要让 Agent 自己决定什么时候调用哪个工具
  ↓
必要时还能在多个 Agent 之间交接任务
```

所以第19天的核心是：

> **LlamaIndex 的 AgentWorkflow 如何让智能体使用工具完成任务。**

一句话总结：

```text
第17天：搭 RAG 能力。
第18天：把 RAG / 函数 / 外部能力包装成工具。
第19天：让智能体使用这些工具，甚至组织多个智能体协作。
```

---

# 1. 图片和第18天有什么联系？

第18天的主题是“工具”。

也就是：

```text
FunctionTool：把 Python 函数变成工具
QueryEngineTool：把 RAG 查询引擎变成工具
ToolSpecs：一组现成服务工具
Utility Tools：帮助处理大型工具输出
```

第19天的图片是在回答：

> 工具准备好之后，谁来决定用哪个工具？

答案是：

```text
Agent / AgentWorkflow
```

## 1.1 图1和第18天的关系

图1列出了三类智能体：

```text
1. 函数调用智能体
2. ReAct 智能体
3. 高级自定义智能体
```

这三类智能体都要依赖工具。

区别在于：

| 智能体类型 | 怎么调用工具 | 和第18天的关系 |
|---|---|---|
| 函数调用智能体 | 使用模型原生 function calling / tool calling API | 第18天定义的工具会被转成函数 schema |
| ReAct 智能体 | 用 Thought / Action / Observation 循环调用工具 | 第18天的工具作为 Action 被调用 |
| 高级自定义智能体 | 用更复杂的 workflow 和定制逻辑 | 仍然需要工具作为外部能力入口 |

所以图1不是新概念孤立出现，而是第18天工具系统的“使用者”。

可以理解成：

```text
第18天：造工具
第19天：让智能体用工具
```

## 1.2 图2和第18天的关系

图2讲的是 Agentic RAG。

图中 Alfred 可以使用：

```text
RAG pipeline tool
External API
Web Search
Direct LLM Response
```

这里的 RAG pipeline tool，本质上就是第18天讲过的：

```text
QueryEngineTool
```

也就是说：

```text
第17天：QueryEngine 可以基于知识库回答问题
第18天：QueryEngineTool 把 QueryEngine 包装成工具
第19天：AgentWorkflow 让 Agent 自主决定是否调用 QueryEngineTool
```

这就是从 RAG 到 Agentic RAG 的过渡。

---

# 2. 初始化智能体代码是什么意思？

课程代码：

```python
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.core.tools import FunctionTool


def multiply(a: int, b: int) -> int:
    """Multiplies two integers and returns the resulting integer"""
    return a * b


llm = HuggingFaceInferenceAPI(model_name="Qwen/Qwen2.5-Coder-32B-Instruct")

agent = AgentWorkflow.from_tools_or_functions(
    [FunctionTool.from_defaults(multiply)],
    llm=llm
)
```

这段代码做了 4 件事。

---

## 2.1 定义一个普通 Python 函数

```python
def multiply(a: int, b: int) -> int:
    """Multiplies two integers and returns the resulting integer"""
    return a * b
```

这原本只是一个普通函数。

它有几个重要信息：

```text
函数名：multiply
参数：a: int, b: int
返回值：int
docstring：说明这个函数用于乘法
```

这些信息对 Agent 很重要。

因为 Agent 需要知道：

```text
这个工具叫什么？
它能做什么？
需要传什么参数？
什么时候该调用？
```

---

## 2.2 用 FunctionTool 把函数包装成工具

```python
FunctionTool.from_defaults(multiply)
```

这一步的意思是：

```text
把 multiply 这个 Python 函数变成 LlamaIndex Agent 可以调用的工具。
```

`from_defaults` 会自动读取：

```text
函数名
参数类型注解
docstring
```

然后生成工具 schema。

如果底层模型支持函数调用 API，这些 schema 会帮助模型生成结构化工具调用。

---

## 2.3 初始化 LLM

```python
llm = HuggingFaceInferenceAPI(model_name="Qwen/Qwen2.5-Coder-32B-Instruct")
```

这里是创建一个模型对象。

课程用的是 Hugging Face Inference API。

如果换成你本地项目里的 OpenAI-compatible API，思路一样，只是 LLM 类不同。例如你前面 Day16 代码里用的是：

```python
from llama_index.llms.openai_like import OpenAILike
```

核心不是 Hugging Face，而是：

```text
AgentWorkflow 需要一个 LLM 来做决策。
```

---

## 2.4 用 AgentWorkflow 创建智能体

```python
agent = AgentWorkflow.from_tools_or_functions(
    [FunctionTool.from_defaults(multiply)],
    llm=llm
)
```

这一步创建了一个能使用工具的智能体工作流。

可以理解成：

```text
AgentWorkflow = LLM + 工具列表 + 调用工具的控制流程
```

用户问：

```text
What is 2 times 2?
```

AgentWorkflow 会让 LLM 判断：

```text
这是乘法问题
  ↓
应该调用 multiply 工具
  ↓
参数是 a=2, b=2
  ↓
工具返回 4
  ↓
最终回答用户
```

---

# 3. FunctionAgent 和 ReActAgent 怎么理解？

课程提到：

> 当前实现中，智能体会自动使用函数调用 API（如果可用），或标准的 ReAct 智能体循环。

这句话的意思是：

```text
如果模型支持 tool calling / function calling，就优先用结构化函数调用。
如果模型不支持，就用 ReAct 的文本推理循环。
```

---

## 3.1 函数调用智能体

函数调用智能体适合支持工具调用 API 的模型。

它的特点是：

```text
模型不是随便输出一段自然语言
而是根据工具 schema 输出结构化调用
```

例如：

```json
{
  "tool": "multiply",
  "arguments": {
    "a": 2,
    "b": 2
  }
}
```

优点：

- 工具调用格式稳定；
- 参数更容易校验；
- 不需要太多提示词技巧；
- 更适合生产环境。

缺点：

- 需要模型和 API 支持 function calling / tool calling；
- 不同模型和中转 API 的兼容程度不一样。

---

## 3.2 ReAct 智能体

ReAct 是：

```text
Reasoning + Acting
推理 + 行动
```

典型循环是：

```text
Thought：我需要计算 2 * 2
Action：调用 multiply
Observation：工具返回 4
Thought：我已经得到答案
Answer：2 times 2 is 4
```

优点：

- 适用范围广；
- 只要模型能聊天或文本生成就能用；
- 推理过程更容易观察；
- 适合复杂推理任务。

缺点：

- 输出格式可能不稳定；
- 需要更好的提示词约束；
- 通常比函数调用更啰嗦。

---

## 3.3 图1怎么理解

图1列出的三类智能体可以这样记：

```text
FunctionAgent：模型原生会调工具，格式更稳。
ReActAgent：模型通过思考-行动-观察循环调工具，兼容性更强。
高级自定义智能体：你自己定制 workflow，适合复杂业务。
```

选择建议：

```text
模型支持函数调用 API -> 优先 FunctionAgent
模型不稳定或不支持函数调用 -> 用 ReActAgent
业务流程很复杂 -> 自定义 Workflow
```

---

# 4. await 和 Context 是什么意思？

课程代码：

```python
response = await agent.run("What is 2 times 2?")
```

这里的 `await` 说明：

```text
LlamaIndex 的 AgentWorkflow 是异步运行的。
```

在 Notebook / Colab 里可以直接写：

```python
response = await agent.run("...")
```

如果是在普通 Python 文件里，通常要写：

```python
import asyncio

async def main():
    response = await agent.run("What is 2 times 2?")
    print(response)

asyncio.run(main())
```

---

## 4.1 默认无状态是什么意思？

课程代码：

```python
response = await agent.run("What is 2 times 2?")
```

默认情况下，Agent 不记得之前对话。

也就是说：

```text
第一轮：My name is Bob.
第二轮：What was my name again?
```

如果没有上下文，Agent 不一定知道你叫 Bob。

---

## 4.2 Context 是什么？

课程代码：

```python
from llama_index.core.workflow import Context

ctx = Context(agent)

response = await agent.run("My name is Bob.", ctx=ctx)
response = await agent.run("What was my name again?", ctx=ctx)
```

`Context` 的作用是：

```text
保存同一个 workflow 的状态和历史信息。
```

它适合：

- 聊天机器人；
- 需要跨多轮记忆的任务；
- 长任务进度追踪；
- 多轮工具调用；
- 多智能体交接。

可以理解成：

```text
AgentWorkflow = 执行流程
Context = 这次会话的记忆和状态
```

---

# 5. QueryEngineTool 代码是什么意思？

课程代码：

```python
from llama_index.core.tools import QueryEngineTool

query_engine = index.as_query_engine(llm=llm, similarity_top_k=3)

query_engine_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="name",
    description="a specific description",
    return_direct=False,
)

query_engine_agent = AgentWorkflow.from_tools_or_functions(
    [query_engine_tool],
    llm=llm,
    system_prompt="You are a helpful assistant that has access to a database containing persona descriptions. "
)
```

这段代码的核心是：

> **把一个 RAG QueryEngine 包装成 Agent 可以调用的工具。**

---

## 5.1 `index.as_query_engine(...)`

```python
query_engine = index.as_query_engine(
    llm=llm,
    similarity_top_k=3
)
```

这一步把索引变成查询引擎。

其中：

```text
index：已经建立好的文档索引
llm：用于生成回答的大模型
similarity_top_k=3：每次查询时取最相关的 3 个文本片段
```

底层大概会做：

```text
用户问题
  ↓
转换成检索请求
  ↓
从 index 中找出最相关的 3 个 Node
  ↓
把问题 + Node 内容交给 LLM
  ↓
生成答案
```

---

## 5.2 `QueryEngineTool.from_defaults(...)`

```python
query_engine_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="name",
    description="a specific description",
    return_direct=False,
)
```

这一步是把 QueryEngine 包装成工具。

参数含义：

| 参数 | 含义 |
|---|---|
| `query_engine` | 要包装的 RAG 查询引擎 |
| `name` | 工具名称，Agent 根据它识别工具 |
| `description` | 工具描述，告诉 Agent 什么时候该用它 |
| `return_direct` | 是否直接把工具结果返回给用户 |

最关键的是 `name` 和 `description`。

如果描述太模糊：

```python
description="a specific description"
```

Agent 就不容易判断什么时候调用这个工具。

真实项目里应该写得更具体：

```python
query_engine_tool = QueryEngineTool.from_defaults(
    query_engine=query_engine,
    name="persona_database",
    description=(
        "用于查询人物设定数据库。"
        "当用户询问 persona、角色背景、人物偏好、人物描述时使用。"
    ),
    return_direct=False,
)
```

---

## 5.3 `return_direct=False`

`return_direct=False` 表示：

```text
工具返回结果后，不一定马上原样返回给用户；
Agent 可以继续加工、总结、判断或调用其他工具。
```

如果设成：

```python
return_direct=True
```

意思更接近：

```text
工具结果就是最终答案，直接返回。
```

在 Agentic RAG 里，通常先用 `False`，因为 Agent 可能需要：

- 综合多个工具结果；
- 对 RAG 结果做解释；
- 再调用外部 API；
- 再调用计算工具；
- 用更适合用户的语言回答。

---

## 5.4 `AgentWorkflow.from_tools_or_functions(...)`

```python
query_engine_agent = AgentWorkflow.from_tools_or_functions(
    [query_engine_tool],
    llm=llm,
    system_prompt="You are a helpful assistant that has access to a database containing persona descriptions. "
)
```

这一步创建一个可以使用 RAG 工具的 Agent。

流程是：

```text
用户提问
  ↓
Agent 阅读 system_prompt 和工具描述
  ↓
判断是否需要查 persona database
  ↓
如果需要，调用 query_engine_tool
  ↓
QueryEngine 执行 RAG
  ↓
Agent 根据 RAG 结果回答
```

---

# 6. 为什么 QueryEngineTool 是 RAG 智能体的关键？

传统 RAG 是：

```text
用户问问题
  ↓
系统固定执行检索
  ↓
LLM 基于检索结果回答
```

Agentic RAG 是：

```text
用户问问题
  ↓
Agent 判断是否需要检索
  ↓
如果需要，调用 QueryEngineTool
  ↓
如果还需要其他信息，调用其他工具
  ↓
综合回答
```

区别在于：

| 类型 | 谁决定是否检索 | 能否调用其他工具 |
|---|---|---|
| 传统 RAG | 程序固定流程 | 通常不能 |
| Agentic RAG | Agent 自主判断 | 可以 |

这就是图2的意思。

图2里 Alfred 不是只能做 RAG。

它可以在这些能力之间选择：

```text
RAG pipeline tool
External API
Web Search
Direct LLM Response
```

如果用户问：

```text
根据我的资料，Alfred 的晚宴安排要注意什么？
```

Agent 应该调用 RAG 工具。

如果用户问：

```text
5 + 3 等于多少？
```

Agent 可以调用计算工具，或者直接回答。

如果用户问：

```text
今天某个实时信息是什么？
```

Agent 可能调用 Web Search 或 External API。

所以 QueryEngineTool 的核心价值是：

```text
它让“查知识库”成为 Agent 可以主动选择的一项能力。
```

---

# 7. 多智能体代码是什么意思？

课程代码：

```python
from llama_index.core.agent.workflow import (
    AgentWorkflow,
    FunctionAgent,
    ReActAgent,
)


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b


calculator_agent = ReActAgent(
    name="calculator",
    description="Performs basic arithmetic operations",
    system_prompt="You are a calculator assistant. Use your tools for any math operation.",
    tools=[add, subtract],
    llm=llm,
)

query_agent = ReActAgent(
    name="info_lookup",
    description="Looks up information about XYZ",
    system_prompt="Use your tool to query a RAG system to answer information about XYZ",
    tools=[query_engine_tool],
    llm=llm
)

agent = AgentWorkflow(
    agents=[calculator_agent, query_agent],
    root_agent="calculator"
)

response = await agent.run(user_msg="Can you add 5 and 3?")
```

这段代码创建了一个多智能体 workflow。

---

## 7.1 `add` 和 `subtract`

```python
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

```python
def subtract(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b
```

这是两个普通 Python 函数。

在 `ReActAgent` 里，它们会被当成工具使用。

---

## 7.2 `calculator_agent`

```python
calculator_agent = ReActAgent(
    name="calculator",
    description="Performs basic arithmetic operations",
    system_prompt="You are a calculator assistant. Use your tools for any math operation.",
    tools=[add, subtract],
    llm=llm,
)
```

这个 Agent 的职责是：

```text
做基础算术。
```

它有：

```text
名字：calculator
描述：Performs basic arithmetic operations
系统提示：遇到数学计算就用工具
工具：add, subtract
模型：llm
```

---

## 7.3 `query_agent`

```python
query_agent = ReActAgent(
    name="info_lookup",
    description="Looks up information about XYZ",
    system_prompt="Use your tool to query a RAG system to answer information about XYZ",
    tools=[query_engine_tool],
    llm=llm
)
```

这个 Agent 的职责是：

```text
查资料。
```

它有一个 RAG 工具：

```text
query_engine_tool
```

也就是前面包装好的 QueryEngineTool。

---

## 7.4 `AgentWorkflow`

```python
agent = AgentWorkflow(
    agents=[calculator_agent, query_agent],
    root_agent="calculator"
)
```

这一步创建多智能体系统。

含义是：

```text
系统里有两个 Agent：
1. calculator
2. info_lookup

默认从 calculator 开始处理任务。
```

`root_agent="calculator"` 表示：

```text
用户消息先交给 calculator。
```

如果 calculator 发现任务不属于自己，workflow 可以把任务交接给其他 Agent。

---

# 8. 智能体之间怎么通信？

这是这一节最容易误解的地方。

多智能体不是两个 Agent 像人一样随便私聊。

更准确地说：

```text
AgentWorkflow 维护一个统一的执行流程和上下文。
每个 Agent 有自己的名称、描述、系统提示和工具。
Workflow 根据当前任务、Agent 描述和运行状态，决定当前由哪个 Agent 处理。
必要时发生 handoff，把任务交接给另一个 Agent。
```

---

## 8.1 它们不是怎么通信的？

不是这样：

```text
calculator_agent 直接网络调用 query_agent
query_agent 私下发消息给 calculator_agent
两个 Agent 自己无限聊天
```

这不是 LlamaIndex 多智能体的核心模型。

---

## 8.2 它们实际怎么协作？

更像这样：

```text
用户消息
  ↓
AgentWorkflow 接收
  ↓
root_agent 先处理
  ↓
当前 Agent 根据任务和可用工具做判断
  ↓
如果自己能处理，调用自己的工具并回答
  ↓
如果另一个 Agent 更合适，发生任务交接
  ↓
新的 Agent 接着处理同一个 workflow 上下文
  ↓
最终输出响应
```

核心中介是：

```text
AgentWorkflow + Context
```

也就是说：

```text
Agent 之间的通信不是点对点私聊，
而是通过 workflow 的状态、事件、上下文和任务交接机制完成。
```

---

## 8.3 名称和描述为什么重要？

多智能体系统能不能正确交接，很大程度取决于：

```text
name
description
system_prompt
tools
```

例如：

```python
calculator_agent = ReActAgent(
    name="calculator",
    description="Performs basic arithmetic operations",
    ...
)
```

这个描述告诉 workflow：

```text
涉及算术运算时，calculator 更合适。
```

```python
query_agent = ReActAgent(
    name="info_lookup",
    description="Looks up information about XYZ",
    ...
)
```

这个描述告诉 workflow：

```text
涉及 XYZ 资料查询时，info_lookup 更合适。
```

如果描述写得含糊：

```text
description="helpful agent"
```

那系统就很难判断谁该处理什么。

---

## 8.4 实现原则是什么？

多智能体实现原则可以总结成 5 条。

### 1. 职责边界清晰

每个 Agent 只负责一类任务。

例如：

```text
calculator：只负责计算
info_lookup：只负责查资料
planner：只负责制定计划
writer：只负责写作
reviewer：只负责检查
```

### 2. 工具归属清晰

不要把所有工具都塞给一个 Agent。

应该是：

```text
会计算的 Agent 拿计算工具
会查资料的 Agent 拿 QueryEngineTool
会搜索的 Agent 拿 Web Search
会调用业务系统的 Agent 拿 API Tool
```

### 3. 描述要能帮助路由

`description` 不是给人看的装饰文字，而是给 LLM / workflow 判断职责用的。

应该写清：

```text
这个 Agent 擅长什么
什么时候应该交给它
什么时候不应该交给它
```

### 4. root_agent 负责入口

`root_agent` 是默认入口。

如果任务总是先要判断类型，可以让 root_agent 做调度。

如果任务主要是某一类，就让最常用的 Agent 做 root。

### 5. 用 Context 维护状态

复杂任务和多轮任务应该使用 Context。

否则每次调用都是无状态的，Agent 不容易记住之前的交互和中间结果。

---

# 9. Day19 和 Day17 / Day18 的完整关系

可以把这三天串成一条线：

```text
Day17：组件与 QueryEngine

你的数据
  ↓
Reader
  ↓
Index
  ↓
QueryEngine
  ↓
RAG 问答
```

```text
Day18：工具系统

QueryEngine
  ↓
QueryEngineTool
  ↓
Agent 可调用的工具
```

```text
Day19：智能体系统

FunctionTool / QueryEngineTool / API Tool / Search Tool
  ↓
AgentWorkflow
  ↓
FunctionAgent / ReActAgent
  ↓
单智能体或多智能体协作
  ↓
Agentic RAG
```

所以第19天不是重新学一套东西，而是在前两天基础上往上叠：

```text
数据能力 -> 工具能力 -> 智能体调度能力
```

---

# 10. 实际开发里怎么用？

如果你要做一个 Obsidian 笔记助手，可以这样设计：

## 10.1 传统 RAG 版本

```text
用户提问
  ↓
固定查询 Obsidian 笔记索引
  ↓
LLM 基于检索结果回答
```

适合：

```text
只做知识库问答
```

## 10.2 Agentic RAG 版本

```text
用户提问
  ↓
Agent 判断问题类型
  ↓
如果问笔记内容，调用 QueryEngineTool
  ↓
如果问日期，调用日历工具
  ↓
如果需要计算，调用计算工具
  ↓
如果需要搜索最新信息，调用 Web Search
  ↓
综合答案
```

适合：

```text
不只是查资料，还要完成任务
```

## 10.3 多智能体版本

```text
root_agent：判断任务类型
notes_agent：查询 Obsidian 笔记
calendar_agent：查询日历
writer_agent：整理成文章或计划
reviewer_agent：检查答案是否忠实于资料
```

适合：

```text
任务复杂、工具多、流程长
```

---

# 11. 今天要记住的核心结论

今天最重要的不是背代码，而是理解层级：

```text
FunctionTool = 把普通函数变成工具
QueryEngineTool = 把 RAG 查询能力变成工具
AgentWorkflow = 让 Agent 使用工具完成任务
FunctionAgent = 适合支持函数调用 API 的模型
ReActAgent = 适合更通用的模型，通过 Thought / Action / Observation 工作
Context = 保存跨轮状态和 workflow 记忆
多智能体 = 多个职责清晰的 Agent 在同一个 Workflow 下协作
```

最关键的一句话：

```text
第19天讲的是：当工具已经准备好之后，智能体如何选择、调用、组合这些工具。
```

---

# 12. 易混淆点

## 12.1 AgentWorkflow 不是工具

AgentWorkflow 是组织工具调用的流程。

工具是：

```text
FunctionTool
QueryEngineTool
add
subtract
Web Search
External API
```

AgentWorkflow 是：

```text
决定什么时候用哪个工具的执行框架。
```

## 12.2 QueryEngineTool 不是新的知识库

QueryEngineTool 只是把已有的 QueryEngine 包装成工具。

真正的数据和索引来自：

```text
Reader
Index
VectorStore
Embedding
```

## 12.3 多智能体不是越多越好

Agent 多了会带来：

- 路由错误；
- 成本增加；
- 延迟增加；
- 调试困难；
- 责任边界混乱。

只有当任务真的需要不同专业角色时，才适合多智能体。

## 12.4 ReAct 展示推理过程不等于一定更好

ReAct 可解释性更强，但格式更不稳定。

函数调用更结构化，但依赖模型能力。

真实开发中要根据模型和任务选择。

---

# 13. 我的理解版总结

把 Alfred 当成一个管家来看：

```text
LLM 是 Alfred 的脑子。
FunctionTool 是 Alfred 手里的简单工具，比如计算器。
QueryEngineTool 是 Alfred 的资料库查询能力。
AgentWorkflow 是 Alfred 的工作流程。
Context 是 Alfred 的记忆本。
多智能体系统是 Alfred 带着不同专长的助手团队。
```

第19天的重点就是：

```text
Alfred 不只是会回答问题，
而是能根据任务选择工具、查询资料、计算、调用 API，
必要时把任务交给更合适的专业 Agent。
```

