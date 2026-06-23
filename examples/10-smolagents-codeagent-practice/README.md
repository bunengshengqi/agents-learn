# Day10-smolagents CodeAgent 练习项目

这个目录是第 10 天的配套代码，用来练习：

- 如何配置真实 API
- 如何创建 `CodeAgent`
- 如何准备工具菜单 `tools`
- `agent.run()` 如何启动智能体
- CodeAgent 如何通过 Python 代码调用工具
- CodeAgent 为什么比 JSON Agent 更适合多步骤任务

## 第一步：安装依赖

```bash
pip install -r examples/10-smolagents-codeagent-practice/requirements.txt
```

## 第二步：配置真实 API

在项目根目录创建 `.env`：

```env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=你的中转站地址，例如 https://xxx.com/v1
OPENAI_MODEL=你的模型名称
```

如果使用 OpenAI 官方地址，`OPENAI_BASE_URL` 可以不填；如果使用中转站，一般需要填写。

## 第三步：运行 CodeAgent

```bash
cd examples/10-smolagents-codeagent-practice
python first_agent.py
```

## 文件说明

- `model_config.py`：读取 API 配置，创建 `OpenAIServerModel`。
- `tools.py`：定义 CodeAgent 可以调用的工具菜单。
- `first_agent.py`：创建 `CodeAgent` 并运行两个练习任务。
