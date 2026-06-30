# 第18天：LlamaIndex Tools 工具系统代码最终版

## 1. 当前目录

你现在在：

```bash
/Users/yuyuan/Desktop/agents-learn/examples
```

建议目录：

```bash
cd /Users/yuyuan/Desktop/agents-learn/examples
mkdir 18-llama-index-tools-final
cd 18-llama-index-tools-final
```

把本项目文件放到这个目录。

---

## 2. 这一节代码对应什么内容？

第18天讲 LlamaIndex 的四类工具：

```text
1. FunctionTool
2. QueryEngineTool
3. ToolSpecs
4. Utility Tools
```

这四类工具的作用是：

```text
把 Python 函数、RAG 查询引擎、第三方服务工具包、大量数据处理能力，
包装成 Agent 可以调用的工具。
```

---

## 3. 安装依赖

```bash
python -m pip install -U -r requirements.txt
```

如果你已经在第17天安装过，大部分依赖已有。

---

## 4. .env 配置

继续使用你之前的 DeepSeek 配置：

```bash
OPENAI_API_KEY=你的DeepSeek_API_Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
```

或者：

```bash
DEEPSEEK_API_KEY=你的DeepSeek_API_Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

---

## 5. 运行顺序

```bash
python model_config.py
python 01_function_tool_demo.py
python 02_query_engine_tool_demo.py
python 03_agent_with_tools_demo.py
python 04_toolspecs_gmail_preview.py
python 05_utility_tools_demo.py
```

---

## 6. 文件说明

| 文件 | 作用 |
|---|---|
| model_config.py | 统一配置 DeepSeek + 本地 Embedding |
| 01_function_tool_demo.py | FunctionTool 示例 |
| 02_query_engine_tool_demo.py | QueryEngineTool 示例 |
| 03_agent_with_tools_demo.py | Agent 同时使用 FunctionTool + QueryEngineTool |
| 04_toolspecs_gmail_preview.py | ToolSpecs 结构说明 |
| 05_utility_tools_demo.py | Utility Tools 思路演示 |
| data/agent_course_notes.txt | 第18天课程知识库 |
| data/bank_notes.txt | 银行业务示例知识库 |

---

## 7. 重点修复

### 7.1 DeepSeek 使用 OpenAILike

不要用：

```python
from llama_index.llms.openai import OpenAI
```

要用：

```python
from llama_index.llms.openai_like import OpenAILike
```

并且配置：

```python
Settings.llm = OpenAILike(
    model=model,
    api_key=api_key,
    api_base=base_url,
    temperature=0.2,
    is_chat_model=True,
    is_function_calling_model=True,
    context_window=64000,
    max_tokens=2048,
)
```

### 7.2 FunctionAgent 是异步的

不要写：

```python
response = agent.run("问题")
```

要写：

```python
response = await agent.run("问题")
```

外面使用：

```python
asyncio.run(main())
```

---

## 8. 四种工具怎么理解？

| 工具类型 | 适合场景 | 本项目对应文件 |
|---|---|---|
| FunctionTool | 简单 Python 函数 | 01_function_tool_demo.py |
| QueryEngineTool | RAG 知识库问答 | 02_query_engine_tool_demo.py |
| ToolSpecs | 第三方服务工具包 | 04_toolspecs_gmail_preview.py |
| Utility Tools | 大量数据先索引再搜索 | 05_utility_tools_demo.py |

---

## 9. 一句话总结

第18天不是重新学 RAG，而是学习：

```text
如何把函数、知识库、服务工具包和大量数据处理能力，
包装成 Agent 可以主动调用的工具。
```
