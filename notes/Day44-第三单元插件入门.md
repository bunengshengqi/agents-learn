---
title: Day44 - 第三单元：插件入门
date: 2026-07-23
tags:
  - AI-Agent
  - Context-Engineering
  - Plugin
  - Skill
  - MCP
  - Hook
  - Codex
  - HuggingFace-Context-Course
---

# 第44天：第三单元——插件入门

> [!abstract] 本章定位
> 第一单元学习 Skill，第二单元学习 MCP，第三单元开始学习 Plugin。插件不是用来替代 Skill 或 MCP 的“第五种神秘技术”，而是把 Skill、MCP 配置、Connector、Hook 和展示资源组合成一个可安装、可版本化、可分享的扩展包。本章先建立准确的心智模型，后续再拆解插件结构、创建方式、安装与分发。

## 0. 学习资料、图片和示例

- 在线教材：[Unit 3: Plugins](https://huggingface.co/learn/context-course/unit3/introduction)
- GitHub 原文：[unit3/introduction.mdx](https://github.com/huggingface/context-course/blob/main/units/en/unit3/introduction.mdx)
- Codex 官方文档：[Build plugins](https://learn.chatgpt.com/docs/build-plugins)
- 本地最小示例：[examples/44-plugin-introduction](../examples/44-plugin-introduction/README.md)
- 上一章：[Day43 - 实战构建并部署 MCP Server](Day43-实战构建并部署MCP服务器.md)

课程大纲截图已经保存到仓库：

![第44天课程大纲](assets/day44/01-course-outline.png)

今天的大纲只有四项：

```text
什么是插件？
语境的演变
插件为何重要
关键术语
```

看起来短，但它决定后面能否分清 Skill、MCP、Plugin、Integration 和 Marketplace。

---

## 1. 先用“工具箱”理解插件

假设你要让团队的 Agent 做代码审查，需要：

- 一份审查流程；
- 一套安全规则；
- 一个读取 GitHub PR 的连接；
- 一个在提交前运行检查的 Hook；
- 图标、说明和版本号。

如果分散交付，使用者需要执行：

```text
复制 Skill
→ 配置 MCP Server
→ 授权 GitHub
→ 安装 Hook
→ 阅读安装文档
→ 自己确保版本匹配
```

插件把这些内容装进一个有清单的工具箱：

```text
code-review-plugin/
├── manifest：这个工具箱是谁、版本多少、包含什么
├── skills：怎么完成代码审查
├── MCP / Connector：怎样读取 PR 和仓库数据
├── hooks：在哪个生命周期自动检查
└── assets：图标、截图和展示资料
```

使用者面对的是：

```text
安装插件 → 审查权限 → 启用需要的组件 → 使用
```

一句话定义：

> Plugin 是面向安装和分发的扩展包，它把 Agent 所需的知识、能力、自动化和元数据组合起来。

### 1.1 Plugin 与手机 App 的类比

```text
Agent 平台   ≈ 手机操作系统
Plugin       ≈ 可安装 App
Manifest     ≈ App 的名称、版本、权限和入口说明
Skill        ≈ App 内的一项标准操作流程
MCP Server   ≈ App 访问后端服务的接口
Connector    ≈ 登录 GitHub、Slack 等外部账号的连接
Hook         ≈ 在特定事件发生时自动执行的机制
Marketplace  ≈ App Store / 插件目录
```

类比只帮助入门。Plugin 不一定有可视化界面，也不一定包含运行代码；只打包一个 Skill 也可以成为合法插件。

---

## 2. 什么是插件？

Hugging Face 课程把插件描述为：

```text
可复用的代码代理扩展
预先构建、经过整理和测试、可以分享的上下文包
```

这里“上下文包”不只是文字上下文，还可能包含实时工具和自动化。

### 2.1 一个插件可能包含什么？

| 组件 | 提供什么 | 是否必需 |
|---|---|---:|
| Manifest | 名称、版本、组件路径、展示信息 | 必需 |
| Skills | 可复用工作流和领域知识 | 可选 |
| MCP Server 配置 | 实时工具、数据和动作 | 可选 |
| App / Connector | 外部服务连接和授权 | 可选 |
| Hooks | 生命周期事件中的自动检查 | 可选 |
| Assets | 图标、Logo、截图 | 可选 |

Codex 当前要求每个插件都有：

```text
.codex-plugin/plugin.json
```

其余内容按需组合。

### 2.2 Plugin 不是一个新的通信协议

MCP 定义 Client 与 Server 怎样通信；Plugin 定义一组扩展怎样被打包、安装和发现。

```text
MCP 关心：消息怎么交换、Tool 怎样调用
Plugin 关心：哪些组件属于同一个扩展、怎样安装和分发
```

Plugin 可以包含 MCP 配置，但 Plugin 本身不是 MCP Server。

### 2.3 Plugin 也不是一个超大 Prompt

Prompt 主要给模型指令；Plugin 还可以包含：

- 版本和作者信息；
- 多个 Skills；
- 可执行 Tool；
- OAuth Connector；
- 生命周期 Hook；
- 权限与安装策略；
- Marketplace 元数据。

把 Plugin 只理解成“提示词文件夹”，会忽略它的分发与权限边界。

---

## 3. 不同平台的 Plugin 不是同一种文件格式

课程特别提醒：Plugin 的精确形态取决于平台。

### 3.1 Claude Code 与 Codex：Manifest-first Bundle

这类系统通常有：

```text
一个插件目录
一个 Manifest
可选 Skills / MCP / Hooks / Integrations
```

Manifest 就像包裹外面的装箱单，平台先读它，知道里面有什么。

### 3.2 OpenCode：JavaScript / TypeScript Module

课程指出 OpenCode 的插件更像代码模块：

- 从本地文件加载；
- 或通过 npm 包分发；
- 可以挂接 Agent 生命周期；
- 通过代码增加行为或 Tool。

### 3.3 为什么这个差异重要？

因为“Plugin”是一个产品层概念，不是一套全行业统一规范。

不要做以下假设：

```text
Claude 插件目录复制到 Codex 一定可用      ×
Codex plugin.json 放到 OpenCode 一定可用 ×
所有平台都支持相同 Hook 事件              ×
所有 Marketplace 的元数据格式相同        ×
```

跨平台迁移时，应该复用业务知识和工具协议，再为目标平台建立相应包装层。

---

## 4. 语境的演变：Prompt → Skill → MCP → Plugin

课程用四个阶段描述 Agent 上下文工程的发展：

```text
Prompt
  ↓
Skill
  ↓
MCP Server
  ↓
Plugin
```

这不是“新版完全淘汰旧版”，而是逐步增加可复用性与能力边界。

### 4.1 第一阶段：Prompt

例如：

```text
请审查这段 Python，关注 SQL 注入、路径穿越和密钥泄漏。
```

优点：

- 写起来最快；
- 适合一次性任务；
- 可以快速试验想法。

缺点：

- 每次重新输入；
- 容易漏掉步骤；
- 团队成员写法不同；
- 难以配套脚本、资料和测试。

Prompt 适合“这一次怎么做”。

### 4.2 第二阶段：Skill

Skill 把稳定的工作流整理为：

```text
SKILL.md
├── 名称
├── 触发描述
├── 完整操作说明
├── 可选 references
├── 可选 scripts
└── 可选 assets
```

优点：

- 可复用；
- 可以按任务按需加载；
- 便于维护工作方法；
- 能附带脚本、模板和参考资料。

但 Skill 主要解决“Agent 应该怎样完成任务”，并不天然等于一套外部服务连接、安装目录、Marketplace 版本和生命周期自动化。

Skill 适合“这一类任务怎么做”。

### 4.3 第三阶段：MCP Server

MCP 解决 Agent 怎样连接实时能力：

```text
读文件
调用 API
查询数据库
访问浏览器
操作 GitHub / Slack / Figma
```

优点：

- 标准化 Tool、Resource、Prompt；
- Client 与 Server 解耦；
- 本地 stdio 和远程 HTTP 都能工作；
- 多种 Agent 可以复用同一个 Server。

难点：

- 需要安装和配置；
- 处理认证、Transport 和权限；
- 单独交付 MCP Server 不一定包含“什么时候、怎样组合这些工具”的完整工作流。

MCP 适合“Agent 能做什么、怎样连接能力”。

### 4.4 第四阶段：Plugin

Plugin 将前面的组件放进一个可分发单元：

```text
Plugin
├── Skill：怎么做
├── MCP：能做什么
├── Connector：连接谁
├── Hook：什么时候自动做
├── Manifest：它是谁、含什么
└── Marketplace：从哪里发现和安装
```

Plugin 适合“怎样把一套成熟能力交付给别人”。

### 4.5 四者是组合关系，不是替换关系

| 需求 | 最小合适选择 |
|---|---|
| 只在当前对话里加一句要求 | Prompt |
| 反复执行一套固定工作流 | Skill |
| 访问实时数据或执行外部动作 | MCP / Connector |
| 把一套成熟能力安装给团队 | Plugin |

一个好的 Plugin 内部仍然需要好的 Prompt、Skill 和 MCP Tool。

---

## 5. 为什么插件重要？

### 5.1 对个人：减少重复安装和配置

假设你换了一台电脑。没有 Plugin 时可能要：

- 找到 Skill 仓库；
- 手工复制文件；
- 配 MCP Server；
- 写 Hook；
- 找回说明；
- 检查版本。

插件把这套经过整理的能力作为一个整体交付，减少“能用但每次都要重新搭”的摩擦。

### 5.2 对团队：建立一致性

团队最常见的问题不是“没有方法”，而是：

```text
A 使用旧版规则
B 忘记配置工具
C 自己改了 Prompt
D 的 Hook 没安装
```

插件可以通过统一版本和组件减少漂移：

- 相同 Skill；
- 相同 Tool 来源；
- 相同默认提示；
- 相同 Hook 规则；
- 相同升级路径。

插件不是自动保证质量，而是为一致性提供可管理的载体。

### 5.3 对社区：形成可发现的作品

单个 Markdown 片段很难说明：

- 它是谁维护的；
- 当前版本是什么；
- 是否包含外部 Tool；
- 怎样安装；
- 是否需要权限；
- 从哪里升级。

Plugin + Manifest + Marketplace 让扩展成为更完整的可分享工件。

### 5.4 对维护者：有版本、有边界、有升级入口

Manifest 中的版本号让维护者能够表达：

```text
0.1.0  初始实验
0.2.0  增加 Skill
1.0.0  稳定发布
2.0.0  可能包含不兼容变化
```

实际版本策略由项目决定，但总比“大家电脑上有一份不知道什么时候复制的文件夹”更可追踪。

---

## 6. 插件不是免费午餐

安装方便也意味着一次引入更多能力。

### 6.1 插件扩大了什么？

一个插件可能带来：

- 新指令影响 Agent 决策；
- MCP Tool 访问文件、网络或账号；
- Connector 读取私有工作区数据；
- Hook 在生命周期自动运行命令；
- 第三方依赖和供应链风险。

所以“只安装一个插件”不等于“只复制了一段文字”。

### 6.2 安装前至少检查什么？

```text
来源和维护者
Manifest 声明的组件
Skill 的实际指令
MCP Server 的命令或 URL
需要的账号和权限
Hook 在什么事件运行什么命令
依赖与安装脚本
版本、许可证、更新记录
```

### 6.3 Hook 为什么要格外小心？

Hook 是事件触发的自动化。例如会话启动、命令执行前后、文件编辑时运行脚本。它比手动 Tool 更容易在用户没有主动点击时执行。

Codex 官方文档明确说明：安装或启用插件不会自动信任它捆绑的 Hook；用户仍需查看和信任当前 Hook 定义。这是一个重要的安全边界。

### 6.4 密钥不能打包进插件

不要在插件中提交：

```text
API Key
OAuth Token
Cookie
私钥
个人绝对路径
生产数据库密码
```

插件应声明需要什么连接或环境变量，让安装者在自己的安全环境中授权。

---

## 7. 关键术语逐个讲清楚

### 7.1 Skill

定义：可复用的任务工作流与元数据。

它回答：

```text
遇到这种任务，Agent 应该遵循什么步骤？
```

例子：

- 如何审查 Pull Request；
- 如何生成周报；
- 如何分析数据表；
- 如何发布 Python 包。

### 7.2 MCP Server

定义：通过 Model Context Protocol 提供 Tools、Resources 和 Prompts 的服务。

它回答：

```text
Agent 可以读取什么、调用什么、执行什么？
```

例子：

- 查询数据库；
- 读取项目管理系统；
- 控制浏览器；
- 搜索公司文档。

### 7.3 Integration / App / Connector

定义：把 Agent 与 GitHub、Slack、Google Drive、Notion 等外部服务连接起来的集成。

它通常涉及：

- OAuth 登录；
- 用户或工作区身份；
- 权限范围；
- 私有数据；
- 服务端 API。

Integration 比普通网页搜索更适合访问用户授权的私有数据。

### 7.4 Manifest

定义：插件的机器可读清单。

它告诉平台：

- 插件名称和版本；
- 描述与作者；
- Skills 在哪里；
- MCP 配置在哪里；
- Apps 和 Hooks 在哪里；
- UI 中怎样展示。

Codex 的入口是：

```text
.codex-plugin/plugin.json
```

Manifest 不是 Skill 的执行说明，而是插件的“身份证 + 装箱单”。

### 7.5 Marketplace

定义：一个插件目录或插件源。

它负责：

- 列出有哪些 Plugin；
- 提供来源位置；
- 控制是否可安装；
- 组织分类和展示顺序；
- 支持发现、安装和升级。

Marketplace 不是 Plugin 本身，就像 App Store 不是某一个 App。

### 7.6 Hook

定义：在 Agent 生命周期事件发生时自动运行的逻辑。

它回答：

```text
什么时候自动检查、阻止、补充或记录？
```

例子：

- 会话开始时加载项目背景；
- 工具调用前检查权限；
- 文件修改后运行格式检查；
- 结束时写审计日志。

### 7.7 Dependency

依赖是插件运行所需的外部内容，例如 CLI、Python 包、Node 包、MCP Server 或账号授权。

“Skill 缺少依赖管理”是课程为了表达演进做的简化。Skill 可以附带脚本和说明，但 Plugin 更适合作为整体安装、版本和分发边界。

---

## 8. 用一张表彻底分清

| 概念 | 核心目的 | 典型文件/形式 | 是否执行外部动作 | 是否用于分发 |
|---|---|---|---:|---:|
| Prompt | 一次性指令 | 对话文本 | 通常否 | 弱 |
| Skill | 可复用工作流 | `SKILL.md` | 可指导 Tool | 可以单独分享 |
| MCP Server | 标准化实时能力 | stdio / HTTP 服务 | 可以 | 可独立部署 |
| Connector | 连接授权服务 | App 配置/OAuth | 可以 | 可作为集成发布 |
| Hook | 生命周期自动化 | Hook 配置和脚本 | 可以 | 可随插件打包 |
| Manifest | 描述插件 | `plugin.json` | 否 | 是 |
| Plugin | 安装与分发单元 | 目录 + Manifest + 组件 | 取决于组件 | 是 |
| Marketplace | 发现与安装目录 | Catalog JSON / 远程目录 | 否 | 管理 Plugin |

---

## 9. Codex 插件的最小结构

本章用 `plugin-creator` 官方技能生成了一个教学骨架：

```text
day44-hello-plugin/
├── .codex-plugin/
│   └── plugin.json
└── skills/
    └── hello/
        └── SKILL.md
```

这是一个真实可验证的最小结构，但本章不会安装它。

### 9.1 plugin.json

```json
{
  "name": "day44-hello-plugin",
  "version": "0.1.0",
  "description": "A minimal educational plugin...",
  "skills": "./skills/",
  "interface": {
    "displayName": "Day44 Hello Plugin"
  }
}
```

逐项解释：

- `name`：稳定、机器可读的插件 ID，通常使用 kebab-case；
- `version`：插件版本；
- `description`：它解决什么问题；
- `skills`：插件内 Skill 目录，相对插件根目录；
- `interface`：安装页面中的展示信息。

插件外层目录名应与 `name` 保持一致，减少安装和命名空间混乱。

### 9.2 路径为什么写 `./skills/`？

Manifest 应使用相对于插件根目录的路径：

```text
./skills/
./.mcp.json
./.app.json
./hooks/hooks.json
./assets/logo.png
```

不能依赖作者电脑上的：

```text
/Users/name/Desktop/my-plugin/skills
```

安装到别人的机器后，这个绝对路径肯定不存在。

### 9.3 SKILL.md

```markdown
---
name: hello
description: Greet a learner and explain...
---

# Hello from Day 44

1. Greet the learner.
2. Explain that this skill is one component inside the plugin.
```

它描述一项工作流，而不是整个插件。

```text
day44-hello-plugin = 工具箱
hello skill        = 工具箱里的一张说明卡
```

### 9.4 为什么示例没有 MCP、App 和 Hook？

因为它们都是可选组件。学习顺序应该是：

```text
先理解最小 Manifest + Skill
→ 再加 MCP
→ 再加 Connector
→ 最后谨慎加入自动 Hook
```

每增加一个组件，都增加能力、安装复杂度和权限面。

---

## 10. 一个完整插件可能长什么样？

Codex 官方结构大致是：

```text
my-plugin/
├── .codex-plugin/
│   └── plugin.json       必需：Manifest
├── skills/
│   └── my-skill/
│       └── SKILL.md      可选：工作流
├── hooks/
│   └── hooks.json        可选：生命周期 Hook
├── .app.json             可选：App / Connector 映射
├── .mcp.json             可选：MCP Server 配置
└── assets/               可选：图标、Logo、截图
```

注意：

```text
.codex-plugin/ 目录里只放 plugin.json
skills、hooks、assets 等放插件根目录
```

### 10.1 一个组件怎样进入插件？

Manifest 可以通过相对路径指向组件：

```json
{
  "skills": "./skills/",
  "mcpServers": "./.mcp.json",
  "apps": "./.app.json",
  "hooks": "./hooks/hooks.json"
}
```

可以把 Manifest 想象为电源排插：它把多个组件接到同一个安装包入口。

---

## 11. 插件安装后大致发生什么？

不同平台细节不同，但概念流程通常是：

```text
1. 从 Marketplace 或本地源找到 Plugin
2. 下载或复制插件目录
3. 读取并验证 Manifest
4. 显示名称、版本、作者和能力
5. 请求必要授权
6. 注册 Skills、MCP、Apps 和 Hooks
7. 用户启用需要的组件
8. 新会话加载相应能力
9. 更新时替换为新版本并重新验证
```

Codex 本地 Marketplace 的安装副本可能进入插件缓存目录，而不是永远直接读取开发目录。因此修改本地源后，通常需要刷新、重新安装或重启相应客户端，不能假设编辑文件立即影响已安装副本。

---

## 12. Plugin、Skill、MCP 怎么组合？

以“客户支持插件”为例：

```text
support-plugin/
├── Skill：如何判断问题类型、怎样组织回复
├── Zendesk MCP：读取工单、添加备注
├── Slack Connector：通知值班团队
├── Hook：发送前检查敏感信息
└── Manifest：版本、作者、组件和展示信息
```

用户说：

```text
帮我处理今天最紧急的客户问题。
```

可能发生：

```text
Skill 提供分诊步骤
→ MCP 查询工单
→ Agent 判断优先级
→ Skill 指导撰写回复
→ Hook 检查是否泄露隐私
→ Connector 通知 Slack
```

Plugin 的价值不是它自己完成所有步骤，而是它把协同工作的组件一起交付。

---

## 13. 什么时候不应该创建 Plugin？

### 13.1 只是当前任务的一句话要求

直接写 Prompt，不需要为了“专业”创建目录和版本。

### 13.2 只有你自己反复使用的一套简单流程

先做本地 Skill。Codex 官方文档也建议：仍在迭代单个仓库或个人工作流时，从本地 Skill 开始。

### 13.3 只是提供一个独立 API Tool

先做 MCP Server。如果暂时不需要统一安装 Skill、Hook 和展示资源，没必要立刻再包一层 Plugin。

### 13.4 流程还没有稳定

如果每周都大改工作流、接口和权限，先在本地迭代。过早发布 Plugin 会把不成熟的行为扩散到团队。

### 13.5 适合创建 Plugin 的信号

- 需要分享给团队；
- 同时包含多个组件；
- 需要版本和升级路径；
- 需要 Marketplace 发现；
- 安装步骤多且容易出错；
- 工作流已经过测试并相对稳定。

---

## 14. 本章示例如何检查？

### 14.1 教学验证器

```bash
python3 examples/44-plugin-introduction/validate_example.py
```

它检查：

- Manifest 是否存在并且是合法 JSON；
- `name`、`version`、`description` 是否存在；
- 目录名和插件名是否一致；
- `skills` 是否是 `./` 开头的相对路径；
- 每个 Skill 是否存在 `SKILL.md`；
- Skill 是否有 `name` 和 `description` frontmatter。

### 14.2 plugin-creator 严格验证器

```bash
.venv/bin/python \
  ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  examples/44-plugin-introduction/day44-hello-plugin
```

本章没有创建 Marketplace，也没有安装插件。原因是安装属于外部状态变更；学习结构不需要改变当前 Codex 环境。

---

## 15. 常见误区

### 误区1：Plugin 就是 Skill 的新名字

不是。Skill 是一项工作流，Plugin 是可安装的组合与分发单元。Plugin 可以包含一个或多个 Skill。

### 误区2：Plugin 一定包含 MCP Server

不是。最小插件可以只包含 Manifest 和 Skill。MCP 是可选组件。

### 误区3：安装插件后所有组件都应自动获得最高权限

危险。每个 Connector、MCP Tool 和 Hook 都应按最小权限审查。插件安装不应该绕过授权。

### 误区4：Marketplace 会运行插件

Marketplace 主要负责列出来源和安装策略；实际组件由 Agent 平台加载和运行。

### 误区5：所有平台插件格式完全兼容

不是。Plugin 是平台相关的包装层，Claude Code、Codex 和 OpenCode 的结构和运行机制不同。

### 误区6：Plugin 越大越好

不是。一个插件聚焦一个清晰能力域更容易理解、授权、测试和升级。把所有工具塞进“万能插件”会扩大权限和故障面。

### 误区7：安装成功等于业务质量可靠

Manifest 合法只证明结构能被识别，不证明 Skill 正确、Tool 安全或 Hook 没有副作用。仍然需要功能测试、安全审查和真实任务评估。

---

## 16. 第三单元接下来学什么？

根据课程目录，后续内容包括：

```text
Day44  Unit 3 Introduction：建立插件心智模型
后续   Plugin Anatomy：逐个认识 Manifest 和组件
后续   Building Your Own Plugin：创建插件
后续   Quiz 1：基础概念检查
后续   Using Plugins：安装、启用和使用
后续   Quiz 2：构建与分发检查
```

今天不急着创建复杂 MCP 和 Hook。先能准确回答：

```text
Plugin 为什么存在？
它与 Skill、MCP 有什么区别？
Manifest 和 Marketplace 分别负责什么？
安装插件会带来哪些权限和供应链风险？
```

---

## 17. 要点总结

```text
1. Plugin 是可安装、可版本化、可分享的 Agent 扩展包。
2. Codex Plugin 必须有 .codex-plugin/plugin.json。
3. Skill 负责“怎么做”，MCP 负责“能做什么”，Plugin 负责“怎么一起交付”。
4. Connector 连接外部服务，Hook 在生命周期事件中自动运行。
5. Marketplace 是插件目录，不是插件本身。
6. Prompt → Skill → MCP → Plugin 是能力逐层增加，不是旧技术被淘汰。
7. 不同 Agent 平台对 Plugin 的文件格式和执行模型不同。
8. 一个 Plugin 可以只有一个 Skill，不必一次加入所有组件。
9. 插件越容易安装，越需要认真审查来源、权限、MCP 和 Hook。
10. 个人未稳定工作流先做 Skill；团队分发和组合组件时再做 Plugin。
```

---

## 18. 自测题

1. 用“工具箱”类比说明 Plugin 与 Skill 的关系。
2. 为什么 Plugin 本身不是 MCP Server？
3. Prompt、Skill、MCP、Plugin 各自最适合解决什么问题？
4. Codex Plugin 唯一必需的入口文件是什么？
5. Manifest 和 Marketplace 有什么区别？
6. Integration / Connector 为什么通常涉及 OAuth 和私有数据？
7. 安装插件前为什么需要单独审查 Hook？
8. 为什么课程的“语境演变”不能理解为 Plugin 淘汰了 Prompt？
9. 哪些情况下应该先做本地 Skill，而不是 Plugin？
10. 一个只含 Manifest 和 Skill 的插件为什么仍然是合法 Plugin？

能不用看笔记回答这些问题，就完成了第44天的核心学习目标。
