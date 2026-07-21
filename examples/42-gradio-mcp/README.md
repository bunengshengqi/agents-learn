---
title: Day42 Gradio MCP Text Toolkit
emoji: 🧰
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.20.0
app_file: app.py
pinned: false
---

# Day 42：Gradio Web UI + MCP Server

这个示例让同一套 Python 函数拥有两种入口：人类使用 Gradio 网页，Agent 使用 Streamable HTTP MCP endpoint。完整讲解见 [Day42 学习笔记](../../notes/Day42-Gradio-MCP集成-WebUI与MCP服务器.md)。

## 1. 安装

```bash
cd /Users/yuyuan/Desktop/agents-learn
source .venv/bin/activate
python -m pip install -r examples/42-gradio-mcp/requirements.txt
```

## 2. 先跑快速测试

```bash
.venv/bin/python examples/42-gradio-mcp/test_functions.py
```

## 3. 启动应用

```bash
.venv/bin/python examples/42-gradio-mcp/app.py
```

启动后访问：

- Web UI：`http://127.0.0.1:7860/`
- MCP endpoint：`http://127.0.0.1:7860/gradio_api/mcp/`
- MCP Schema：`http://127.0.0.1:7860/gradio_api/mcp/schema`

## 4. 验证真实 MCP 连接

保留应用终端，再打开另一个终端：

```bash
.venv/bin/python examples/42-gradio-mcp/verify_mcp.py
```

验证器会完成 MCP 初始化、列出 Tools/Resources/Prompts，并调用 `analyze_text`。

## 5. 配置 Codex

```bash
codex mcp add day42-gradio \
  --url http://127.0.0.1:7860/gradio_api/mcp/
```

检查：

```bash
codex mcp list
codex mcp get day42-gradio
```

然后让 Agent 尝试：

```text
使用 day42-gradio 分析文本 “Gradio gives humans a UI and agents MCP tools”。
```

## 6. 部署到 Hugging Face Spaces

1. 创建 Space，SDK 选择 Gradio；
2. 把本目录的 `README.md`、`app.py` 和 `requirements.txt` 上传到 Space 根目录；
3. 等待 Building 变为 Running；
4. 打开 Web UI 和 `/gradio_api/mcp/schema`；
5. 将远程 endpoint 配置给 MCP Client：

```text
https://<username>-<space-name>.hf.space/gradio_api/mcp/
```

公开 Space 的 MCP 工具通常也公开可调用。`demo.launch(auth=...)` 只保护网页，不会自动保护 MCP endpoint；涉及私有数据或写操作时，应使用私有 Space、反向代理或 MCP Gateway 做认证和授权。
