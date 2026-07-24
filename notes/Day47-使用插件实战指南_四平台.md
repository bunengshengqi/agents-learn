---
title: Day47 - 使用插件实战指南：把别人做的插件装进自己的 Agent
date: 2026-07-24
tags:
  - AI-Agent
  - Context-Engineering
  - Plugin
  - MCP
  - Claude-Code
  - Codex
  - OpenCode
  - Pi
  - HuggingFace-Context-Course
status: completed
---

# Day47｜使用插件实战指南：把别人做的插件装进自己的 Agent

> [!abstract] 本章目标
> Day46 我们学会了**怎么把 MCP server 打包成 Plugin**。今天是 Unit 3 的最后一节：学会**怎么把别人（或者自己）做好的 Plugin 装到 Agent 客户端里去用**。你只要跟着走一遍四个平台的安装流程，就能彻底打通"开发 → 分发 → 使用"这条链路。

**学习资料：**

- 在线教材：[Using Plugins](https://huggingface.co/learn/context-course/unit3/using-plugins)
- GitHub 原文：[unit3/using-plugins.mdx](https://github.com/huggingface/context-course/blob/main/units/en/unit3/using-plugins.mdx)
- 本仓库示例：[examples/47-using-plugins](../examples/47-using-plugins/README.md)
- 上一天的插件：[examples/46-text-processor-plugin](../examples/46-text-processor-plugin/README.md)

---

## 1. 一句话总结

> **装 Plugin 跟装手机 App 一样：找应用市场 → 点安装 → 配权限（API Key）→ 打开用。**

所有 Agent 客户端都遵循同一条**四步走**流程：

```text
发现（discover） → 安装（install） → 配置（configure） → 使用（use）
```

只不过不同平台的"应用市场"叫法不一样：

| 平台 | 应用市场 | 安装命令 |
|---|---|---|
| Claude Code | Marketplace | `/plugin marketplace add` + `/plugin install` |
| Codex | Marketplace / Plugin Browser | `/plugins` + `marketplace.json` |
| OpenCode | 文件夹 / npm | `.opencode/plugins/` 或 `opencode.json` |
| Pi | Pi Package | `pi install` |

---

## 2. 为什么需要学"用" Plugin？

你可能会问：插件装上之后不就能用了吗？还需要专门学？

因为：

1. **不同平台的入口不一样**：同一个 `text-processor-plugin`，装到 Claude Code 用 `/plugin`、装到 Codex 用 `/plugins`、装到 OpenCode 要重启进程。
2. **本地调试你总要做**：在 Claude Code 上线前，你需要把插件加载到本地客户端跑一遍。
3. **API Key 不会自己飞过来**：如果插件要访问 Hugging Face / OpenAI，你需要把 token 注入到客户端。
4. **第一次装失败很正常**：路径写错、JSON 缺逗号、MCP server 找不到 venv……这些都是新手必踩的坑。

> 学会"装"和"调"，你才算真正拥有了一个完整的插件开发能力。

---

## 3. 核心概念地图

| 术语 | 含义 | 出现频率 |
|---|---|---|
| **Marketplace** | "应用商店"清单文件，列出可安装的插件 | Claude Code / Codex |
| **Plugin / Package** | 实际可安装的扩展包 | 通用 |
| **`/plugin` 命令** | Claude Code 里的插件浏览器 | Claude Code |
| **`/plugins` 命令** | Codex 里的插件浏览器 | Codex |
| **`marketplace.json`** | 本地应用市场的清单文件 | Claude Code / Codex |
| **环境变量** | 装 API Key 的统一方式 | 通用 |
| **MCP Adapter** | 让本身不支持 MCP 的客户端也能用 MCP 工具 | Pi |
| **Restart / Reload** | 修改配置后必须重新加载 | 几乎所有平台 |

---

## 4. 通用四步走流程

不管哪个平台，"装插件"都长这样：

```text
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  1. 发现    │ →  │ 2. 安装      │ →  │ 3. 配置      │ →  │ 4. 使用      │
│             │    │             │    │             │    │             │
│ 找 marketplace, │ 复制到插件目录, │  export KEY=, │  自然语言/调用 │
│ 找本地目录    │ 运行 install  │  写 .mcp.json │  /skill 触发  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

下面 5~8 节分别讲四个平台怎么走完这四步。

---

## 5. Claude Code 怎么装插件

### 5.1 应用市场安装

```text
/plugin marketplace add <owner>/<repo>       # 告诉 Claude Code 去哪个仓库找
/plugin install <plugin-name>@<marketplace-name>   # 装哪个
```

`/plugin` 是 Claude Code 的插件浏览器，可以**启用 / 禁用 / 卸载** 任何插件。

### 5.2 本地目录安装（开发调试用）

Day47 我们主要用这种方式。第一步：写一个 `marketplace.json`：

```json
{
  "name": "local-example-plugins",
  "owner": { "name": "you" },
  "plugins": [
    {
      "name": "text-processor-plugin",
      "source": "./text-processor-plugin",
      "description": "Text analysis skills"
    }
  ]
}
```

第二步：在 Claude Code 里运行

```text
/plugin marketplace add /absolute/path/to/marketplace.json
/plugin install text-processor-plugin@local-example-plugins
```

Claude Code 接下来会：

1. 读 `.claude-plugin/plugin.json` 认识插件；
2. 加载 `skills/` 目录下的所有 `SKILL.md`；
3. 启动 `.mcp.json` 里声明的 MCP server。

### 5.3 改完之后怎么重新加载

本地开发时改了文件，**必须 disable 再 enable** 一次：

```text
/plugin   # 找 text-processor-plugin → disable → enable
```

或者直接重启 Claude Code。

### 5.4 怎么调用 Skill

两种方式：

**方式 A：自然语言**

```text
Analyze the reading level of this paragraph
```

Claude Code 会自己匹配到 `check-reading-level` skill。

**方式 B：显式命名空间**

```text
/text-processor-plugin:check-reading-level
```

新手推荐先用方式 A，看着感觉对再切换到 B 调试。

---

## 6. Codex 怎么装插件

Codex 的思路跟 Claude Code 很像，但**多了一个 "Repo Marketplace" 概念**。

### 6.1 插件浏览器安装

```text
/plugins
```

打开浏览器搜索、安装，然后**新建一个 thread** 才能用。

### 6.2 个人 Marketplace 安装

把插件复制到 `~/.codex/plugins/`：

```bash
mkdir -p ~/.codex/plugins
cp -R /local/path/to/text-processor-plugin ~/.codex/plugins/text-processor-plugin
```

然后编辑 `~/.agents/plugins/marketplace.json`。注意：这里的 `source.path` 是**相对 `~/.agents/plugins/`** 的：

```json
{
  "name": "local-example-plugins",
  "interface": {
    "displayName": "Local Example Plugins"
  },
  "plugins": [
    {
      "name": "text-processor-plugin",
      "source": {
        "source": "local",
        "path": "../../.codex/plugins/text-processor-plugin"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

Codex 加载时会：

1. 读 `.codex-plugin/plugin.json`；
2. 加载 `skills/`；
3. 启动 `.mcp.json` 中的 MCP server；
4. 缓存到 `~/.codex/plugins/cache/$MARKETPLACE/$PLUGIN/$VERSION/`。

### 6.3 仓库 Marketplace 安装

如果你想跟队友共享，直接在**项目根目录**创建：

```text
$REPO_ROOT/.agents/plugins/marketplace.json
```

用相对路径指向 `./plugins/text-processor-plugin`，然后重启 Codex。

### 6.4 怎么调用 Skill

**自然语言**：

```text
What's the reading level of this README?
```

**显式选择**：

```text
@text-processor-plugin
```

或者直接打字：

```text
Extract the top keywords from this document
```

### 6.5 改完之后怎么重新加载

修改 `~/.agents/plugins/marketplace.json` 或插件目录后，**必须重启 Codex**。

---

## 7. OpenCode 怎么装插件

OpenCode 的思路完全不同：**插件就是 `.js` / `.ts` 文件**，Skills 和 MCP 是另外两个独立通道。

### 7.1 从本地文件安装

把插件文件扔到下面两个目录之一：

```text
.opencode/plugins/              # 项目级
~/.config/opencode/plugins/     # 全局
```

重启 OpenCode 时会自动加载。

### 7.2 从 npm 安装

编辑 `opencode.json`：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["@your-org/text-processor-plugin"]
}
```

OpenCode 启动时用 Bun 自动安装。

### 7.3 Skills 和 MCP 怎么"配对"？

OpenCode 的 Skills 和 MCP 是**独立**的扩展点：

**Skills 配置**：

```bash
mkdir -p .opencode/skills/analyze-text
# 写一个 SKILL.md 进去
```

OpenCode 会自动从 `.opencode/skills/`、`.claude/skills/`、`.agents/skills/` 三个目录发现 Skills。

**MCP 配置**（仍然在 `opencode.json`）：

```json
{
  "mcp": {
    "text-processor": {
      "type": "remote",
      "url": "https://YOUR-USERNAME-text-processor-mcp.hf.space/gradio_api/mcp/"
    }
  }
}
```

### 7.4 怎么调用

```text
Summarize this file and note any text-analysis follow-up that would help.
```

如果插件注册了 hook（事件监听），它在对应事件触发时**自动运行**；如果注册了自定义工具，OpenCode 把它当作内置工具一起调用。

### 7.5 改完之后怎么重新加载

Bun 安装的包 → 直接重启 OpenCode。本地文件 → 删掉再加回来也能触发。

---

## 8. Pi 怎么装插件

Pi 的术语叫 **Package（包）**。

### 8.1 本地目录安装

```bash
pi install /local/path/to/text-processor-plugin -l
```

`-l` 标志把包写入项目级 `.pi/settings.json`。

### 8.2 从 npm / git 安装

```bash
pi install npm:@your-org/text-processor-plugin
pi install git:github.com/your-org/text-processor-plugin
```

### 8.3 配对 MCP

Pi 本身不直接支持 MCP，需要 `pi-mcp-adapter`：

```bash
pi install npm:pi-mcp-adapter
```

然后在 `.mcp.json` 里加：

```json
{
  "mcpServers": {
    "text-processor": {
      "url": "https://YOUR-USERNAME-text-processor-mcp.hf.space/gradio_api/mcp/"
    }
  }
}
```

### 8.4 怎么调用

```text
What's the reading level of this README?
/skill:check-reading-level What's the reading level of this README?
```

### 8.5 管理和重载

```bash
pi list          # 看装了哪些包
pi config        # 看当前配置
pi remove /local/path/to/text-processor-plugin
```

本地文件改完后，**在 Pi 里跑 `/reload`** 才会生效。

---

## 9. 四个平台安装方式对照表

| 平台 | 本地装法 | 网络装法 | 改后重载方式 |
|---|---|---|---|
| **Claude Code** | `/plugin marketplace add ./marketplace.json` | `/plugin marketplace add <owner>/<repo>` | `/plugin` 浏览器 disable/enable |
| **Codex** | 复制到 `~/.codex/plugins/` + 编辑 `~/.agents/plugins/marketplace.json` | `/plugins` 浏览器搜索 | **重启客户端** |
| **OpenCode** | 放到 `.opencode/plugins/` | npm 包名加到 `opencode.json` 的 `plugin` 数组 | **重启 OpenCode** |
| **Pi** | `pi install ./dir -l` | `pi install npm:...` 或 `pi install git:...` | Pi 里 `/reload` |

> **最容易踩的坑**：OpenCode 和 Pi 的"插件"和"Skills/MCP"是两套独立的扩展点，单独安装 Skills 不会自动带来 MCP 工具。

---

## 10. 配置 API Key

所有平台都需要把 API key 放到**环境变量**里。

```bash
export HF_TOKEN="hf_xxxxx"
export OPENAI_API_KEY="sk-xxxxx"
export GITHUB_TOKEN="ghp_xxxxx"
```

各平台读取方式：

| 平台 | 读法 |
|---|---|
| Claude Code | 读 shell 环境变量 |
| Codex | 读 shell 环境变量 |
| OpenCode | 读 shell 环境变量，**或者**在 `opencode.json` 的 `mcp.<server>.environment` 块里写 |
| Pi | 读 shell 环境变量；`pi-mcp-adapter` 支持从 `.mcp.json` 里插值 |

> **永远不要把 API Key 写进插件代码里**。环境变量是社区共识，平台 Secrets 是部署时的方案。

---

## 11. 常见问题排查

### 11.1 插件没加载？

按平台逐项检查：

**Claude Code**

```bash
cat ./my-plugin/.claude-plugin/plugin.json   # 1. 验证 manifest 合法
ls -la ./my-plugin/skills/                   # 2. 验证 skills 目录存在
```

然后 `/plugin` 里重新 enable 一次。

**Codex**

```bash
cat ~/.agents/plugins/marketplace.json       # 1. 验证 marketplace 格式
```

确认 `.codex-plugin/plugin.json` 里的 `skills` 和 `mcpServers` 路径都对：

```json
{
  "skills": "./skills/",
  "mcpServers": "./.mcp.json"
}
```

**OpenCode**

```bash
ls -la .opencode/plugins/                    # 1. 验证文件位置
```

如果插件引用外部包，确认 `.opencode/package.json` 里有 dependencies。

**Pi**

```bash
pi list                                      # 1. 看是否真的安装了
```

如果路径不对，编辑后用 `/reload`。

### 11.2 MCP server 启动失败？

按平台逐项排查：

| 平台 | 排查命令 |
|---|---|
| Claude Code | `cat ./.mcp.json` 验证 JSON 合法 |
| Codex | 同上，且确认 `.codex-plugin/plugin.json` 里 `mcpServers` 指向 `./.mcp.json` |
| OpenCode | `opencode mcp debug text-processor` |
| Pi | `cat ./.mcp.json`；在 Pi 内用 `/mcp`、`/mcp reconnect text-processor`、`/mcp tools` |

### 11.3 改了文件没生效？

| 平台 | 重新加载方式 |
|---|---|
| Claude Code | `/plugin` 里 disable/enable |
| Codex | **重启客户端** |
| OpenCode | **重启客户端** |
| Pi | Pi 内 `/reload` |

99% 的 "改了不生效" 问题都是这一条——别忘了重启。

---

## 12. 实战建议

1. **先在本地跑通，再上 Marketplace**
   - Day47 的 marketplace.json 已经写好一个最小可用版本，复制改一改就能用。

2. **路径用绝对路径，不要有空格和中文**
   - `/Users/yuyuan/agents-learn/...` 是好习惯；
   - `/Users/张三/我的项目/...` 这种路径在 shell 里会很痛苦。

3. **改完任何文件，都要重启或 reload**
   - 把这条当作"肌肉记忆"。

4. **记一份你自己的"踩坑清单"**
   - 第一次装一定会遇到路径、Python venv、API key 三个问题之一；
   - 记下来，下次就能 5 分钟搞定。

5. **用最新版客户端**
   - 不同版本 marketplace.json 字段可能差；
   - 升级前看 changelog。

6. **权限分层**
   - 验证用本地 marketplace；
   - 队友共享用 Repo Marketplace；
   - 大规模分发用官方 Marketplace。

---

## 13. 面试题与思考题

1. **"发现 → 安装 → 配置 → 使用" 这四步里，哪一步最容易出错？为什么？**
2. **Claude Code 和 Codex 的 Marketplace 有什么区别？**
3. **OpenCode 的 "插件"、Skills、MCP Server 是什么关系？**
4. **为什么 Pi 需要 `pi-mcp-adapter`？它和 Claude Code 的 MCP 集成有什么本质区别？**
5. **如果一个插件在 Claude Code 能用、在 Codex 不能用，通常是哪一步出了问题？**
6. **API Key 应该放在哪里？为什么？**
7. **改了本地插件文件后，Codex 必须重启才能生效，这跟 Claude Code 的 disable/enable 有什么设计差异？**

---

## 14. 要点总结

- 装插件的**通用流程**：发现 → 安装 → 配置 → 使用。
- **Claude Code**：用 `/plugin` 命令 + `marketplace.json`，改后 disable/enable。
- **Codex**：用 `/plugins` + `~/.agents/plugins/marketplace.json`，改后**重启**。
- **OpenCode**：插件是 `.js`/`.ts` 文件，Skills 和 MCP 是独立的扩展点。
- **Pi**：用 `pi install` 装包，MCP 需要 `pi-mcp-adapter`。
- API Key 走 **环境变量**，不要写进代码。
- **改了配置一定要重启 / reload**。

完成今天的学习后，你应该能：

- 在任意一个平台本地加载 Day46 的 `text-processor-plugin`；
- 排查 80% 的常见安装失败问题；
- 给同事写一份"如何安装我们的插件"的小文档。

---

**下一步：**

Unit 3 全部结束！建议用本仓库的 `examples/47-using-plugins/` 里的 `marketplace.json`，在你常用的客户端里**实际安装一次 Day46 的 text-processor-plugin**。只有真跑通了四步走流程，才算真正学完"插件"这一章。
