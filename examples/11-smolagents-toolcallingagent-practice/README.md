# Day11-smolagents ToolCallingAgent 练习项目

这个目录对应 Hugging Face Agents Course 第 2.1 单元：

`将操作编写为代码片段或 JSON 结构`

今天重点不是新工具，而是理解 Agent 的 `Action` 可以有两种表达方式：

- `CodeAgent`：生成 Python 代码片段作为 Action。
- `ToolCallingAgent`：生成 JSON 结构的工具调用指令作为 Action。

## 第一步：安装依赖

```bash
pip install -r examples/11-smolagents-toolcallingagent-practice/requirements.txt
```

## 第二步：配置真实 API

在项目根目录创建 `.env`：

```env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=你的中转站地址，例如 https://xxx.com/v1
OPENAI_MODEL=你的模型名称
```

`OPENAI_BASE_URL` 可选。如果使用中转站，一般需要填写。

注意：`ToolCallingAgent` 需要模型或接口支持原生 tool/function calling。

## 第三步：先看 Action 形式对比

这个脚本不调用真实模型，只打印课程里的核心对比：

```bash
cd examples/11-smolagents-toolcallingagent-practice
python action_format_demo.py
```

你要看懂：

```python
print(web_search("Search for: ..."))
```

和：

```json
{"name": "web_search", "arguments": {"query": "..."}}
```

表达的是同一件事：调用工具，只是 Action 格式不同。

## 第四步：运行 ToolCallingAgent

```bash
cd examples/11-smolagents-toolcallingagent-practice
python first_agent.py
```

`first_agent.py` 里有三个练习：

1. 简单天气查询：最适合 ToolCallingAgent。
2. 点菜推荐：多个简单工具调用，仍然适合 ToolCallingAgent。
3. 手机价格比较：能用 ToolCallingAgent 做，但更适合 Day10 的 CodeAgent。

## 文件说明

- `model_config.py`：读取 API 配置，创建 `OpenAIServerModel`。
- `tools.py`：定义 ToolCallingAgent 可以调用的工具。
- `action_format_demo.py`：展示 Python 代码 Action 和 JSON 工具调用 Action 的区别。
- `first_agent.py`：创建 `ToolCallingAgent` 并运行练习。

## 今日核心结论

`ToolCallingAgent` 不是简单地“把工具调用转成 JSON”。

它真正做的是：让模型使用标准化、结构化、可解析、可控的工具调用格式。

选择建议：

| 场景 | 更适合 |
|---|---|
| 查天气、搜索、查一条数据、调一个 API | ToolCallingAgent |
| 多步骤计算、循环、变量保存、列表/字典处理、方案比较 | CodeAgent |

