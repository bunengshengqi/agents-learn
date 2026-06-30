 # 第17天：LlamaIndex Components 与 QueryEngine 实现 RAG

> 来源：Hugging Face Agents Course / Unit 2.2 / LlamaIndex Components  
> 主题：LlamaIndex 组件是什么？QueryEngine 为什么可以作为 Agent 的 RAG 工具？

---

## 0. 这一节到底在讲什么？

这一节讲的是：

**一个智能体想真正帮你做事，不能只靠大模型自己的“通用知识”，还必须能读取、检索、理解、使用你的私有资料。**

比如课程里的 Alfred 管家智能体，如果你让它帮你策划晚宴，它不能只靠“大模型知道什么是晚宴”。它还需要知道：

- 你的日历有没有空；
- 你和客人的饮食偏好；
- 以前哪些菜单成功过；
- 家里有哪些食材；
- 这次晚宴有什么特殊要求。

这些信息不是模型训练时自带的，而是来自你自己的数据。

所以这一节的核心是：

> **LlamaIndex 的组件负责把你的外部数据接入大模型，让 Agent 能查资料、用资料、基于资料回答和行动。**

其中最重要的组件之一就是：

> **QueryEngine：查询引擎。**

它可以把“用户问题”变成一次完整的 RAG 查询流程：  
**问题 → 检索相关资料 → 交给 LLM → 生成答案。**

---

# Q1：怎么理解这句话？

原文大意是：

> 要有效协助我们，Alfred 需要理解我们的请求，并准备、查找和使用相关信息来帮助完成任务。这正是 LlamaIndex 组件发挥作用的地方。

这句话可以拆成 4 层理解。

---

## 1. “理解我们的请求”是什么意思？

用户说一句话，Agent 不能只看表面文字，而要理解用户真正要做什么。

比如你说：

> Alfred，帮我准备一个适合周五晚上的家庭晚宴。

Agent 要理解：

- 这是一个“任务型请求”，不是闲聊；
- 目标是“策划晚宴”；
- 时间是“周五晚上”；
- 可能需要查询日历；
- 可能需要查询客人偏好；
- 可能需要查询历史菜单；
- 可能需要生成计划。

这一步靠的是 LLM 的语言理解能力。

---

## 2. “准备相关信息”是什么意思？

Agent 不能马上胡乱回答，它要先判断：

> 完成这个任务需要哪些信息？

比如晚宴任务可能需要：

| 需要的信息 | 可能的数据来源 |
|---|---|
| 周五晚上是否有安排 | 日历 |
| 客人名单 | 通讯录 / 备忘录 |
| 饮食禁忌 | 个人资料库 |
| 过往菜单 | 历史记录 |
| 菜谱 | 文档 / 网页 / 数据库 |

这一步相当于 Agent 在做“任务分解”和“信息需求判断”。

---

## 3. “查找相关信息”是什么意思？

有了信息需求之后，Agent 要去你的数据里找东西。

比如：

- 从 PDF 里找某个制度条款；
- 从本地文件夹里找学习笔记；
- 从数据库里找客户信息；
- 从知识库里找某个业务流程；
- 从网页、API、Notion、Google Drive 等数据源里找资料。

这正是 LlamaIndex 擅长的事情。

LlamaIndex 提供很多组件，比如：

- `SimpleDirectoryReader`：读取本地文件；
- `LlamaHub`：连接各种外部数据源；
- `SentenceSplitter`：把文档切成小块；
- `Embedding Model`：把文本转成向量；
- `VectorStoreIndex`：建立可检索索引；
- `QueryEngine`：对索引发起查询并生成答案。

---

## 4. “使用相关信息”是什么意思？

找到资料还不够，Agent 还要把资料用起来。

比如从知识库里查到：

> 客人 A 不吃辣，客人 B 对花生过敏，以前最受欢迎的是意面和烤鸡。

Agent 最后应该输出：

> 周五晚宴建议准备清淡风格菜单，避免辣椒和花生。主菜可以选烤鸡，搭配意面和蔬菜沙拉。

也就是说，Agent 不是简单“搜索”，而是：

> **检索资料 + 理解资料 + 结合用户目标生成可用结果。**

---

## Q1 总结

这句话的核心意思是：

> **Agent 想真正有用，必须具备“理解任务、判断需要什么信息、从外部知识库查资料、基于资料完成任务”的能力。LlamaIndex 的组件就是帮 Agent 建立这种能力的工具箱。**

可以把它理解成：

```text
LLM = 大脑
LlamaIndex = 资料管理和检索系统
QueryEngine = 问资料、拿答案的接口
Agent = 会调用工具完成任务的人
```

---

# Q2：为什么重点关注 QueryEngine？它为什么可以作为 RAG 工具？

课程说：

> 我们将重点关注 QueryEngine 组件。为什么？因为它可以作为智能体的检索增强生成（RAG）工具。

这句话非常重要。

---

## 1. 先理解 RAG 是什么

RAG 全称是：

> Retrieval-Augmented Generation  
> 检索增强生成

它的核心逻辑是：

```text
用户问题
  ↓
从知识库中检索相关资料
  ↓
把资料和问题一起交给大模型
  ↓
大模型基于资料生成答案
```

普通 LLM 回答问题时，主要依赖训练时学到的知识。

但 LLM 有几个问题：

- 不知道你的私有资料；
- 不知道最新资料；
- 容易编造；
- 对专业领域细节不一定准确；
- 无法直接读取你本地的 PDF、Word、Excel、网页、数据库。

RAG 就是为了解决这个问题。

它让模型先“查资料”，再“回答”。

---

## 2. QueryEngine 在 RAG 里负责什么？

`QueryEngine` 可以理解成：

> **LlamaIndex 里对外提供问答能力的组件。**

你把索引建好之后，可以这样创建 QueryEngine：

```python
query_engine = index.as_query_engine(
    llm=llm,
    response_mode="tree_summarize",
)
```

然后就可以问：

```python
response = query_engine.query("What is the meaning of life?")
```

表面看只是一句 `query()`，但底层其实做了很多事情。

---

## 3. QueryEngine 背后的完整动作

当你调用：

```python
query_engine.query("用户的问题")
```

底层大致会发生这些步骤：

```text
1. 接收用户问题
2. 将用户问题转成向量
3. 到向量数据库中查找最相似的文本块
4. 取回相关 Node / 文本片段
5. 把问题 + 检索结果一起组装成 Prompt
6. 调用 LLM
7. 让 LLM 基于检索资料生成答案
8. 返回最终响应
```

所以 QueryEngine 不是简单的“搜索框”，而是一个完整的 RAG 问答接口。

---

## 4. 为什么它适合给 Agent 当工具？

Agent 的特点是：

> 它不是只回答问题，而是会根据任务选择工具。

比如 Agent 有这些工具：

- 查询日历工具；
- 查询邮件工具；
- 查询数据库工具；
- 查询知识库工具；
- 发送邮件工具；
- 生成报告工具。

那么 `QueryEngine` 就可以包装成一个“查询知识库工具”。

例如：

```text
工具名称：party_planning_query_engine
工具功能：查询 Alfred 的晚宴策划知识库
输入：用户问题
输出：相关知识和答案
```

当用户说：

> Alfred，帮我根据过去成功菜单安排一个晚宴。

Agent 可以决定：

```text
这个问题需要查历史菜单 → 调用 QueryEngine 工具 → 拿到资料 → 生成晚宴方案
```

这就是 QueryEngine 作为 Agent RAG 工具的原因。

---

## 5. QueryEngine 和 Retriever 有什么区别？

课程里提到索引可以转成三种接口：

| 接口 | 作用 | 返回结果 |
|---|---|---|
| `as_retriever` | 只检索资料 | 返回相关文本块 |
| `as_query_engine` | 检索 + 生成答案 | 返回完整回答 |
| `as_chat_engine` | 多轮对话 + 记忆 + 检索 | 返回对话式回答 |

简单理解：

```text
Retriever = 只帮你找资料
QueryEngine = 找资料 + 总结成答案
ChatEngine = 带聊天记忆的 QueryEngine
```

所以如果你只是想拿到原始资料，用 Retriever。  
如果你想直接得到问答结果，用 QueryEngine。  
如果你想做多轮聊天知识库助手，用 ChatEngine。

---

# Q3：图1例子展开说明

课程图1讲的是 RAG 的基本思想。虽然图上可能是一个简化示意，但可以理解为：

```text
用户问题
  ↓
检索系统
  ↓
外部知识库 / 文档 / 数据库
  ↓
取回相关内容
  ↓
大语言模型
  ↓
生成更准确的答案
```

---

## 1. 不使用 RAG 的情况

比如你问模型：

> Alfred，帮我安排一个晚宴菜单。

如果没有 RAG，模型只能根据通用知识回答：

> 可以准备沙拉、牛排、甜点和饮品。

这个答案可能看起来不错，但问题是：

- 它不知道客人不吃什么；
- 不知道你家有什么食材；
- 不知道你以前做过什么；
- 不知道周五晚上有多少人；
- 不知道你的预算；
- 不知道客人是否过敏。

所以它可能“流畅但不可靠”。

---

## 2. 使用 RAG 的情况

如果使用 RAG，流程会变成：

```text
用户问题：帮我安排周五晚宴
  ↓
QueryEngine 检索
  ↓
找到：
- 周五有 6 位客人
- 客人 A 不吃辣
- 客人 B 对花生过敏
- 上次烤鸡评价很好
- 预算 500 元
  ↓
LLM 基于这些资料生成答案
  ↓
输出个性化晚宴方案
```

这样生成的答案就更符合真实情况。

---

## 3. 对 Alfred 的意义

Alfred 作为管家智能体，本质上要做的是“基于你的个人信息帮你完成任务”。

它不能只会聊天，还要能查你的资料。

所以 QueryEngine 相当于 Alfred 的“资料查询能力”。

可以类比为：

```text
没有 QueryEngine 的 Alfred：
像一个聪明但不了解你家的管家。

有 QueryEngine 的 Alfred：
像一个能查看日历、菜单记录、客人偏好、家庭库存的管家。
```

---

## 4. 放到你自己的学习场景里理解

你现在经常把课程内容整理成 Obsidian 笔记。

如果你以后有一个自己的学习 Agent，它应该可以回答：

> 第13天 smolagents 的 Tool 是怎么写的？
> 第17天 LlamaIndex 的 QueryEngine 和 RAG 是什么关系？
> 我之前整理过哪些关于 Agent 的内容？

这个时候，Agent 就需要查你的 Obsidian 笔记。

流程就是：

```text
你的问题
  ↓
QueryEngine 查询 Obsidian 知识库
  ↓
找到第13天、第17天相关笔记
  ↓
LLM 汇总解释
  ↓
输出答案
```

这就是 RAG 的真实价值。

---

# Q4：图2开始的组件实现 RAG 流程是不是固定的？实现思路是什么？流程是什么？

课程中列出 RAG 的五个关键阶段：

```text
1. 加载
2. 索引
3. 存储
4. 查询
5. 评估
```

这个流程是 RAG 的经典主流程，但不是死板固定的。

---

## 1. 流程是不是固定的？

答案是：

> **大方向基本固定，具体实现不固定。**

固定的是思想：

```text
数据进入系统
  ↓
处理成适合检索的结构
  ↓
存起来
  ↓
用户提问时检索
  ↓
LLM 基于检索结果生成答案
  ↓
评估答案质量
```

不固定的是每一步的工具和策略。

比如：

| 阶段 | 可以变化的地方 |
|---|---|
| 加载 | 本地文件、网页、PDF、数据库、API、Notion、飞书、Obsidian |
| 切分 | 按句子切、按段落切、按标题切、按 token 切 |
| 嵌入 | OpenAI embedding、BGE、E5、Jina、国产 embedding |
| 存储 | Chroma、FAISS、Milvus、Qdrant、pgvector |
| 检索 | 向量检索、关键词检索、混合检索、多路召回 |
| 生成 | compact、refine、tree_summarize |
| 评估 | 忠实性、相关性、正确性、响应速度 |

所以你可以理解为：

```text
RAG 流程是固定骨架，但每个环节都可以替换组件。
```

---

# 二、组件实现 RAG 的完整流程

下面按课程流程拆开讲。

---

## 阶段1：加载数据 Loading

目的：

> 把原始资料读进 LlamaIndex。

原始资料可能是：

- `.txt`
- `.md`
- `.pdf`
- `.docx`
- 网页
- 数据库
- API
- Notion
- Google Drive
- Obsidian 文件夹

课程里最简单的加载方式是：

```python
from llama_index.core import SimpleDirectoryReader

reader = SimpleDirectoryReader(input_dir="path/to/directory")
documents = reader.load_data()
```

这段代码的意思是：

```text
从某个文件夹读取文件
  ↓
转换成 LlamaIndex 可以处理的 Document 对象
```

`Document` 可以理解为“一篇原始文档”。

比如：

```text
第17天学习笔记.md → Document
银行制度.pdf → Document
晚宴菜单.txt → Document
```

---

## 阶段2：切分和嵌入 Ingestion

加载完文档之后，不能直接把整篇文档塞给大模型。

原因：

- 文档太长；
- LLM 上下文有限；
- 检索时需要更细颗粒度；
- 一整篇文档不利于精准匹配。

所以要切分成小块。

课程里使用：

```python
SentenceSplitter(chunk_overlap=0)
```

它的作用是：

> 把长文档按句子或语义边界切成较小文本块。

这些小块在 LlamaIndex 里叫：

> `Node`

可以理解为：

```text
Document = 一整篇文章
Node = 文章中的一个小片段
```

例如：

```text
Document：第17天完整课程笔记

Node 1：LlamaIndex 组件介绍
Node 2：RAG 的概念
Node 3：SimpleDirectoryReader 用法
Node 4：QueryEngine 用法
Node 5：ResponseSynthesizer 策略
```

---

## 阶段3：Embedding 向量化

切成 Node 之后，还要把文本变成向量。

课程里使用：

```python
HuggingFaceInferenceAPIEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)
```

Embedding 的作用是：

> 把文本转换成一组数字，让计算机可以比较语义相似度。

比如：

```text
“晚宴菜单怎么安排”
“如何准备家庭聚餐”
```

这两句话字面不完全一样，但语义很接近。

Embedding 会让它们在向量空间里距离更近。

这就是向量检索的基础。

---

## 阶段4：建立 IngestionPipeline

课程代码：

```python
from llama_index.core import Document
from llama_index.embeddings.huggingface_api import HuggingFaceInferenceAPIEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_overlap=0),
        HuggingFaceInferenceAPIEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    ]
)

nodes = await pipeline.arun(documents=[Document.example()])
```

这段代码可以理解为：

```text
输入 Document
  ↓
SentenceSplitter 切成 Node
  ↓
Embedding Model 把 Node 转成向量
  ↓
输出带向量的 Node
```

也就是：

```text
原始文档 → 文本块 → 向量化文本块
```

---

## 阶段5：存储向量 Store

如果每次启动程序都重新切分、重新向量化，会很浪费时间和钱。

所以要把向量存起来。

课程里使用 ChromaDB：

```python
import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore

db = chromadb.PersistentClient(path="./alfred_chroma_db")
chroma_collection = db.get_or_create_collection("alfred")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
```

这段代码的意思是：

```text
创建一个本地 Chroma 向量数据库
数据库路径：./alfred_chroma_db
集合名称：alfred
然后把它包装成 LlamaIndex 可用的 vector_store
```

你可以把 Chroma 理解为：

> 专门存放“文本向量 + 原始文本 + 元数据”的数据库。

---

## 阶段6：把 vector_store 接入 pipeline

课程代码：

```python
pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=25, chunk_overlap=0),
        HuggingFaceInferenceAPIEmbedding(model_name="BAAI/bge-small-en-v1.5"),
    ],
    vector_store=vector_store,
)
```

这一步的意思是：

```text
文档进入 pipeline
  ↓
切块
  ↓
向量化
  ↓
写入 Chroma 向量数据库
```

到这里，知识库就基本建好了。

---

## 阶段7：创建 VectorStoreIndex

课程代码：

```python
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.huggingface_api import HuggingFaceInferenceAPIEmbedding

embed_model = HuggingFaceInferenceAPIEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
)

index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=embed_model
)
```

这一步的作用是：

> 基于向量数据库创建一个可查询的索引对象。

注意这里有个关键点：

**查询时使用的 embedding 模型，应该和入库时使用的 embedding 模型保持一致。**

因为：

```text
入库时：文本 → 向量
查询时：问题 → 向量
```

如果两边使用不同模型，向量空间可能不一致，检索效果会变差。

---

## 阶段8：把索引转换成 QueryEngine

课程代码：

```python
from llama_index.llms.huggingface_api import HuggingFaceInferenceAPI

llm = HuggingFaceInferenceAPI(
    model_name="Qwen/Qwen2.5-Coder-32B-Instruct"
)

query_engine = index.as_query_engine(
    llm=llm,
    response_mode="tree_summarize",
)
```

这一步非常关键。

它的意思是：

```text
VectorStoreIndex 只是索引
QueryEngine 才是问答接口
```

索引解决的是：

> 去哪里查？

QueryEngine 解决的是：

> 怎么查？查到后怎么组织给 LLM？最后怎么回答？

---

## 阶段9：发起查询

课程代码：

```python
query_engine.query("What is the meaning of life?")
```

执行这句代码时，完整链路是：

```text
用户问题
  ↓
问题向量化
  ↓
向量数据库检索相关 Node
  ↓
取回文本块
  ↓
组装 Prompt
  ↓
调用 LLM
  ↓
生成答案
```

这就是 QueryEngine 实现 RAG 的关键。

---

# 三、ResponseSynthesizer：回答是怎么组织出来的？

课程里提到，QueryEngine 底层会使用 `ResponseSynthesizer` 处理响应。

它负责：

> 把检索到的多个文本块，组织成最终答案。

常见策略有三种。

---

## 1. refine：迭代优化

逻辑：

```text
先读第一个文本块生成初版答案
  ↓
再读第二个文本块修正答案
  ↓
再读第三个文本块继续修正
  ↓
直到所有文本块处理完
```

优点：

- 适合需要逐步整合信息的问题；
- 答案比较细。

缺点：

- LLM 调用次数多；
- 成本高；
- 速度慢。

---

## 2. compact：紧凑模式

逻辑：

```text
先把多个文本块尽量合并
  ↓
减少 LLM 调用次数
  ↓
生成答案
```

优点：

- 更快；
- 更省钱；
- 默认常用。

缺点：

- 如果资料太多，可能压缩后遗漏细节。

---

## 3. tree_summarize：树状总结

逻辑：

```text
多个文本块
  ↓
分组总结
  ↓
再总结分组结果
  ↓
形成最终答案
```

优点：

- 适合长资料、多资料汇总；
- 结构化总结能力强。

缺点：

- 实现相对复杂；
- 也可能需要多次 LLM 调用。

课程示例里使用的是：

```python
response_mode="tree_summarize"
```

说明它希望 QueryEngine 对检索结果做更强的归纳总结。

---

# 四、评估与可观测性

RAG 不是搭好就结束，还要评估效果。

因为 RAG 常见问题包括：

- 检索到了错误资料；
- 检索资料不够完整；
- LLM 没有忠实使用资料；
- 回答看起来对，但其实编造；
- 答案和问题不相关；
- 响应速度太慢。

课程里提到三个评估器。

---

## 1. FaithfulnessEvaluator：忠实性评估

检查：

> 答案是否真的被检索到的上下文支持？

比如资料里没有“客户必须提交 A 材料”，但模型回答说“必须提交 A 材料”，这就是不忠实。

---

## 2. AnswerRelevancyEvaluator：答案相关性评估

检查：

> 答案有没有真正回答用户问题？

比如用户问“QueryEngine 为什么能做 RAG 工具”，模型却大篇幅讲 LlamaIndex 历史，这就是相关性差。

---

## 3. CorrectnessEvaluator：正确性评估

检查：

> 答案本身是否正确？

这通常需要标准答案或更强模型辅助判断。

---

# 五、用你自己的话总结第17天

第17天可以这样总结：

> 这一节讲 LlamaIndex 的组件体系，重点是 QueryEngine。LlamaIndex 可以把外部资料加载进来，切成 Node，转成向量，存进向量数据库，再创建索引。用户提问时，QueryEngine 会从索引中检索相关文本块，再交给 LLM 生成答案。因此 QueryEngine 可以作为 Agent 的 RAG 工具，让智能体具备“查资料后再回答”的能力。

---

# 六、最重要的理解框架

你可以记住这个公式：

```text
RAG = 检索 + 生成
```

再进一步：

```text
LlamaIndex RAG =
加载数据
+ 切分文档
+ 向量化
+ 存储
+ 建索引
+ QueryEngine 查询
+ LLM 生成答案
+ 评估质量
```

再放到 Agent 里：

```text
Agent 发现自己需要查知识库
  ↓
调用 QueryEngine 工具
  ↓
QueryEngine 检索相关资料
  ↓
LLM 基于资料生成答案
  ↓
Agent 用这个答案继续完成任务
```

---

# 七、和你之前学习内容的关系

你之前学过 smolagents 里的 Tool。

那这一节可以这样连接起来：

```text
smolagents 的 Tool：
定义一个工具，让 Agent 可以调用。

LlamaIndex 的 QueryEngine：
提供一个知识库问答能力。

两者结合：
把 QueryEngine 包装成 Tool，Agent 就拥有了查询知识库的能力。
```

举个例子：

```python
class KnowledgeBaseTool(Tool):
    name = "knowledge_base_query"
    description = "查询我的 Obsidian 学习笔记知识库"

    inputs = {
        "query": {
            "type": "string",
            "description": "用户想查询的问题"
        }
    }

    output_type = "string"

    def forward(self, query: str) -> str:
        response = query_engine.query(query)
        return str(response)
```

这样 Agent 就可以调用：

```text
knowledge_base_query("第17天 QueryEngine 是什么？")
```

然后从你的 Obsidian 笔记里查答案。

---

# 八、你应该掌握的关键词

| 关键词 | 含义 |
|---|---|
| Document | 原始文档 |
| Node | 文档切分后的文本块 |
| Embedding | 文本向量化 |
| Vector Store | 向量数据库 |
| VectorStoreIndex | 基于向量库建立的索引 |
| Retriever | 只负责检索 |
| QueryEngine | 检索 + 生成答案 |
| ChatEngine | 多轮对话式检索问答 |
| ResponseSynthesizer | 把检索结果组织成最终答案 |
| RAG | 检索增强生成 |
| Evaluation | 评估回答质量 |
| Observability | 观察系统内部运行过程 |

---

# 九、最终记忆版

你可以把第17天记成一句话：

> **LlamaIndex 的组件可以把外部数据变成智能体可查询的知识库，而 QueryEngine 是这个知识库的问答入口。它通过检索相关资料，再让 LLM 基于资料生成答案，所以 QueryEngine 可以作为 Agent 的 RAG 工具。**

---

# 十、适合 Obsidian 的复习卡片

## 卡片1：RAG 是什么？

RAG 是检索增强生成。  
它先从外部知识库中检索相关资料，再把资料交给 LLM 生成答案。  
它解决的是大模型不知道私有数据、最新数据和专业资料的问题。

---

## 卡片2：QueryEngine 是什么？

QueryEngine 是 LlamaIndex 中的查询引擎。  
它把用户问题转成检索请求，从索引中找相关文本块，再调用 LLM 生成最终答案。  
它可以作为智能体的 RAG 工具。

---

## 卡片3：QueryEngine 和 Retriever 区别？

Retriever 只负责查资料，返回文本块。  
QueryEngine 负责查资料并生成答案。  
ChatEngine 适合带上下文记忆的多轮对话。

---

## 卡片4：LlamaIndex RAG 流程

```text
加载数据 → 文档切分 → 向量化 → 存储 → 建索引 → 查询 → 生成答案 → 评估
```

---

## 卡片5：为什么 Agent 需要 RAG？

因为 Agent 不能只依赖大模型通用知识。  
它要完成真实任务，就必须能查询用户的私有资料、历史记录、业务文档和实时数据。  
RAG 让 Agent 具备“查资料后再行动”的能力。

---

# 十一、你后面可以怎么实践？

建议你下一步做一个最小版个人知识库：

```text
输入：你的 Obsidian 学习笔记
处理：用 LlamaIndex 加载 md 文件
存储：ChromaDB
查询：QueryEngine
应用：问“第13天 smolagents 学了什么？”
```

最小闭环：

```text
Obsidian 笔记文件夹
  ↓
SimpleDirectoryReader
  ↓
SentenceSplitter
  ↓
Embedding
  ↓
ChromaDB
  ↓
VectorStoreIndex
  ↓
QueryEngine
  ↓
问答
```

只要这个跑通，你就真正理解了第17天。
