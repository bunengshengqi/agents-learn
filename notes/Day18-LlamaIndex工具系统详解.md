# 第18天：LlamaIndex 中的 Tools 工具系统

> 对应课程：Hugging Face Agents Course / Unit 2.2 / 在 LlamaIndex 中使用工具  
> 核心主题：FunctionTool、QueryEngineTool、ToolSpecs、Utility Tools  
> 学习目标：理解 LlamaIndex 里的工具类型，以及它们分别适合什么场景。

---

## 0. 这一节到底在讲什么？

第17天我们重点学习了：

```text
LlamaIndex 组件
  ↓
文档加载
  ↓
切分
  ↓
Embedding
  ↓
向量数据库
  ↓
VectorStoreIndex
  ↓
QueryEngine
  ↓
RAG 问答
```

第18天是在第17天的基础上继续往前走。

第17天你已经有了一个 `QueryEngine`，它能回答问题。

第18天要解决的问题是：

> 如何把这些能力变成 Agent 可以主动调用的工具？

也就是说：

```text
第17天：搭建知识库问答能力
第18天：把能力包装成 Agent 工具
```

课程里说，LlamaIndex 中主要有四种工具类型：

```text
1. FunctionTool
2. QueryEngineTool
3. ToolSpecs
4. Utility Tools
```

这四种工具本质上都是为了让 Agent 更好地使用外部能力。

---

# 1. 为什么 Agent 需要工具？

大模型本身只会生成文本。

但真实任务通常需要：

```text
查天气
查知识库
查邮件
查日历
调用数据库
读取文件
搜索网页
计算结果
整理大量返回数据
```

这些事情不是 LLM 自己凭空能完成的。

所以我们要把外部能力封装成工具。

Agent 的工作方式可以理解为：

```text
用户提出任务
  ↓
Agent 理解任务
  ↓
Agent 判断需要哪个工具
  ↓
调用工具
  ↓
拿到工具结果
  ↓
继续推理
  ↓
生成最终答案
```

工具定义越清晰，Agent 越容易正确调用。

这也是课程开头强调的重点：清晰明确的工具集对 Agent 性能很重要。

---

# 2. 四种工具类型总览

| 工具类型 | 核心作用 | 适合场景 |
|---|---|---|
| FunctionTool | 把普通 Python 函数变成工具 | 简单、明确、单步操作 |
| QueryEngineTool | 把 QueryEngine 变成工具 | RAG 知识库问答 |
| ToolSpecs | 一组预设工具集合 | Gmail、Google、Slack 等服务集成 |
| Utility Tools | 处理大数据量工具结果 | 工具返回太多内容，需要加载、索引、搜索 |

一句话记忆：

```text
FunctionTool：把一个函数变工具
QueryEngineTool：把一个知识库问答引擎变工具
ToolSpecs：把一组服务能力变工具包
Utility Tools：帮 Agent 消化大型工具输出
```

---

# 3. FunctionTool：把任意 Python 函数变成工具

## 3.1 FunctionTool 是什么？

`FunctionTool` 的作用是：

> 将一个普通 Python 函数封装成 Agent 可以调用的工具。

比如你写了一个函数：

```python
def get_weather(location: str) -> str:
    return f"{location} 今天是晴天"
```

这个函数原本只是 Python 代码。

如果把它变成 `FunctionTool`，Agent 就可以在需要查天气的时候主动调用它。

课程示例代码类似：

```python
from llama_index.core.tools import FunctionTool

def get_weather(location: str) -> str:
    """Useful for getting the weather for a given location."""
    print(f"Getting weather for {location}")
    return f"The weather in {location} is sunny"

tool = FunctionTool.from_defaults(
    get_weather,
    name="my_weather_tool",
    description="Useful for getting the weather for a given location.",
)

tool.call("New York")
```

---

## 3.2 FunctionTool 适合什么场景？

适合这些场景：

```text
1. 工具逻辑比较简单
2. 输入参数清晰
3. 输出结果明确
4. 任务是单步操作
5. 你自己能用 Python 写出来
```

例如：

```text
查天气
计算汇率
发送短信
生成订单号
查询数据库
读取本地配置
调用一个内部 API
计算 BMI
查询某个接口状态
```

---

## 3.3 FunctionTool 的关键点

FunctionTool 最重要的是三个东西：

```text
函数名
参数类型
函数描述 docstring / description
```

因为 Agent 不是靠“猜”来调用工具，而是靠工具的元数据理解：

```text
这个工具叫什么？
这个工具能做什么？
这个工具需要哪些参数？
什么时候应该调用？
```

比如：

```python
def get_weather(location: str) -> str:
    """查询指定城市的天气。参数 location 是城市名称。"""
```

这个就比下面这种好：

```python
def tool(x):
    return something
```

因为第二种对 Agent 来说太模糊了。

---

## 3.4 FunctionTool 的例子：银行业务日期判断工具

假设你在银行科技部门，经常需要判断一个日期是不是工作日。

可以写：

```python
from llama_index.core.tools import FunctionTool
from datetime import datetime

def is_workday(date: str) -> str:
    """判断给定日期是否为工作日。date 格式为 YYYY-MM-DD。"""
    dt = datetime.strptime(date, "%Y-%m-%d")
    if dt.weekday() < 5:
        return f"{date} 是工作日"
    return f"{date} 是周末，不是工作日"

workday_tool = FunctionTool.from_defaults(
    fn=is_workday,
    name="is_workday_tool",
    description="用于判断某个日期是否为工作日，输入格式为 YYYY-MM-DD。",
)
```

Agent 遇到问题：

```text
2026-07-01 是不是工作日？
```

就可以调用这个工具。

---

## 3.5 FunctionTool 的核心总结

FunctionTool 适合：

> 把你自己写的简单 Python 能力交给 Agent 使用。

它解决的是：

```text
我已经有一个 Python 函数
  ↓
我想让 Agent 可以调用它
  ↓
用 FunctionTool 包装
```

---

# 4. QueryEngineTool：把 QueryEngine 变成智能体工具

## 4.1 QueryEngineTool 是什么？

第17天我们学习了 `QueryEngine`。

它的作用是：

```text
用户问题
  ↓
检索知识库
  ↓
找到相关资料
  ↓
LLM 基于资料生成答案
```

第18天的 `QueryEngineTool` 就是把这个 QueryEngine 包装成工具。

也就是说：

```text
QueryEngine 原本只能直接 query()
QueryEngineTool 可以让 Agent 主动调用这个 query_engine
```

课程里的示例逻辑是：

```python
from llama_index.core.tools import QueryEngineTool

tool = QueryEngineTool.from_defaults(
    query_engine,
    name="some useful name",
    description="some useful description",
)
```

---

## 4.2 QueryEngineTool 适合什么场景？

适合：

```text
1. 知识库问答
2. RAG 检索增强生成
3. 文档问答
4. 让 Agent 查询某个领域资料
5. 多个知识库之间智能路由
6. 把另一个 Agent 当成工具
```

比如：

```text
查询公司制度
查询银行业务手册
查询 Obsidian 学习笔记
查询项目代码说明
查询产品文档
查询 PDF 合同
查询课程笔记
```

---

## 4.3 QueryEngineTool 和 FunctionTool 的区别

| 对比项 | FunctionTool | QueryEngineTool |
|---|---|---|
| 封装对象 | Python 函数 | QueryEngine |
| 主要用途 | 执行一个具体动作 | 查询一个知识库 |
| 是否 RAG | 不一定 | 通常是 RAG |
| 输入 | 函数参数 | 自然语言问题 |
| 输出 | 函数返回值 | 基于资料生成的答案 |

简单理解：

```text
FunctionTool = 执行动作
QueryEngineTool = 查询知识
```

---

## 4.4 QueryEngineTool 的例子：Obsidian 学习笔记问答工具

你现在每天都在整理 Agent 课程笔记到 Obsidian。

如果把 Obsidian 笔记做成知识库，就可以封装一个工具：

```python
from llama_index.core.tools import QueryEngineTool

obsidian_tool = QueryEngineTool.from_defaults(
    query_engine=obsidian_query_engine,
    name="obsidian_notes_query_tool",
    description=(
        "用于查询用户的 Obsidian 学习笔记，"
        "适合回答关于 Agent、LlamaIndex、RAG、smolagents 等学习内容的问题。"
    ),
)
```

Agent 遇到问题：

```text
第17天 QueryEngine 是什么？
```

它就会调用：

```text
obsidian_notes_query_tool
```

然后从你的 Obsidian 笔记中检索答案。

---

## 4.5 QueryEngineTool 的核心总结

QueryEngineTool 适合：

> 把一个知识库问答能力交给 Agent 使用。

它解决的是：

```text
我已经有一个 RAG QueryEngine
  ↓
我想让 Agent 可以在需要时查它
  ↓
用 QueryEngineTool 包装
```

---

# 5. ToolSpecs：社区预设工具包

## 5.1 ToolSpecs 是什么？

`ToolSpecs` 可以理解成：

> 一组已经封装好的工具集合。

课程里用了一个非常形象的比喻：

```text
ToolSpec 就像一个专业工具箱。
```

比如机械师修车，不是只用一个工具，而是一整套工具：

```text
扳手
螺丝刀
千斤顶
测压表
```

同理，一个 Gmail 工具包可能包括：

```text
搜索邮件
读取邮件
读取附件
创建草稿
发送邮件
```

你不需要自己一个个写 FunctionTool，社区已经帮你封装好了。

---

## 5.2 ToolSpecs 适合什么场景？

适合：

```text
1. 连接第三方服务
2. 某个服务需要多个相关工具
3. 不想自己从零封装 API
4. 需要一组配套能力
```

例如：

```text
Gmail
Google Calendar
Google Drive
Slack
Notion
GitHub
Wikipedia
SQL 数据库
浏览器搜索
```

---

## 5.3 ToolSpecs 示例：Gmail 工具包

课程示例：

```bash
pip install llama-index-tools-google
```

然后：

```python
from llama_index.tools.google import GmailToolSpec

tool_spec = GmailToolSpec()
tool_spec_list = tool_spec.to_tool_list()

[(tool.metadata.name, tool.metadata.description) for tool in tool_spec_list]
```

这段代码的意思是：

```text
加载 Gmail 工具规范
  ↓
转换成工具列表
  ↓
Agent 可以调用这些 Gmail 工具
```

---

## 5.4 ToolSpecs 的例子：财务助理 Agent

比如一个财务助理 Agent，它可能需要：

```text
读取 Excel
发送邮件
计算金额
查询发票
生成报表
```

如果这些都自己写 FunctionTool，会比较麻烦。

用 ToolSpecs 就可以直接引入一组成熟工具。

例如：

```text
Google Sheets ToolSpec：处理表格
Gmail ToolSpec：发送邮件
Calculator Tool：计算金额
```

然后 Agent 可以完成：

```text
读取本月报销数据
  ↓
统计异常单据
  ↓
生成邮件
  ↓
发送给负责人
```

---

## 5.5 ToolSpecs 的核心总结

ToolSpecs 适合：

> 已经有成熟第三方服务，需要一组相关工具一起使用。

它解决的是：

```text
我不想自己封装 Gmail / Google / Slack / GitHub
  ↓
社区已经有工具包
  ↓
直接安装 ToolSpec
  ↓
转换成工具列表
  ↓
交给 Agent 使用
```

---

# 6. Utility Tools：处理大量工具返回数据

## 6.1 Utility Tools 是什么？

`Utility Tools` 是一种辅助工具。

它不是为了连接某个具体服务，而是为了解决一个常见问题：

> 工具返回的数据太多，LLM 一次处理不了。

比如一个工具返回了：

```text
100 封邮件
500 条日志
1000 行网页内容
一整个 PDF
大量 API 结果
```

如果全部塞给 LLM，会出现几个问题：

```text
上下文窗口不够
token 成本很高
大量无关信息干扰回答
模型容易总结错
```

Utility Tools 就是为了解决这个问题。

---

## 6.2 课程中提到的两个 Utility Tools

课程重点提到两个：

```text
1. OnDemandToolLoader
2. LoadAndSearchToolSpec
```

---

## 6.3 OnDemandToolLoader

`OnDemandToolLoader` 的作用是：

> 把一个数据加载器变成 Agent 可以使用的工具。

它的执行过程是：

```text
调用数据加载器
  ↓
加载数据
  ↓
临时建立索引
  ↓
根据自然语言问题查询
  ↓
返回相关答案
```

适合：

```text
临时读取一个大文件
临时读取一个网页
临时读取一个数据库导出
读取大量 API 返回内容
```

---

## 6.4 LoadAndSearchToolSpec

`LoadAndSearchToolSpec` 的作用是：

> 把一个会返回大量数据的工具，拆成“加载工具”和“搜索工具”。

它会返回两个工具：

```text
加载工具：调用原始工具，并把结果建立索引
搜索工具：在索引里查询相关内容
```

这个设计很重要。

因为有些工具返回内容特别多，Agent 不应该每次都把全部结果喂给 LLM。

更合理的方式是：

```text
先加载并索引
再按问题搜索
```

---

## 6.5 Utility Tools 适合什么场景？

适合：

```text
1. 工具返回大量数据
2. 原始结果不能直接塞给 LLM
3. 需要先索引再查询
4. 希望减少 token 消耗
5. 希望提高答案相关性
```

例如：

```text
邮件搜索返回 200 封邮件
日志查询返回 10 万行日志
网页抓取返回几十页内容
PDF 读取返回几百页文本
GitHub issue 查询返回大量讨论
```

---

## 6.6 Utility Tools 的例子：日志分析工具

假设你有一个工具可以读取服务器日志。

原始工具返回：

```text
最近 7 天所有日志，共 200MB
```

如果直接给 LLM，肯定不现实。

更好的流程是：

```text
LoadAndSearchToolSpec
  ↓
先加载日志
  ↓
建立索引
  ↓
用户问：昨天 9005 端口连接失败原因是什么？
  ↓
只搜索相关日志片段
  ↓
再让 LLM 总结
```

这就是 Utility Tools 的价值。

---

# 7. 四种工具对应的四个完整例子

## 例子1：FunctionTool —— 查询银行工作日

### 场景

用户问：

```text
2026-07-01 是工作日吗？
```

### 工具类型

```text
FunctionTool
```

### 为什么用 FunctionTool？

因为这个任务是一个明确的 Python 函数逻辑：

```text
输入日期
  ↓
判断星期几
  ↓
返回是否工作日
```

### 示例代码

```python
from datetime import datetime
from llama_index.core.tools import FunctionTool

def is_workday(date: str) -> str:
    """判断给定日期是否为工作日。date 格式为 YYYY-MM-DD。"""
    dt = datetime.strptime(date, "%Y-%m-%d")
    if dt.weekday() < 5:
        return f"{date} 是工作日"
    return f"{date} 是周末，不是工作日"

workday_tool = FunctionTool.from_defaults(
    fn=is_workday,
    name="is_workday_tool",
    description="判断某个日期是否为工作日，输入格式为 YYYY-MM-DD。",
)
```

### 适合原因

```text
简单函数
明确输入
明确输出
不需要 RAG
```

---

## 例子2：QueryEngineTool —— 查询 Obsidian 学习笔记

### 场景

用户问：

```text
第17天 QueryEngine 和 RAG 是什么关系？
```

### 工具类型

```text
QueryEngineTool
```

### 为什么用 QueryEngineTool？

因为这个问题需要查询你的 Obsidian 学习笔记。

流程是：

```text
用户问题
  ↓
Obsidian 知识库
  ↓
QueryEngine 检索
  ↓
LLM 总结
```

### 示例代码

```python
from llama_index.core.tools import QueryEngineTool

obsidian_tool = QueryEngineTool.from_defaults(
    query_engine=obsidian_query_engine,
    name="obsidian_notes_query_tool",
    description="查询用户的 Obsidian 学习笔记，适合回答 Agent、RAG、LlamaIndex 等学习问题。",
)
```

### 适合原因

```text
需要查知识库
需要基于资料回答
典型 RAG 场景
```

---

## 例子3：ToolSpecs —— Gmail 邮件助理

### 场景

用户说：

```text
帮我查一下最近一周客户发来的未读邮件，并草拟回复。
```

### 工具类型

```text
ToolSpecs
```

### 为什么用 ToolSpecs？

因为 Gmail 不是一个单一操作，而是一组相关操作：

```text
搜索邮件
读取邮件
读取附件
创建草稿
发送邮件
```

这些工具可以通过 GmailToolSpec 一次性获取。

### 示例代码

```python
from llama_index.tools.google import GmailToolSpec

tool_spec = GmailToolSpec()
gmail_tools = tool_spec.to_tool_list()
```

### 适合原因

```text
第三方服务
多工具集合
社区已有封装
不必自己从零写 API
```

---

## 例子4：Utility Tools —— 处理大量邮件或日志

### 场景

用户说：

```text
帮我分析最近 1000 条系统日志，找出 9005 端口连接失败的原因。
```

### 工具类型

```text
Utility Tools
```

### 为什么用 Utility Tools？

因为 1000 条日志不能直接全部塞给 LLM。

合理流程：

```text
加载日志
  ↓
建立索引
  ↓
按问题搜索相关日志
  ↓
只把相关片段交给 LLM
  ↓
生成分析结论
```

### 适合原因

```text
数据量大
结果杂
需要二次检索
需要节省 token
```

---

# 8. 四种工具怎么选？

可以按这个判断：

```text
如果只是执行一个 Python 函数：
  用 FunctionTool

如果是查询知识库 / RAG：
  用 QueryEngineTool

如果是连接 Gmail、Google、Slack、GitHub 这类服务：
  优先找 ToolSpecs

如果工具返回的数据太大：
  用 Utility Tools 做加载、索引、搜索
```

也可以记成：

```text
动作型任务 → FunctionTool
知识型任务 → QueryEngineTool
服务型任务 → ToolSpecs
大数据处理型任务 → Utility Tools
```

---

# 9. 和前面课程的关系

## 第13天 smolagents Tool

你之前学过 smolagents 的 Tool：

```text
定义 name
定义 description
定义 inputs
实现 forward
```

它的重点是：

```text
让 Agent 可以调用一个外部能力
```

## 第17天 QueryEngine

你学了 QueryEngine：

```text
文档
  ↓
向量库
  ↓
索引
  ↓
查询引擎
```

它的重点是：

```text
让系统可以基于知识库回答问题
```

## 第18天 Tools

第18天就是把这两者合起来：

```text
外部能力
  ↓
包装成工具
  ↓
交给 Agent 使用
```

所以第18天可以理解成：

> 从“会查资料”走向“让 Agent 主动选择工具查资料”。

---

# 10. 最重要的理解

第18天最重要的是：

> 工具不是越多越好，而是越清晰越好。

因为 Agent 调工具时，主要依赖：

```text
工具名称
工具描述
参数说明
返回结果
```

如果工具描述模糊，Agent 就容易乱调用。

比如不好：

```text
name = tool1
description = useful tool
```

比较好：

```text
name = obsidian_notes_query_tool
description = 查询用户的 Obsidian 学习笔记，适合回答 Agent、RAG、LlamaIndex、smolagents 等学习问题。
```

---

# 11. 第18天总结

第18天学习的是 LlamaIndex 的工具系统。

四种工具分别是：

```text
FunctionTool：
把普通 Python 函数变成 Agent 工具。

QueryEngineTool：
把 QueryEngine 变成 Agent 可调用的 RAG 知识库工具。

ToolSpecs：
社区预设的一组工具集合，适合 Gmail、Google、Slack 等服务。

Utility Tools：
用于处理大量工具返回数据，先加载、索引，再搜索，避免 LLM 直接吃下过多无关内容。
```

最终目标是：

```text
让 Agent 不只是会聊天，
而是能选择合适工具，
查资料、用服务、处理数据，
完成真实任务。
```

---

# 12. Obsidian 复习卡片

## 卡片1：FunctionTool 是什么？

FunctionTool 可以把任意 Python 函数封装成 Agent 可以调用的工具。  
适合简单、明确、单步操作，比如查天气、计算日期、调用内部接口。

## 卡片2：QueryEngineTool 是什么？

QueryEngineTool 可以把 QueryEngine 封装成 Agent 工具。  
适合 RAG 知识库问答，比如查询 Obsidian 笔记、公司制度、业务手册。

## 卡片3：ToolSpecs 是什么？

ToolSpecs 是社区预设工具集合。  
它把某个服务的一组能力封装起来，比如 Gmail 的搜索邮件、读取邮件、发送邮件、创建草稿等。

## 卡片4：Utility Tools 是什么？

Utility Tools 用来处理大量工具输出。  
当工具返回内容太多时，它可以先加载、索引，再按问题搜索，减少 token 消耗，提高相关性。

## 卡片5：四种工具怎么选？

动作型任务用 FunctionTool。  
知识库问答用 QueryEngineTool。  
第三方服务集成用 ToolSpecs。  
大数据量工具输出用 Utility Tools。
