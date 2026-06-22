# Day 8: First Agent with smolagents

这个示例演示如何用 `smolagents` 创建一个最小可运行的 `CodeAgent`，并通过
OpenAI 兼容接口接入自己的中转站。

## 运行前准备

在项目根目录创建 `.env`：

```env
OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=你的中转站地址，例如 https://xxx.com/v1
OPENAI_MODEL=你的模型名
```

安装本示例依赖：

```bash
pip install -r examples/08-smolagents-first-agent/requirements.txt
```

运行：

```bash
cd examples/08-smolagents-first-agent
python first_agent.py
```

也可以传入自己的问题：

```bash
python first_agent.py "现在 Asia/Shanghai 是几点？顺便计算 7 乘以 8。"
```

## 文件说明

- `first_agent.py`：创建并运行 `CodeAgent`。
- `model_config.py`：读取 `.env`，构造 OpenAI 兼容模型。
- `tools.py`：定义 Agent 可以调用的工具。
