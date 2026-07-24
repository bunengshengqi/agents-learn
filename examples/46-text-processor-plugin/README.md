# Day46：跨平台 text-processor-plugin 示例

本目录是 [Day46 学习笔记](../notes/Day46-从零构建跨平台Plugin.md) 的配套代码，演示如何把 Day43 的 `text-processor-mcp` 封装成可以安装到不同 Agent 客户端的 Plugin。

## 目录说明

```text
46-text-processor-plugin/
├── README.md                              # 本文件
├── text-processor-plugin/                 # Claude Code / Codex 通用插件包
│   ├── .claude-plugin/plugin.json
│   ├── .codex-plugin/plugin.json
│   ├── .mcp.json
│   └── skills/
├── opencode/                              # OpenCode 插件模块
│   ├── opencode.json
│   └── plugins/text-processor-plugin.ts
└── pi/                                    # Pi package
    └── text-processor-plugin/
        ├── package.json
        ├── skills/
        └── extensions/text-processor.ts
```

## 前置依赖

请确保 Day43 的 MCP server 可以正常运行：

```bash
cd /Users/yuyuan/Desktop/agents-learn
source .venv/bin/activate
python examples/43-text-processor-mcp/test_fastmcp.py
```

`.mcp.json` 中默认使用本仓库的绝对路径。如果你的仓库路径不同，请修改以下文件中的路径：

- `text-processor-plugin/.mcp.json`
- `opencode/opencode.json`

## 各平台快速测试

### Claude Code

1. 把 `text-processor-plugin/` 复制到 Claude Code 插件目录（如 `~/.claude/plugins/`）。
2. 重启 Claude Code。
3. 提问测试：

```text
请分析这段文本的字数和句数："AI Agent can perceive, reason, and act."
```

### Codex

1. 把 `text-processor-plugin/` 复制到 `~/.codex/plugins/`。
2. 在 Codex 中执行 `/plugins`，安装 `text-processor-plugin`。
3. 新建会话，提问：

```text
请提取下面这段英文的关键词："Machine learning models require data and compute."
```

### OpenCode

1. 把 `opencode/` 下的文件复制到你的 OpenCode 项目根目录。
2. 启动 `opencode`。
3. 用 `opencode mcp list` 检查 MCP 连接。

### Pi

```bash
pi install /path/to/pi/text-processor-plugin -l
# 如需 MCP 工具，再安装 pi-mcp-adapter 并配置 .mcp.json
pi /reload
```

## 设计原则

- **不复制服务端代码**：插件只包含 manifest、skills、README 和 MCP 配置。
- **Skill 聚焦使用时机**：每个 SKILL.md 都说明何时调用、参数含义、结果解释。
- **薄适配层**：同一套业务能力，用不同平台的入口文件分别打包。

## 注意事项

- 修改插件文件后，多数平台需要 disable/re-enable 或重启客户端才能生效。
- 不要把真实 API key 写进插件文件，使用环境变量或平台 Secrets。
- `.mcp.json` 中的 `command` 和 `args` 路径必须指向你本机的 Python 虚拟环境和 Day43 server。
