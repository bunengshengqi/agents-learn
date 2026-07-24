---
title: Day46 - 从零构建跨平台 Plugin
date: 2026-07-24
tags:
  - AI-Agent
  - Context-Engineering
  - Plugin
  - MCP
  - Codex
  - Claude-Code
  - OpenCode
  - Pi
  - HuggingFace-Context-Course
status: completed
---

# Day46｜从零构建跨平台 Plugin：把 MCP Server 打包成可安装插件

> [!abstract] 本章目标
> 第46天是 Unit 3 的最后一课。今天我们要把 Day43 写的 `text-processor` MCP server，封装成**跨平台 Plugin**，让它能被 Claude Code、Codex、OpenCode、Pi 等不同客户端安装和使用。

**学习资料：**

- 在线教材：[Building Your Own Plugin](https://huggingface.co/learn/context-course/unit3/building-plugins)
- GitHub 原文：[unit3/building-plugins.mdx](https://github.com/huggingface/context-course/blob/main/units/en/unit3/building-plugins.mdx)
- 本仓库示例：[examples/46-text-processor-plugin](../examples/46-text-processor-plugin/README.md)
- 前置 MCP Server：[examples/43-text-processor-mcp](../examples/43-text-processor-mcp/README.md)

---

## 1. 一句话总结

> **MCP Server 负责“提供工具”，Skill 负责“教 Agent 何时/如何使用工具”，Plugin 负责“把这一套东西按平台规矩打包，方便分发和安装”。**

三者关系可以用一个餐馆类比：

| 概念 | 餐馆类比 | 作用 |
|---|---|---|
| **MCP Server** | 后厨的厨师和厨具 | 真正干活，提供文本分析、关键词提取等具体能力 |
| **Skill** | 菜单上的一道菜 + 制作流程卡 | 告诉服务员/顾客：什么时候点、怎么做、注意什么 |
| **Plugin** | 整家餐厅的加盟手册 | 把菜单、装修、服务流程打包，让不同商场（Claude Code、Codex、OpenCode、Pi）都能开店 |

**关键设计原则：**

```text
skills describe how to use tools
MCP servers provide the tools
plugins package reusable agent behavior
```

**最重要的一条：** 插件包里**不要复制服务端代码**，只引用已经存在的 MCP server。

---

## 2. 为什么需要 Plugin？

Day40~43 我们已经学会了写 MCP server。但一个 MCP server 不会自己跑进用户的 Agent 客户端里。用户需要：

1. 知道有这个能力；
2. 知道什么时候该用；
3. 知道怎么配置连接地址；
4. 在不同平台（Claude Code、Codex 等）上重复第 3 步。

Plugin 解决的就是这些问题：

- **版本绑定**：Skill、MCP 配置、Hook 按同一个版本号一起发布，避免“Skill 已更新但 MCP 还是旧接口”。
- **一次安装**：用户安装一次插件，就获得一套经过配套测试的能力。
- **跨平台分发**：同一套业务能力，可以用不同平台的“薄适配层”分别打包。

---

## 3. 核心概念速查

| 术语 | 含义 | 例子 |
|---|---|---|
| **Plugin** | 按平台规则打包好的可复用 Agent 行为包 | `text-processor-plugin` |
| **Skill** | `SKILL.md`，告诉 Agent “何时做、怎么做” | `analyze-text` / `extract-keywords` |
| **Manifest** | 插件的“身份证”，说明名称、版本、组件位置 | `.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`package.json` |
| **MCP Server** | 真正提供工具能力的服务端 | Day43 的 `server.py` |
| **Hook / Extension** | 监听生命周期事件，自动执行代码 | 工具调用前记录日志 |
| **Marketplace** | 本地或远程的“插件货架”，方便安装 | `marketplace.json` |

---

## 4. 动手实操：把 text-processor MCP 包成 Plugin

今天我们基于 Day43 的 MCP server，创建一个 `text-processor-plugin`。

### 4.1 前置准备

确保 Day43 MCP server 可以正常运行：

```bash
cd /Users/yuyuan/Desktop/agents-learn
source .venv/bin/activate
python examples/43-text-processor-mcp/test_fastmcp.py
```

如果测试通过，说明 `server.py` 里的 6 个工具可用：

- `analyze_text`
- `extract_keywords`
- `check_reading_level`
- `check_writing_basics`
- `summarize_text`
- `reverse_text`

### 4.2 创建目录结构

课程要求的最小结构是：

```text
text-processor-plugin/
├── .claude-plugin/plugin.json      # Claude Code 入口
├── .codex-plugin/plugin.json       # Codex 入口
├── .mcp.json                       # MCP 连接配置
├── skills/
│   ├── analyze-text/SKILL.md
│   ├── extract-keywords/SKILL.md
│   └── check-reading-level/SKILL.md
└── README.md
```

本仓库示例把它扩展为**跨平台完整版**：[examples/46-text-processor-plugin](../examples/46-text-processor-plugin/README.md)。

### 4.3 Step 1：写 Skill 文件

每个 Skill 只解决一件事：告诉 Agent **什么时候**调用、**怎么调用**、**结果怎么解释**。

以 `analyze-text` 为例：

```markdown
---
name: analyze-text
description: |
  Use this skill when the user wants basic statistics about a text
  (character count, word count, sentence count, average word length, etc.).
---

# analyze-text

When the user asks for text statistics, readability metadata, or a quick overview of a passage:

1. Call the MCP tool `analyze_text` with the full text as the `text` parameter.
2. Parse the returned JSON and present the numbers in a friendly way.
3. Mention that this is deterministic statistics, not semantic analysis.

Example user requests:
- "这段文字有多少字？"
- "Analyze this paragraph for me."
- "Give me the word count and sentence count."
```

**写 Skill 的黄金法则：**

- 开头说明**触发条件**（when to use），而不是只写功能；
- 给出**工具名和参数**；
- 给出**示例用户请求**，帮助模型匹配意图；
- 说明**限制和注意事项**。

### 4.4 Step 2：Claude Code 入口

`.claude-plugin/plugin.json`：

```json
{
  "name": "text-processor-plugin",
  "version": "1.0.0",
  "description": "Text analysis skills powered by the text-processor MCP server",
  "author": {
    "name": "agents-learn"
  }
}
```

规则：

- `.claude-plugin/` 目录里**只能放 `plugin.json`**；
- `skills/`、`.mcp.json` 都放在插件根目录；
- Claude Code 会自动发现根目录的 `.mcp.json`。

### 4.5 Step 3：Codex 入口 + MCP 配置

`.codex-plugin/plugin.json`：

```json
{
  "name": "text-processor-plugin",
  "version": "1.0.0",
  "description": "Text analysis skills powered by the text-processor MCP server",
  "skills": "./skills/",
  "mcpServers": "./.mcp.json",
  "interface": {
    "displayName": "Text Processor",
    "shortDescription": "Analyze text, extract keywords, and estimate reading level",
    "longDescription": "A teaching plugin that bundles text analysis skills and connects to a local text-processor MCP server.",
    "developerName": "agents-learn",
    "category": "Productivity",
    "capabilities": ["Instructions"]
  }
}
```

`.mcp.json`：

```json
{
  "mcpServers": {
    "text-processor": {
      "command": "../../.venv/bin/python",
      "args": ["../../examples/43-text-processor-mcp/server.py"]
    }
  }
}
```

> 注意：`.mcp.json` 里的路径是**相对于插件根目录**的。如果你把插件复制到别的地方，需要改成绝对路径或调整相对路径。

### 4.6 Step 4：OpenCode 插件

OpenCode 是 **Code-first**：插件入口就是 TypeScript 文件。

`.opencode/plugins/text-processor-plugin.ts`：

```typescript
import type { Plugin } from "@opencode-ai/plugin"

export const TextProcessorPlugin: Plugin = async ({ client }) => {
  await client.app.log({
    body: {
      service: "text-processor-plugin",
      level: "info",
      message: "Text Processor plugin initialized",
    },
  })

  return {
    "tool.execute.before": async (input) => {
      if (input.tool === "analyze_text") {
        await client.app.log({
          body: {
            service: "text-processor-plugin",
            level: "info",
            message: "About to run analyze_text",
          },
        })
      }
    },
  }
}
```

`opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["./.opencode/plugins/text-processor-plugin.ts"],
  "mcp": {
    "text-processor": {
      "command": "/Users/yuyuan/Desktop/agents-learn/.venv/bin/python",
      "args": ["/Users/yuyuan/Desktop/agents-learn/examples/43-text-processor-mcp/server.py"]
    }
  }
}
```

OpenCode 的特点：

- MCP 配置放在 `opencode.json` 的 `mcp` 键下；
- 插件模块通过 `client` 与运行时通信；
- Hook 由返回的事件处理器对象定义。

### 4.7 Step 5：Pi Package

Pi 使用 npm 生态的 `package.json` 作为 Manifest。

`package.json`：

```json
{
  "name": "text-processor-plugin",
  "version": "1.0.0",
  "description": "Text analysis skills powered by the text-processor MCP server",
  "keywords": ["pi-package"],
  "pi": {
    "skills": ["./skills"],
    "extensions": ["./extensions"]
  }
}
```

`extensions/text-processor.ts`：

```typescript
export default function textProcessorExtension(pi: any) {
  pi.on("load", () => {
    console.log("Text Processor Pi extension loaded")
  })
}
```

Pi 如果需要 MCP 工具，需要额外安装 `pi-mcp-adapter` 并配置 `.mcp.json`。

### 4.8 Step 6：写人类能看懂的 README

README 不是给模型看的，是给开发者和用户看的。至少包含：

1. 插件做什么、不做什么；
2. 安装步骤（不同平台）；
3. 需要什么环境变量或前置 MCP server；
4. 一个最小测试命令；
5. 常见问题排查。

---

## 5. 四个平台对比

| 问题 | Claude Code | Codex | OpenCode | Pi |
|---|---|---|---|---|
| 核心模型 | Manifest-first | Manifest-first | Code-first | Package-based |
| 入口 | `.claude-plugin/plugin.json` | `.codex-plugin/plugin.json` | JS/TS 模块 | `package.json` |
| Skills | 根目录 `skills/` | 根目录 `skills/` | 与代码分开配置 | `skills/` |
| MCP | 根目录 `.mcp.json` | 根目录 `.mcp.json` | `opencode.json` 的 `mcp` 键 | `pi-mcp-adapter` + `.mcp.json` |
| Hook | 根目录 `hooks/` | 根目录 `hooks/` | 插件返回事件处理器 | `extensions/` |
| 分发方式 | 插件目录 / Marketplace | 插件目录 / Marketplace | npm / 本地文件 | npm package |

**最容易复用的：**

- 业务规则和流程思想
- `SKILL.md` 的主体内容
- 远程 MCP server（协议兼容时）
- README 和测试案例

**通常需要重写的：**

- Manifest 文件路径和字段
- Hook / Extension 事件格式
- 安装与 Marketplace 元数据

---

## 6. 完整示例目录树

本仓库示例：[examples/46-text-processor-plugin](../examples/46-text-processor-plugin/README.md)

```text
examples/46-text-processor-plugin/
├── README.md                              # 示例总说明
├── text-processor-plugin/                 # Claude Code / Codex 可直接加载的插件包
│   ├── README.md
│   ├── .claude-plugin/plugin.json
│   ├── .codex-plugin/plugin.json
│   ├── .mcp.json
│   └── skills/
│       ├── analyze-text/SKILL.md
│       ├── extract-keywords/SKILL.md
│       ├── check-reading-level/SKILL.md
│       ├── check-writing-basics/SKILL.md
│       ├── summarize-text/SKILL.md
│       └── reverse-text/SKILL.md
├── opencode/
│   ├── opencode.json
│   └── plugins/text-processor-plugin.ts
└── pi/
    └── text-processor-plugin/
        ├── package.json
        ├── skills/
        └── extensions/text-processor.ts
```

---

## 7. 测试你的 Plugin

### 7.1 Claude Code

1. 把 `text-processor-plugin/` 复制到 Claude Code 的插件目录（通常是 `~/.claude/plugins/` 或项目内 `.claude/plugins/`）。
2. 重启 Claude Code。
3. 测试提问：

```text
请用 text-processor-plugin 分析这段文本的字数和句数：
"AI Agent is a system that can perceive, reason, and act."
```

### 7.2 Codex

1. 把 `text-processor-plugin/` 复制到 `~/.codex/plugins/`。
2. 更新 `~/.codex/plugins/marketplace.json`，加入本插件路径。
3. 在 Codex 中执行 `/plugins`，安装 `text-processor-plugin`。
4. 新建会话，测试：

```text
请提取下面这段英文文本的关键词：
"Machine learning models require large amounts of data and compute."
```

### 7.3 OpenCode

1. 把 `.opencode/plugins/text-processor-plugin.ts` 和 `opencode.json` 放到你的 OpenCode 项目根目录。
2. 启动 OpenCode：

```bash
opencode
```

3. 用 `opencode mcp list` 检查 MCP server 是否连接成功。
4. 测试读取文档并调用文本分析工具。

### 7.4 Pi

```bash
pi install /path/to/pi/text-processor-plugin -l
pi install npm:pi-mcp-adapter
# 配置 .mcp.json 指向 Day43 server
pi /reload
```

---

## 8. 最佳实践与避坑指南

1. **插件目录里不要放服务端代码**
   - 错误做法：把 `server.py`、`text_tools.py` 复制进插件。
   - 正确做法：插件只放 manifest、skills、README 和 MCP 配置。

2. **Skill 描述聚焦 “when to use”**
   - 不要只写 “This skill analyzes text”；
   - 要写 “当用户询问字数、词数、句数或平均词长时调用”。

3. **不要硬编码 API key**
   - 如果 MCP server 需要密钥，通过环境变量或平台 Secrets 传递。

4. **使用语义化版本号**
   - `1.0.0` 首次发布；
   - `1.0.1` 修复问题；
   - `1.1.0` 新增功能；
   - `2.0.0` 不兼容变更。

5. **修改插件后记得刷新**
   - Claude Code / Codex：disable/re-enable 插件或重启客户端；
   - Pi：执行 `/reload`。

6. **先写最小可用版本，再叠加组件**
   - 一个插件可以只有 Skills；
   - 也可以只有 MCP 配置；
   - 不必一次性把 Hooks、Apps、Subagents 全加上。

7. **安装成功 ≠ 可以信任**
   - 审查 Hook 会执行什么命令；
   - 审查 MCP server 把数据发到哪里；
   - 审查 OAuth scopes 和文件访问范围。

---

## 9. 面试题与思考题

1. **Plugin、Skill、MCP server 三者的关系是什么？**
2. **为什么 plugin 不应该包含 server 代码？**
3. **如果一个团队要同时支持 Claude Code 和 Codex，哪些文件可以复用？哪些必须重写？**
4. **Skill 文件为什么要强调 “when to use”，而不只是 “what it does”？**
5. **Manifest 写入了 MCP 配置，是否意味着插件自动获得网络/文件权限？为什么？**
6. **OpenCode 的插件模型与 Claude Code/Codex 有什么本质区别？**

---

## 10. 要点总结

- Plugin 是**分发层**：把 Skill 和 MCP 配置按平台规则打包。
- Skill 是**使用说明书**：教 Agent 何时、如何调用工具。
- MCP server 是**能力层**：真正执行工具逻辑。
- 不同平台的 Manifest 位置和字段不同，但业务能力可以复用。
- 不要复制服务端代码到插件目录。
- 先跑通最小版本，再逐步增加 Hooks、Extensions 等高级组件。

完成今天的学习后，你应该能：

- 为一个已有的 MCP server 编写配套 Skill；
- 为 Claude Code、Codex、OpenCode、Pi 分别创建插件入口；
- 解释 Plugin / Skill / MCP server 的分层关系；
- 在不同平台本地安装并测试插件。

---

**下一步：**

Unit 3 到这里就结束了。建议回到 [Day43 MCP server](../examples/43-text-processor-mcp/README.md)，确认它还能正常运行，然后把今天示例中的 `text-processor-plugin/` 复制到 Codex 或 Claude Code 的插件目录里，实际对话测试一次。只有真正跑通，才算学完。
