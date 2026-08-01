# Day52 — Unit 5: Hooks（钩子）

> 课程地址：https://huggingface.co/learn/context-course/unit5/introduction  
> 课件源码：https://github.com/huggingface/context-course/blob/main/units/en/unit5/introduction.mdx

---

## 1. 什么是 Hooks？

**Hooks 是用户自定义的处理函数（handlers）**，在 Agent 生命周期的特定节点被触发执行。

当 Agent 准备调用工具、结束一轮对话、或开始新会话时，运行时会暂停 → 调用已注册的 hook → 再继续执行。

### 典型生命周期

```text
User prompt
    │
    ├─[UserPromptSubmit hook]─► 记录日志 / 注入上下文
    ▼
Model reasoning
    │
    ├─[PreToolUse hook]─► 允许、拒绝、重写参数
    ▼
Tool executes
    │
    ├─[PostToolUse hook]─► 记录、分析、后处理
    ▼
Model continues
    │
    └─[Stop / SessionEnd hooks]─► 持久化、通知、清理
```

**核心定位：**

- **Skills / MCP / 插件 / 子 Agent**：决定 Agent **能做什么**
- **Hooks**：决定每个步骤**周围会发生什么**

Hooks 是处理**可观测性（observability）、护栏（guardrails）、自动化胶水（automation glue）**的正确层级。

---

## 2. 为什么 Hooks 很重要？

> 让模型承诺"每次改完代码都跑 linter"，它最终会忘记或表现不一致。但一个 `PostToolUse` hook 每次都能可靠地跑 linter。

**Hooks 把约定变成代码。**

### 三大核心应用场景

| 场景 | 说明 | 示例 |
|------|------|------|
| **可观测性** | 捕获每次工具调用、提示词、停止事件 | 写入日志或仪表盘 |
| **护栏** | 在 `Bash` 命令执行前检查并拦截 | 拒绝访问 `~/.ssh/` 或 `rm -rf /` |
| **自动化** | 文件编辑后自动运行格式化、类型检查、测试 | 由运行时处理，而非 Agent |

> 💡 **Note**：Linter（代码检查工具）用于检查代码错误、风格问题和项目规则违规，它扫描代码并报告问题，而不是运行整个程序。

---

## 3. 四大平台的 Hooks 对比

四个平台都支持 Hooks，但形式和命名不同：

| 平台 | 配置位置 | 事件命名风格 | Handler 形式 |
|------|---------|-------------|-------------|
| **Claude Code** | `.claude/settings.json` 或插件内 | `PascalCase`：`PreToolUse`、`Stop` | shell 命令、HTTP 端点、prompt、子 Agent |
| **Codex** | `.codex/hooks.json`，需在 `config.toml` 开启 feature flag | `PascalCase`，事件集较小 | shell 命令，通过 stdin 接收 JSON |
| **OpenCode** | `.opencode/plugins/` 的 TS/JS 插件模块 | 对象键名：`"tool.execute.before"` 或通用 `event` | 纯代码，无 JSON 事件配置 |
| **Pi** | `.pi/extensions/` 或 `~/.pi/agent/extensions/` | `lower_snake_case`：`before_agent_start`、`tool_call`、`tool_result` | 代码中用 `pi.on(...)` 注册 |

**共同心智模型**：事件触发 → handler 执行 → handler 可影响下一步。只有语法和事件名不同。

---

## 4. 本单元最终项目：Agent Activity Dashboard

本单元会带你：

1. 遍历 Hook 生命周期
2. 展示每个平台的确切配置格式
3. 构建一个 **Agent Activity Dashboard**

**Dashboard 是一个 Gradio 应用**，通过 HTTP 接收 hook 事件，实时可视化：

- 工具调用
- 提示词
- 会话状态

最终你会得到一个**能同时对接四个 Agent 平台**的统一仪表盘。

---

## 5. 本单元学习目标

完成本单元后，你将掌握：

- Claude Code、Codex、OpenCode、Pi 的共享 hook 生命周期
- 各平台 hook 配置的位置及 JSON/代码 格式
- Hook handler 如何通过退出码、JSON 输出、抛错或返回值影响 Agent
- 如何用 Gradio 构建实时 Agent 活动仪表盘

---

## 6. 下一节预告

> **Hook 事件本身的完整巡览**（接下来会逐个讲解生命周期中的各个事件）。
