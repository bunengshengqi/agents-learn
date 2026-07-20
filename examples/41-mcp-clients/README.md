# Day 41：把代码代理配置为 MCP Client

这个目录提供一个本地 stdio Server、Codex/OpenCode/Pi 配置样例，以及一个 Codex TOML 安全检查器。完整原理见 [Day41 学习笔记](../../notes/Day41-将代码代理配置为MCP客户端.md)。

## 1. 准备环境

如果已经完成 Day40，可以继续使用项目根目录的 `.venv`：

```bash
cd /Users/yuyuan/Desktop/agents-learn
source .venv/bin/activate
python -m pip install "mcp[cli]"
```

## 2. 用 Codex CLI 添加本地 Server

请把下面路径换成自己电脑上的真实绝对路径：

```bash
codex mcp add day41-learning -- \
  /Users/yuyuan/Desktop/agents-learn/.venv/bin/python \
  /Users/yuyuan/Desktop/agents-learn/examples/41-mcp-clients/local_server.py
```

检查配置：

```bash
codex mcp list
codex mcp get day41-learning
```

随后重新进入 Codex 会话，使用 `/mcp` 查看连接状态，再尝试：

```text
请使用 day41-learning 的 add 工具计算 18 + 24。
```

> `codex mcp add` 会修改用户级 Codex 配置。如果只想让团队在当前仓库使用，请复制 `configs/codex-project.example.toml` 为项目根目录 `.codex/config.toml`，替换绝对路径后再信任该项目。

## 3. 添加远程 Server

无认证：

```bash
codex mcp add remote-example --url https://example.com/mcp
```

Bearer Token：

```bash
export REMOTE_MCP_TOKEN="在本机设置，不要提交到 Git"
codex mcp add remote-example \
  --url https://example.com/mcp \
  --bearer-token-env-var REMOTE_MCP_TOKEN
```

OAuth Server：

```bash
codex mcp login remote-example
```

## 4. 管理 Server

```bash
codex mcp list
codex mcp get day41-learning --json
codex mcp remove day41-learning
```

也可以在 TOML 中设置 `enabled = false` 暂时停用，而不删除配置。

## 5. 检查公开仓库中的 TOML

示例路径故意是占位符，所以会提示需要替换绝对路径：

```bash
python examples/41-mcp-clients/check_config.py \
  examples/41-mcp-clients/configs/codex-project.example.toml
```

替换为真实绝对路径后，检查器会验证：

- 每个 Server 只能选择 `command` 或 `url` 之一；
- 本地脚本使用绝对路径；
- 远程地址使用 HTTPS；
- 没有把令牌或 Authorization 直接写入配置。

这只是学习用的静态检查，不能代替客户端实际连接测试。

## 6. 运行真实 MCP Client 测试

```bash
.venv/bin/python examples/41-mcp-clients/test_client.py
```

它会通过 stdio 启动 `local_server.py`，依次完成初始化、能力发现、Tool 调用，并确认 Resource 与 Prompt 已注册。
