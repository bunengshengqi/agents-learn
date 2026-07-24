# text-processor-plugin

一个教学用跨平台插件，打包了文本分析相关的 Skill，并连接到本地的 `text-processor` MCP server。

## 包含的 Skill

| Skill | 作用 |
|---|---|
| `analyze-text` | 统计字符数、词数、句数、平均词长等 |
| `extract-keywords` | 提取英文高频关键词 |
| `check-reading-level` | 估算英文阅读难度（Flesch-Kincaid） |
| `check-writing-basics` | 检查重复空格、超长句、缺少句末标点等 |
| `summarize-text` | 基于前几句生成抽取式摘要 |
| `reverse-text` | 反转文本字符顺序 |

## 对应 MCP 工具

本插件引用的 MCP server 来自 [examples/43-text-processor-mcp](../43-text-processor-mcp/README.md)。

工具名：

- `analyze_text`
- `extract_keywords`
- `check_reading_level`
- `check_writing_basics`
- `summarize_text`
- `reverse_text`

## 平台安装

### Claude Code

```bash
cp -r text-processor-plugin ~/.claude/plugins/
# 重启 Claude Code
```

### Codex

```bash
cp -r text-processor-plugin ~/.codex/plugins/
# 在 Codex 中 /plugins 安装并启用
```

## MCP 配置

`.mcp.json` 已配置为使用本仓库的 Python 虚拟环境和 Day43 server。如果你的仓库路径不同，请修改：

```json
{
  "mcpServers": {
    "text-processor": {
      "command": "/Users/yuyuan/Desktop/agents-learn/.venv/bin/python",
      "args": ["/Users/yuyuan/Desktop/agents-learn/examples/43-text-processor-mcp/server.py"]
    }
  }
}
```

## 测试问题

1. 请分析这段文本的统计信息：...
2. 请提取这段英文的关键词：...
3. 这段英文的阅读难度是什么水平？
4. 这段文本有哪些基础写作问题？
5. 请把这段文字反转。
