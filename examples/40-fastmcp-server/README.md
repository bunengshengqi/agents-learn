# Day40：使用 Python 和 FastMCP 构建 MCP Server

本目录对应：

```text
notes/Day40-使用Python和FastMCP构建第一个MCP服务器.md
```

## 1. 创建并激活虚拟环境

macOS / Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

## 2. 安装稳定版 FastMCP

```bash
python -m pip install -r examples/40-fastmcp-server/requirements.txt
```

课程使用 MCP Python SDK 1.x 的 FastMCP API。本示例固定为：

```text
mcp[cli]==1.28.1
```

## 3. 运行自动测试

```bash
python examples/40-fastmcp-server/test_client.py
```

该测试会通过 stdio：

1. 启动 `calculator_server.py` 子进程；
2. 初始化 MCP Session；
3. 发现并调用 Tools；
4. 读取 Resource；
5. 发现 Resource Template；
6. 获取 Prompt；
7. 自动检查关键结果。

## 4. 使用 MCP Inspector

```bash
mcp dev examples/40-fastmcp-server/calculator_server.py
```

Inspector 是浏览器调试界面，可以查看和调用 Tools、Resources、Prompts。它通常还需要本机安装 Node.js / npx。

也可以直接运行 Inspector：

```bash
npx -y @modelcontextprotocol/inspector \
  python examples/40-fastmcp-server/calculator_server.py
```

## 5. 直接运行 Server

```bash
python examples/40-fastmcp-server/calculator_server.py
```

终端看起来像“卡住”是正常现象：Server 正在 stdin 上等待 Client 发来的 JSON-RPC 消息。退出请按 `Ctrl+C`。

stdio 模式下不要使用普通 `print()` 向 stdout 写日志，否则会污染协议消息。日志应写入 stderr 或文件。

## 6. 可选：Gradio Web UI + MCP

安装：

```bash
python -m pip install "gradio[mcp]"
```

运行：

```bash
python examples/40-fastmcp-server/gradio_app.py
```

默认地址：

```text
Web UI:      http://127.0.0.1:7860
MCP endpoint: http://127.0.0.1:7860/gradio_api/mcp/
```

FastMCP 更适合纯 Agent Server；Gradio 适合同一函数既给 Agent 调用，也给人通过浏览器操作。

## 文件说明

| 文件 | 作用 |
|---|---|
| `calculator_server.py` | 真实 FastMCP Server，包含 Tools、Resources、Prompts 和错误处理 |
| `test_client.py` | 官方 MCP stdio Client 自动测试 |
| `gradio_app.py` | 可选的 Gradio Web UI + MCP 示例 |
| `requirements.txt` | 固定课程对应的 MCP Python SDK 1.x 版本 |
