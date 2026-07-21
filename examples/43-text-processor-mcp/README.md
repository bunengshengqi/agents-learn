---
title: Day43 Text Processor MCP
emoji: 📝
colorFrom: indigo
colorTo: purple
sdk: gradio
sdk_version: 6.20.0
app_file: app.py
pinned: false
---

# Day 43：构建并部署完整 MCP Server

完整讲解见 [Day43 学习笔记](../../notes/Day43-实战构建并部署MCP服务器.md)。本项目把业务逻辑、本地 FastMCP Server 和 Gradio 应用分开，避免课程示例在 `server.py`、`app.py` 复制两遍算法。

## 文件结构

```text
text_tools.py          纯业务逻辑，框架无关
server.py              本地 FastMCP stdio Server
app.py                 Gradio Web UI + HTTP MCP Server
test_text_tools.py     业务函数测试
test_fastmcp.py        本地 stdio MCP 端到端测试
verify_gradio_mcp.py   HTTP MCP 端到端测试
requirements.txt       本地与 Space 依赖
```

## 1. 安装

```bash
cd /Users/yuyuan/Desktop/agents-learn
source .venv/bin/activate
python -m pip install -r examples/43-text-processor-mcp/requirements.txt
```

## 2. 测试纯函数与 FastMCP

```bash
.venv/bin/python examples/43-text-processor-mcp/test_text_tools.py
.venv/bin/python examples/43-text-processor-mcp/test_fastmcp.py
```

## 3. 将本地 stdio Server 配置给 Codex

```bash
codex mcp add day43-local -- \
  /Users/yuyuan/Desktop/agents-learn/.venv/bin/python \
  /Users/yuyuan/Desktop/agents-learn/examples/43-text-processor-mcp/server.py
```

## 4. 启动 Gradio Web UI + MCP

```bash
.venv/bin/python examples/43-text-processor-mcp/app.py
```

- Web：`http://127.0.0.1:7860/`
- MCP：`http://127.0.0.1:7860/gradio_api/mcp/`
- Schema：`http://127.0.0.1:7860/gradio_api/mcp/schema`

另开终端验证：

```bash
.venv/bin/python examples/43-text-processor-mcp/verify_gradio_mcp.py
```

## 5. 部署到 Hugging Face Spaces

创建 Gradio Space 后，把以下文件上传到 Space 根目录：

```text
README.md
app.py
text_tools.py
requirements.txt
```

等待 Running，然后使用：

```text
https://<username>-<space-name>.hf.space/gradio_api/mcp/
```

配置 Codex：

```bash
codex mcp add day43-remote \
  --url https://<username>-<space-name>.hf.space/gradio_api/mcp/
```

公开 Space 的 MCP endpoint 通常也公开可调用。涉及私有数据、收费 API 或写操作时，请使用私有 Space、环境 Secrets 和独立的 MCP 认证/授权层。
