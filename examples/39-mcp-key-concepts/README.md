# Day39：MCP 关键概念、JSON-RPC 与传输层

本目录对应：

```text
notes/Day39-MCP关键概念架构JSON-RPC传输与生命周期.md
```

## 这个 Demo 证明什么？

`protocol.py` 只定义一份 JSON-RPC 消息处理逻辑，两个 Transport 分别负责搬运消息：

```text
同一组 method / params / result
            │
      ┌─────┴─────┐
      │           │
    stdio        HTTP
  一行一个 JSON   POST body / response body
```

这就是“协议与传输层分离”：

- JSON-RPC 定义消息长什么样、怎样关联请求与响应、怎样表达错误；
- Transport 决定这些 JSON 字节通过进程管道还是网络传递；
- MCP 在 JSON-RPC 之上进一步规定方法、能力协商和生命周期。

## 文件说明

| 文件 | 作用 |
|---|---|
| `protocol.py` | 与 Transport 无关的 JSON-RPC 分发和 MCP-like 方法 |
| `stdio_server.py` | 从 stdin 逐行读取 JSON，从 stdout 逐行返回 JSON |
| `stdio_client.py` | 启动子进程并通过管道调用 Server |
| `http_server.py` | 通过 `POST /mcp` 搬运相同 JSON-RPC 消息 |
| `http_client.py` | 把相同请求放进 HTTP 请求体 |

## 运行 stdio Demo

```bash
python3 examples/39-mcp-key-concepts/stdio_client.py
```

你会看到：

1. `initialize` 请求与响应；
2. 没有 `id` 的 `notifications/initialized` 不产生响应；
3. `tools/list`；
4. `tools/call`；
5. `resources/read`；
6. `prompts/get`。

## 运行 HTTP Demo

终端一：

```bash
python3 examples/39-mcp-key-concepts/http_server.py
```

终端二：

```bash
python3 examples/39-mcp-key-concepts/http_client.py
```

比较两个 Client 的输出，可以发现 JSON-RPC 对象中的：

```text
jsonrpc
id
method
params
result / error
```

没有因为 Transport 改变而改变。改变的是消息外面的载体：换行分隔的进程流，或者 HTTP 请求与响应。

## 重要边界

本目录是零依赖教学 Demo，不是完整 MCP SDK 实现。

特别是 `http_server.py` 只用于展示“相同 JSON-RPC 消息可以放进 HTTP”。它没有完整实现 MCP Streamable HTTP 所需的：

- 初始化状态约束；
- `MCP-Protocol-Version` 等 Header；
- Session 管理；
- SSE 流式返回；
- GET / DELETE 行为；
- Origin 校验；
- 身份认证与授权；
- 恢复、重连和安全控制。

真实 MCP Server 应使用课程下一章介绍的 FastMCP 或官方 MCP SDK。
