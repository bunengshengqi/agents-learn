# Day47：使用插件实战示例

本目录是 [Day47 学习笔记](../../notes/Day47-使用插件实战指南_四平台.md) 的配套代码，演示如何把 Day46 的 `text-processor-plugin` 安装到四个不同的 Agent 客户端。

## 目录结构

```text
47-using-plugins/
├── README.md                                      # 本文件
├── marketplace.json                               # Claude Code 本地 marketplace
├── agents/plugins/marketplace.json                # Codex 仓库 marketplace
├── .opencode/package.json                         # OpenCode 依赖清单
├── verify_install.sh                              # 装前自检脚本
└── pi-install.sh                                  # Pi 安装命令片段
```

## 四步走流程回顾

```text
发现（discover） → 安装（install） → 配置（configure） → 使用（use）
```

下面分别讲每个平台怎么走完这四步，统一基于 Day46 的插件：

- 插件路径：`examples/46-text-processor-plugin/text-processor-plugin/`
- 依赖 MCP server：`examples/43-text-processor-mcp/server.py`

## 1. Claude Code

### 1.1 发现

直接用本目录的 `marketplace.json`：

```json
{
  "name": "local-example-plugins",
  "owner": { "name": "you" },
  "plugins": [
    {
      "name": "text-processor-plugin",
      "source": "../46-text-processor-plugin/text-processor-plugin",
      "description": "Text analysis skills"
    }
  ]
}
```

注意根目录的 `marketplace.json` 和 `agents/plugins/marketplace.json` 都用**相对路径**指向 Day46 的插件目录。

### 1.2 安装

```text
/plugin marketplace add /Users/yuyuan/Desktop/agents-learn/examples/47-using-plugins/marketplace.json
/plugin install text-processor-plugin@local-example-plugins
```

### 1.3 配置

设置 API Key（如果插件需要外部服务）：

```bash
export HF_TOKEN="hf_xxxxx"
```

### 1.4 使用

```text
Analyze the reading level of this paragraph
# 或者
/text-processor-plugin:check-reading-level
```

### 1.5 改后重载

```text
/plugin → 找到 text-processor-plugin → disable → enable
```

## 2. Codex

### 2.1 发现

仓库根目录的 `agents/plugins/marketplace.json` 会被 Codex 自动识别。

### 2.2 安装

```text
/plugins
```

在浏览器里搜索 `text-processor-plugin` 并安装，然后**新建一个 thread**。

### 2.3 配置

```bash
export HF_TOKEN="hf_xxxxx"
```

### 2.4 使用

```text
What's the reading level of this README?
@text-processor-plugin
```

### 2.5 改后重载

**重启 Codex**。

## 3. OpenCode

### 3.1 发现

OpenCode 的插件是 `.js` / `.ts` 文件，Skills 单独放，MCP 单独配。

### 3.2 安装

把 Day46 的 OpenCode 配置复制到本示例：

```bash
cd examples/47-using-plugins
cp -R ../46-text-processor-plugin/opencode/* .
```

### 3.3 配置

编辑 `opencode.json` 里的 `command` 和 `args`，指向你本机的 Python venv 和 Day43 server。

### 3.4 使用

```text
Summarize this file and note any text-analysis follow-up that would help.
```

### 3.5 改后重载

```bash
opencode   # 重新启动
```

## 4. Pi

### 4.1 发现

Pi 的插件是 package。

### 4.2 安装

```bash
pi install /Users/yuyuan/Desktop/agents-learn/examples/46-text-processor-plugin/pi/text-processor-plugin -l
```

### 4.3 配置 MCP（如果需要）

```bash
pi install npm:pi-mcp-adapter
```

确保 `.mcp.json` 指向 Day43 server。

### 4.4 使用

```text
What's the reading level of this README?
/skill:check-reading-level What's the reading level of this README?
```

### 4.5 改后重载

在 Pi 内：

```text
/reload
```

## 装前自检

跑这个脚本验证所有 JSON 文件和路径都是合法的：

```bash
bash examples/47-using-plugins/verify_install.sh
```

成功输出 `✅ All files validated` 即可放心去装。

## 常见问题

| 现象 | 排查 |
|---|---|
| `/plugin install` 找不到插件 | `cat marketplace.json` 检查 `source` 路径 |
| MCP 启动失败 | 运行 `python examples/43-text-processor-mcp/test_fastmcp.py` |
| Skill 触发不了 | 确认 `skills/` 目录里 SKILL.md 存在 |
| 改了文件没生效 | 重新执行 reload / disable-enable / 重启 |

## 注意事项

- 路径以本仓库根目录为基准。如果你的仓库在别处，需要修改 `marketplace.json` 里的 `source` 字段。
- API Key 不要写进任何 JSON 文件，使用环境变量。
- 第一次安装失败很常见，请按 README 步骤逐项确认。
