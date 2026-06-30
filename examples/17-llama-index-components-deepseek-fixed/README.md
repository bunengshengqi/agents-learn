# 第17天：LlamaIndex Components + QueryEngine 实现 RAG 修正版

## 1. 这版修复了什么？

你之前报错：

```text
ValueError: Unknown model 'deepseek-v4-flash'
```

原因是：

```text
llama_index.llms.openai.OpenAI 会校验 OpenAI 官方模型名。
deepseek-v4-flash 不是 OpenAI 官方模型名，所以报错。
```

这版已经改成：

```python
from llama_index.llms.openai_like import OpenAILike
```

DeepSeek 属于 OpenAI-compatible API，所以应该用 `OpenAILike`。

---

## 2. 安装依赖

```bash
cd /Users/yuyuan/Desktop/agents-learn/examples/17-llama-index-components-deepseek-fixed
python -m pip install -U -r requirements.txt
```

核心新增依赖：

```bash
llama-index-llms-openai-like
```

---

## 3. .env 配置

继续使用你已经配置好的 DeepSeek。

支持写法一：

```bash
OPENAI_API_KEY=你的DeepSeek_API_Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
```

支持写法二：

```bash
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

---

## 4. 运行顺序

```bash
python model_config.py
python component_flow_demo.py
python first_index.py
python query_local_notes.py
python query_engine_as_tool.py
```

---

## 5. 第17天核心流程

```text
data/alfred_notes.txt
  ↓
SimpleDirectoryReader 加载
  ↓
SentenceSplitter 切分
  ↓
HuggingFaceEmbedding 向量化
  ↓
Chroma 存储向量
  ↓
VectorStoreIndex 建索引
  ↓
QueryEngine 查询
  ↓
OpenAILike 调 DeepSeek 生成答案
```

---

## 6. 本节课一句话总结

LlamaIndex 的组件负责把外部资料变成可检索知识库，QueryEngine 负责把“检索资料 + LLM 生成答案”封装成一个接口，所以它可以作为 Agent 的 RAG 工具。
