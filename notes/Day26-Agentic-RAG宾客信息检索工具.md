---
title: Day26 - Agentic RAG 宾客信息检索工具
date: 2026-07-07
tags:
  - AI-Agent
  - Agentic-RAG
  - RAG
  - smolagents
  - LlamaIndex
  - LangGraph
  - HuggingFace-Agent-Course
---

# 第26天：Agentic RAG 宾客信息检索工具

> 主题：如何为 Alfred 创建一个可检索宾客信息的 RAG 工具？
>
> 课程来源：
> - Hugging Face Agents Course：创建宾客信息检索生成（RAG）工具
>
> 数据集：
> - `agents-course/unit3-invitees`
>
> 配套代码：
> - `examples/26-agentic-rag-invitees/`

---

## 0. 今天先抓住一句话

**第 26 天是在第 25 天 Agentic RAG 概念基础上，真正做出第一个“宾客信息检索工具”。**

第 25 天讲的是：

```text
为什么 Alfred 需要 Agentic RAG？
```

第 26 天开始落地：

```text
把宾客数据集加载进来
  ↓
转换成适合检索的 Document
  ↓
创建检索器
  ↓
包装成 Agent 可以调用的工具
  ↓
把工具交给 Alfred
```

这节的核心不是“写一个很复杂的 Agent”，而是：

```text
先做出一个可靠的 RAG 工具。
```

---

## 1. 先回答你的问题：图片上的三个框架是什么意思？

图片里出现了三个标签：

```text
smolagents
llama-index
langgraph
```

这不是说加载数据集时必须同时使用三种框架。

它的意思是：

```text
教材提供了三种实现版本，你任选一种框架跟着做即可。
```

也就是说：

- 如果你正在学 `smolagents`，就点 `smolagents` 标签看对应代码；
- 如果你正在学 `LlamaIndex`，就点 `llama-index` 标签看对应代码；
- 如果你正在学 `LangGraph`，就点 `langgraph` 标签看对应代码。

### 1.1 整个智能体是用这三个框架一起实现的吗？

不是。

更准确地说：

```text
课程是同一个用例，给出三套框架实现方案。
```

你可以理解成：

```text
同一道题，提供三种解法。
```

不是：

```text
一个 Agent 同时混用三种框架。
```

当然，在真实项目里你也可以混用工具库，例如：

- 用 `datasets` 加载 Hugging Face 数据集；
- 用 `langchain_core.documents.Document` 表示文档；
- 用 `BM25Retriever` 做检索；
- 用 `smolagents` 包装工具；
- 或者用 `LangGraph` 编排流程。

但课程这里的标签页不是要求你同时用三套 Agent 框架。

### 1.2 这三个框架分别承担什么风格？

| 框架 | 更适合什么 |
|---|---|
| `smolagents` | 快速创建工具型 Agent，代码简洁，适合教学和轻量实验 |
| `LlamaIndex` | 文档索引、RAG、知识库问答能力强 |
| `LangGraph` | 复杂流程控制、状态管理、人类介入、多步骤工作流 |

这节课的核心任务是“宾客信息检索工具”，所以三种框架都能做。

但它们的表达方式不同。

---

## 2. 这节课要解决什么问题？

Alfred 正在筹备一场盛大的晚会。

他需要随时回答关于宾客的问题：

```text
Lady Ada Lovelace 是谁？
她和主办方是什么关系？
她的邮箱是什么？
Dr. Nikola Tesla 有什么适合聊的话题？
Marie Curie 的背景是什么？
```

这些信息不是大模型训练知识的一部分。

它们来自一个特定数据集：

```text
agents-course/unit3-invitees
```

所以 Alfred 需要一个工具：

```text
输入：宾客姓名或关系
输出：相关宾客信息
```

这就是本节要创建的：

```text
GuestInfoRetrieverTool
```

---

## 3. 为什么这里需要 RAG？

教材给了三个理由。

### 3.1 宾客名单是私有数据

大模型不会天然知道你的晚会宾客名单。

例如：

```text
Ada Lovelace 是这场晚会的 best friend。
Nikola Tesla 是 old friend from university days。
```

这些是活动私有数据，不是模型内置知识。

### 3.2 宾客信息可能更新

现实中，宾客信息可能随时变化：

- 邮箱变了；
- 关系变了；
- 饮食偏好变了；
- 禁忌话题变了；
- 近期成就变了。

如果只靠模型记忆，信息会过时。

### 3.3 需要精确查找细节

例如邮箱：

```text
ada.lovelace@example.com
nikola.tesla@gmail.com
marie.curie@example.com
```

这类信息不能靠模型猜。

必须从数据源检索。

所以：

```text
RAG = 让 Alfred 基于可靠数据源回答宾客问题。
```

---

## 4. 数据集是什么？

数据集地址：

[agents-course/unit3-invitees](https://huggingface.co/datasets/agents-course/unit3-invitees)

数据集很小，只有 3 行。

字段包括：

| 字段 | 含义 |
|---|---|
| `name` | 宾客姓名 |
| `relation` | 与主办方关系 |
| `description` | 简要传记、背景或趣闻 |
| `email` | 邀请函发送和后续联系邮箱 |

数据集中包含：

| name | relation | email |
|---|---|---|
| Ada Lovelace | best friend | `ada.lovelace@example.com` |
| Dr. Nikola Tesla | old friend from university days | `nikola.tesla@gmail.com` |
| Marie Curie | no relation | `marie.curie@example.com` |

课程也提醒：

```text
真实场景中可以扩展更多字段。
```

例如：

- 饮食偏好；
- 礼物兴趣；
- 禁忌话题；
- 过敏信息；
- 座位偏好；
- 最近成就；
- 适合的寒暄话题。

---

## 5. 项目结构

课程建议采用结构化 Python 项目。

它提到三个文件：

```text
tools.py
retriever.py
app.py
```

含义：

| 文件 | 作用 |
|---|---|
| `tools.py` | 为智能体提供辅助工具 |
| `retriever.py` | 实现知识访问和检索功能 |
| `app.py` | 整合所有组件，形成完整智能体 |

这是一种很好的工程拆分方式。

不要把所有代码写在一个文件里。

更推荐：

```text
数据加载
  ↓
检索器
  ↓
工具封装
  ↓
Agent 集成
```

---

## 6. 第一步：加载并预处理数据集

课程首先加载 Hugging Face 数据集：

```python
import datasets

guest_dataset = datasets.load_dataset(
    "agents-course/unit3-invitees",
    split="train",
)
```

然后把每条数据转换成 `Document`：

```python
from langchain_core.documents import Document

docs = [
    Document(
        page_content="\n".join([
            f"Name: {guest['name']}",
            f"Relation: {guest['relation']}",
            f"Description: {guest['description']}",
            f"Email: {guest['email']}",
        ]),
        metadata={"name": guest["name"]},
    )
    for guest in guest_dataset
]
```

### 6.1 为什么要转成 Document？

因为检索器通常不直接处理原始字典，而是处理文档对象。

一个 `Document` 通常有两部分：

```text
page_content：可检索的文本内容
metadata：额外元数据
```

例如：

```text
page_content:
Name: Ada Lovelace
Relation: best friend
Description: ...
Email: ada.lovelace@example.com

metadata:
{"name": "Ada Lovelace"}
```

这样做有几个好处：

- 检索器可以直接对 `page_content` 建索引；
- 元数据可以保存姓名、来源、ID；
- 后续可以追踪结果来自哪条记录；
- 不同框架都容易兼容这种文档格式。

### 6.2 加载和预处理是不是三种框架都用？

不是。

图片上三个标签表示：

```text
课程分别给了 smolagents / llama-index / langgraph 三个版本。
```

如果选择 `smolagents`，你就看 `smolagents` 标签里的代码。

如果选择 `langgraph`，你就看 `langgraph` 标签里的代码。

不是三套一起用。

不过很多底层库可能是共享的，比如：

- `datasets` 用来加载数据集；
- `Document` 用来表示文档；
- `BM25Retriever` 用来检索。

这些是工具库，不等于 Agent 框架本身。

---

## 7. 第二步：创建检索工具

课程创建了一个工具：

```python
class GuestInfoRetrieverTool(Tool):
    name = "guest_info_retriever"
    description = "Retrieves detailed information about gala guests based on their name or relation."
    inputs = {
        "query": {
            "type": "string",
            "description": "The name or relation of the guest you want information about."
        }
    }
    output_type = "string"
```

这个工具的含义：

```text
名字：guest_info_retriever
用途：根据姓名或关系检索晚会宾客信息
输入：query
输出：字符串
```

### 7.1 为什么工具名和描述很重要？

因为 Agent 选择工具时会看工具描述。

工具描述如果写得模糊，模型就不知道什么时候该用。

不好的描述：

```text
search information
```

好的描述：

```text
Retrieves detailed information about gala guests based on their name or relation.
```

这会告诉 Agent：

```text
当问题涉及宾客姓名、关系、邮箱、背景时，应该调用这个工具。
```

---

## 8. BM25Retriever 是什么？

课程使用：

```python
from langchain_community.retrievers import BM25Retriever

self.retriever = BM25Retriever.from_documents(docs)
```

BM25 是一种经典关键词检索算法。

它适合：

- 小型文本数据；
- 关键词明确的问题；
- 人名、邮箱、关系这种精确匹配；
- 不想先做 embedding 的轻量场景。

### 8.1 BM25 的优点

- 不需要向量模型；
- 不需要 embedding API；
- 速度快；
- 对关键词匹配友好；
- 对小数据集很合适。

### 8.2 BM25 的不足

- 不擅长语义相似；
- 同义词召回能力弱；
- 问法变化大时可能漏掉；
- 复杂语义问题不如向量检索。

课程也提示：

```text
更高级的语义搜索可以考虑 sentence-transformers 等 embedding 检索器。
```

---

## 9. 第三步：把工具交给 Alfred

课程里使用 `smolagents` 的示例：

```python
from smolagents import CodeAgent, InferenceClientModel

model = InferenceClientModel()

alfred = CodeAgent(
    tools=[guest_info_tool],
    model=model,
)
```

然后查询：

```python
response = alfred.run(
    "Tell me about our guest named 'Lady Ada Lovelace'."
)
```

这里 Alfred 的工作方式是：

```text
看到用户问宾客信息
  ↓
判断需要调用 guest_info_retriever
  ↓
用 query 搜索数据集
  ↓
把检索结果组织成自然语言回答
```

这就是 Agentic RAG：

```text
检索器不是固定流水线的一部分，
而是 Agent 可调用的工具。
```

---

## 10. 普通 RAG 和本节 Agentic RAG 的区别

普通 RAG：

```text
用户问题
  ↓
固定检索宾客库
  ↓
把结果塞给 LLM
  ↓
回答
```

本节 Agentic RAG：

```text
用户问题
  ↓
Agent 判断是否需要宾客工具
  ↓
如果需要，调用 guest_info_retriever
  ↓
获得工具结果
  ↓
Agent 组织答案
```

区别在于：

```text
检索是 Agent 可选择的工具，而不是永远固定执行的步骤。
```

---

## 11. 互动示例怎么理解？

课程给了一个晚会场景：

```text
你：“Alfred，那位正在和大使说话的先生是谁？”
```

Alfred 可以快速搜索宾客数据库，找到类似：

```json
{
  "name": "Dr. Nikola Tesla",
  "relation": "old friend from university days",
  "description": "...",
  "email": "nikola.tesla@gmail.com"
}
```

然后 Alfred 用自然语言回答：

```text
先生，那是 Dr. Nikola Tesla，他是您大学时代的老朋友……
```

这个例子强调：

```text
Agent 不只是返回数据库原文，
而是把检索结果转成适合场景的回答。
```

---

## 12. 更进一步可以怎么做？

课程建议可以增强系统：

1. 改进检索器，比如使用 `sentence-transformers`；
2. 实现对话记忆，让 Alfred 记住之前的互动；
3. 结合网页搜索，获取陌生宾客最新信息；
4. 整合多个索引，从经过验证的来源获取更完整信息。

我建议还可以扩展：

- 增加饮食偏好字段；
- 增加禁忌话题字段；
- 增加适合聊天话题字段；
- 增加座位偏好；
- 增加最近一次联系时间；
- 给工具返回结果附带分数和来源；
- 如果找不到宾客，返回澄清问题。

---

## 13. 对你自己的项目有什么启发？

你想做多个智能体给自己打工。

这节课的价值在于：

```text
教你如何把一份业务数据变成 Agent 可调用工具。
```

以后你可以把很多数据都做成类似工具：

| 数据 | 工具 |
|---|---|
| 公众号历史文章 | `article_history_retriever` |
| 爆款标题库 | `viral_title_retriever` |
| 账号风格库 | `account_style_retriever` |
| 用户评论库 | `reader_feedback_retriever` |
| 平台规则 | `platform_rule_retriever` |
| 选题池 | `topic_pool_retriever` |

这样你的内容 Agent 就不是空写，而是：

```text
先检索你的私有经验，再创作。
```

这就是变现项目里非常重要的护城河。

---

## 14. 本节最重要的心智模型

第 26 天真正要记住的是：

```text
数据集不是直接给 LLM。
数据集先变成可检索文档。
可检索文档再变成检索器。
检索器再包装成工具。
工具交给 Agent 使用。
```

也就是：

```text
Dataset
  ↓
Document
  ↓
Retriever
  ↓
Tool
  ↓
Agent
```

这是一条非常重要的 Agentic RAG 工程链路。

---

## 15. 配套代码说明

代码目录：

```text
examples/26-agentic-rag-invitees/
```

文件：

| 文件 | 作用 |
|---|---|
| `01_load_and_preprocess_invitees.py` | 加载本地宾客数据，并转换成 Document |
| `02_guest_info_retriever_tool.py` | 创建一个简单关键词检索工具 |
| `03_alfred_invitee_agent.py` | 模拟 Alfred 调用宾客检索工具回答问题 |
| `04_pipeline_map.py` | 输出 Dataset → Document → Retriever → Tool → Agent 流程图 |
| `data/invitees.json` | 本地复刻课程数据集的 3 条宾客记录 |

这些代码不依赖第三方库，方便先理解流程。

注意：你要求“每一行代码都需要加注释”，所以 Python 示例里每一行代码都加了行内说明。

---

## 16. 记忆卡片

### 这节课讲了什么？

把晚会宾客数据集做成一个 RAG 检索工具，让 Alfred 可以按姓名或关系检索宾客信息。

### 图片上的三个框架是都要用吗？

不是。它们是三种可选实现方案：`smolagents`、`llama-index`、`langgraph`。选择一种即可。

### 整个 Agent 是由三个框架一起实现的吗？

不是。课程是同一个用例的多框架版本，不是三框架混合实现。

### 数据集字段有哪些？

`name`、`relation`、`description`、`email`。

### 为什么要转成 Document？

因为检索器需要统一的可检索文本格式，`page_content` 存正文，`metadata` 存来源信息。

### 为什么用 BM25？

因为数据集小，查询多为姓名、关系、邮箱等关键词检索，BM25 简单、快速、不需要 embedding。

### 这一节的工程链路是什么？

`Dataset -> Document -> Retriever -> Tool -> Agent`。

---

## 17. 我的理解

这节课看起来只是查宾客，其实是在教一个很关键的变现能力：

```text
把你的私有数据变成 Agent 的工具。
```

如果一个 Agent 只能调用大模型，它很容易同质化。

但如果它能调用你的私有知识库：

```text
历史文章
客户资料
账号风格
平台规则
爆款案例
读者反馈
销售话术
```

它就开始真正像一个“给你打工的员工”。

所以第 26 天不是简单的 RAG 入门，而是：

```text
Agentic RAG 的第一个可复用工程模板。
```

以后你做任何业务 Agent，都可以沿用这条链路：

```text
业务数据
  ↓
可检索文档
  ↓
检索工具
  ↓
Agent 调用
```

---

## 参考资料

- [Hugging Face Agents Course - 创建宾客信息检索生成（RAG）工具](https://huggingface.co/learn/agents-course/zh-CN/unit3/agentic-rag/invitees)
- [Hugging Face Dataset - agents-course/unit3-invitees](https://huggingface.co/datasets/agents-course/unit3-invitees)
- [GitHub 教材源码 - invitees.mdx](https://github.com/huggingface/agents-course/blob/main/units/zh-CN/unit3/agentic-rag/invitees.mdx)
