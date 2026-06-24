# Day12-smolagents 工具创建与工具生态练习项目

这个目录对应 Hugging Face Agents Course 第 2.1 单元的 `工具` 章节。

Day12 的重点不是继续比较 Agent 类型，而是理解：

- 工具是什么。
- LLM 为什么需要工具接口描述。
- 如何用 `@tool` 创建简单工具。
- 如何用 `Tool` 类创建复杂工具。
- smolagents 默认工具箱和工具生态是什么。

## 第一步：安装依赖

```bash
pip install -r examples/12-smolagents-tools-practice/requirements.txt
```

## 第二步：配置真实 API

在项目根目录创建 `.env`：

```env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=你的中转站地址，例如 https://xxx.com/v1
OPENAI_MODEL=你的模型名称
```

## 第三步：先看工具说明书

这个脚本不调用真实模型，只打印工具 schema：

```bash
cd examples/12-smolagents-tools-practice
python tool_schema_demo.py
```

你要重点观察：

- `name`：工具名称。
- `description`：工具描述。
- `parameters`：输入参数类型和说明。

## 第四步：看默认工具箱说明

```bash
python default_toolbox_notes.py
```

这个脚本只做说明，不直接调用搜索或网页工具，避免网络和额外依赖干扰学习。

## 第五步：运行 Agent 练习

```bash
python first_agent.py
```

里面有三个练习：

1. `@tool` 函数工具：餐厅评分、性价比计算、关键词风险判断。
2. `Tool` 类工具：派对主题生成、商品标题优化。
3. 完整工具菜单：让 Agent 自己选择应该调用哪些工具。

## 文件说明

- `model_config.py`：读取 API 配置，创建模型对象。
- `tools.py`：定义 Day12 的所有自定义工具。
- `tool_schema_demo.py`：打印工具 schema，帮助理解“工具说明书”。
- `default_toolbox_notes.py`：说明 smolagents 默认工具箱和工具生态。
- `first_agent.py`：用 Agent 实际调用自定义工具。

## 今日核心结论

工具不是代码里的附属品。

工具是 Agent 连接真实世界的手脚。

一个好工具应该具备：

- 清楚的工具名。
- 明确的工具描述。
- 清晰的输入参数。
- 正确的输入类型。
- 明确的输出类型。
- 稳定的执行逻辑。

