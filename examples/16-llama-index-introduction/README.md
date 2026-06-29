# Day16：LlamaIndex 与 LlamaHub 入门练习

这个目录对应 Hugging Face Agents Course 第 16 天：

- [LlamaIndex Introduction](https://huggingface.co/learn/agents-course/zh-CN/unit2/llama-index/introduction)
- [LlamaHub](https://huggingface.co/learn/agents-course/zh-CN/unit2/llama-index/llama-hub)

Day16 的重点是：

- LlamaIndex 是什么。
- 组件是什么意思。
- LlamaHub 是什么。
- LlamaHub 的安装包和 import 路径如何对应。
- 如何读取本地资料并构建一个最小查询引擎。

## 第一步：安装依赖

```bash
pip install -r examples/16-llama-index-introduction/requirements.txt
```

如果你已经在项目根目录 `.venv` 里学习，可以用：

```bash
.venv/bin/pip install -r examples/16-llama-index-introduction/requirements.txt
```

## 第二步：配置真实 API

在项目根目录 `.env` 里配置：

```env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=你的 OpenAI-compatible API 地址，例如 https://api.deepseek.com
OPENAI_MODEL=你的模型名称，例如 deepseek-chat
```

这份代码使用 `llama-index-llms-openai-like`，适合 DeepSeek、996tokens 或其他 OpenAI-compatible Chat API。

## 第三步：先看无 API 概念演示

```bash
cd examples/16-llama-index-introduction
python component_flow_demo.py
python llamahub_install_demo.py
```

这两个脚本不会调用模型 API。

## 第四步：运行真实 LlamaIndex 本地资料问答

```bash
python first_index.py
```

这个脚本会：

```text
读取 data/ 目录里的 md 文件
-> 创建 LlamaIndex Document
-> 建立 SummaryIndex
-> 创建 Query Engine
-> 调用你的真实模型 API
-> 基于本地资料回答问题
```

## 第五步：自己提问

```bash
python query_local_notes.py "LlamaHub 和 LlamaIndex 是什么关系？"
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `component_flow_demo.py` | 不调用 API，演示组件、RAG 流程、LlamaHub 作用 |
| `llamahub_install_demo.py` | 不调用 API，检查 LlamaHub 集成包和 import 路径 |
| `model_config.py` | 读取 `.env`，创建 OpenAI-compatible LlamaIndex LLM |
| `first_index.py` | 主练习：读取本地资料并问答 |
| `query_local_notes.py` | 命令行版本地资料问答 |
| `data/` | Day16 本地知识库资料 |
| `requirements.txt` | 本目录依赖 |

## 今日核心结论

LlamaIndex 不是模型，而是把“你的数据”接到模型上的框架。

LlamaHub 不是另一个 Agent 框架，而是 LlamaIndex 的集成目录。

组件不是 UI 组件，而是 AI 应用中的功能积木：

```text
Reader -> Document -> Index -> Retriever / Query Engine -> LLM -> Answer
```

