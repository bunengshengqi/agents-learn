# Day53 — Unit 5: Hook 事件与智能体生命周期

> 课程地址：https://huggingface.co/learn/context-course/unit5/hook-events  
> 课件源码：https://github.com/huggingface/context-course/blob/main/units/en/unit5/hook-events.mdx  
> 上一节：Day52 - Hooks 钩子入门

---

## 0. 先白话一句：这节课解决什么问题？

Day52 我们搞清楚了——**Hooks 是 Agent 生命周期特定节点上触发的小程序**。但那个"特定节点"到底有哪些？分别在什么时候开火？而且每个平台的叫法还不一样：Claude Code 叫 `PreToolUse`，OpenCode 叫 `tool.execute.before`，Pi 叫 `tool_call`。

这节课就干一件事：**把整条生命周期摊开，逐个点名每个事件，并告诉你每个平台具体长什么样。** 就像先给你一张地铁线路图，再带你去每个站台看站牌。

> 💡 **大佬视角**：学 Hooks 最容易踩的坑，是一上来就抄某个平台的 JSON 配置，结果换一个平台全懵。正确姿势是——**先记"生命周期"（通用的，只记一次），再记各平台的"方言"（具体的，按平台查表）**。

还想要更直观的感受？官方有个可交互的生命周期演示页：https://context-course-hook-lifecycle.static.hf.space （课程页里内嵌的那个 iframe 就是它）。

---

## 1. 共享生命周期：所有平台都绕不开的 6 个关键时刻

把镜头拉到最远，抽象到最高层——**任何 Agent 的一次会话，都会走过同样的几个阶段**：

```text
┌─────────────────────────────────────────────┐
│ 会话开始      SessionStart                   │
├─────────────────────────────────────────────┤
│ 每一轮反复执行：                             │
│   用户提交提示词   UserPromptSubmit           │
│   模型推理，可能调用工具                     │
│     每次工具调用前   PreToolUse               │
│     每次工具调用后   PostToolUse              │
│   本轮结束         Stop                       │
├─────────────────────────────────────────────┤
│ 会话结束      SessionEnd                      │
└─────────────────────────────────────────────┘
```

**把这张图刻进脑子。** 后面所有平台的事件，本质上都是把这 6 个节点**拆细、改名、或补几个额外事件**。

六个核心节点速记：

- `SessionStart` —— 开工
- `UserPromptSubmit` —— 你刚敲完回车，模型还没看到
- `PreToolUse` —— 工具要跑了，但还没跑
- `PostToolUse` —— 工具跑完了
- `Stop` —— 这一轮模型说完了
- `SessionEnd` —— 收工

> 💡 注意节奏：`PreToolUse` 和 `PostToolUse` 在一轮里可能触发**很多次**（每调一次工具就一对）；而 `SessionStart` / `Stop` / `SessionEnd` 通常一次会话里各出现一次。

---

## 2. 各平台事件对照：一张表看尽"方言"

四个平台描述同一套生命周期，只是**名字、配置位置、粒度**不同。下面逐个过。

### 2.1 Claude Code —— 事件最全的"全家桶"

配置在 `.claude/settings.json` 或插件里的 `hooks/hooks.json`，事件名全用 `PascalCase`。

**核心生命周期事件：**

| 事件 | 触发时机 |
|------|---------|
| `SessionStart` | 新会话开始（全新 / 恢复 / 压缩续接） |
| `InstructionsLoaded` | `CLAUDE.md` 文件已加载 |
| `UserPromptSubmit` | 用户提交提示词，模型看到之前 |
| `PreToolUse` | 工具调用执行前 |
| `PermissionRequest` | 即将弹出权限询问 |
| `PermissionDenied` | 工具调用被自动模式分类器拒绝 |
| `PostToolUse` | 工具调用返回后 |
| `PostToolUseFailure` | 工具调用失败 |
| `Stop` | 本轮结束 |
| `SessionEnd` | 会话关闭 |

**子代理与任务事件：** `SubagentStart` / `SubagentStop`（委派子代理起停）、`TaskCreated` / `TaskCompleted`（TodoWrite 任务列表变化）。

**环境事件：** `CwdChanged` / `FileChanged`（工作目录或追踪文件变化）、`WorktreeCreate` / `WorktreeRemove`（Git worktree 增删）、`PreCompact` / `PostCompact`（上下文压缩前后）、`ConfigChange` / `Notification`（配置变更 / Claude 发通知）。

**匹配器（matcher）：** 工具类事件可按工具名过滤，比如 `"matcher": "Bash"` 只管 Bash，`"matcher": "Edit|Write"` 管编辑类；更细的 `if` 条件还能用权限规则语法检查参数，比如 `"if": "Bash(rm *)"` 表示"命令以 `rm` 开头才触发"。

> 💡 Claude Code 还支持**四种 handler 形式**：shell 命令、HTTP 端点、prompt、子 Agent。这是四平台里最灵活的。

### 2.2 Codex —— 精简但同源

Codex 的 hooks 是**实验性功能，必须先开**。在 `~/.codex/config.toml`：

```toml
[features]
codex_hooks = true
```

事件配置在 `~/.codex/hooks.json` 或 `<仓库>/.codex/hooks.json`，也是 `PascalCase`，但事件集更小：

| 事件 | 触发时机 |
|------|---------|
| `SessionStart` | 会话开始。matcher 过滤 `source`：`startup` / `resume` / `clear` |
| `UserPromptSubmit` | 用户提示词提交 |
| `PreToolUse` | 受支持的工具调用前（含 `Bash`、`apply_patch`（即 Edit/Write）、MCP 工具） |
| `PermissionRequest` | 即将弹出权限询问 |
| `PostToolUse` | 受支持的工具调用后 |
| `Stop` | 本轮结束 |

> ⚠️ **大佬提醒**：Codex 的事件集刻意贴近 Claude Code 的经典生命周期，所以跨平台脚本好复用。但**它的工具拦截面比 Claude Code 窄**，并不能拦下所有工具路径，别想当然。另外 Codex hooks 迭代很快，小细节可能随版本变化。

匹配器是**正则**：工具事件对 `tool_name` 求值，`SessionStart` 对 `source` 求值。

### 2.3 OpenCode —— 写代码，不写 JSON

OpenCode **没有 JSON 事件配置**那种东西。它的 hooks 就是 `.opencode/plugins/` 下的 TypeScript / JavaScript 模块，导出的插件对象**键名就是事件名**，运行时在事件触发时调用对应键。

**一等公民的 typed 事件键：**

| 事件键 | 含义 |
|--------|------|
| `"tool.execute.before"` | 工具即将执行 |
| `"tool.execute.after"` | 工具执行完毕 |
| `"shell.env"` | 即将启动 shell 命令，可改环境变量 |
| `"experimental.session.compacting"` | 会话正在被压缩 |

**通用 `event` 回调** —— 收到 `{ event }`，按 `event.type` 区分，涵盖生命周期和 UI 事件：

```text
生命周期： session.created / updated / idle / compacted / deleted / error / diff / status
消息：     message.updated / removed / part.updated / part.removed
命令文件： command.executed / file.edited / file.watcher.updated
权限：     permission.asked / permission.replied
诊断：     lsp.client.diagnostics / lsp.updated
其他：     todo.updated / server.connected / installation.updated
UI：       tui.prompt.append / tui.command.execute / tui.toast.show
```

> ⚠️ OpenCode **没有 `UserPromptSubmit` 事件**。最接近的做法是：在通用 `event` 回调里，监听 `message.updated` 时读新用户消息。

### 2.4 Pi —— 扩展事件，蛇形命名

Pi 的 hooks 在 `.pi/extensions/` 或 `~/.pi/agent/extensions/` 下的 TS/JS 扩展里，事件名用 `lower_snake_case`。

**核心生命周期事件：**

| 事件 | 含义 |
|------|------|
| `session_start` | 会话开始（`startup` / `reload` / `new` / `resume` / `fork`） |
| `before_agent_start` | 收到用户提示词；可注入消息或改系统提示词 |
| `agent_start` | Agent 循环开始 |
| `turn_start` / `turn_end` | 单个模型轮次起 / 止 |
| `tool_call` | 工具执行前；可改参数或拦截 |
| `tool_result` | 工具执行后；可改写结果 |
| `agent_end` | 请求结束 |
| `session_shutdown` | 扩展运行时被拆除 |

**会话/控制事件：** `session_before_switch` / `session_before_fork`（拦截 `/new`、`/resume`、`/fork`、`/clone`）、`session_before_compact` / `session_compact` / `session_before_tree` / `session_tree`（上下文管理与树导航）、`model_select` / `user_bash`（换模型 / 用户主动跑 shell）。

Pi 不用 JSON hook 文件，而是在代码里 `pi.on("事件名", handler)` 注册，打包成扩展或 Pi 包发布。

> 💡 **四平台一句话总结**
> - **Claude Code**：事件最多最细，支持 4 种 handler。
> - **Codex**：集最小最聚焦，藏在 feature flag 后。
> - **OpenCode**：把 hook 折进插件系统，用 typed 函数键而非 JSON。
> - **Pi**：扩展事件，如 `before_agent_start` / `tool_call` / `tool_result`。

---

## 3. Hook 收到的"包裹"：事件输入详解

每个平台触发 hook 时，都会把当前上下文塞给你。差别在"怎么塞"。

### 3.1 Claude Code —— stdin 里的 JSON

命令型 hook 从 **stdin** 接收 JSON；HTTP 型 hook 把同样的 JSON 作为 POST body。公共字段：

```json
{
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse"
}
```

- 工具类事件额外带 `tool_name`、`tool_input`；`PostToolUse` 还带 `tool_response`；
- 子代理事件带 `agent_id`、`agent_type`；
- 项目根目录还能通过环境变量 `CLAUDE_PROJECT_DIR` 拿。

### 3.2 Codex —— 同样 stdin JSON

```json
{
  "session_id": "...",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/path/to/project",
  "hook_event_name": "PreToolUse",
  "model": "gpt-5-codex"
}
```

- 轮次级事件加 `turn_id`；
- 工具事件加 `tool_name`、`tool_use_id`、`tool_input`；对 `Bash` / `apply_patch` 命令在 `tool_input.command`；
- `PostToolUse` 带 `tool_response`；`UserPromptSubmit` 带 `prompt`；`Stop` 带 `stop_hook_active` 和 `last_assistant_message`。

### 3.3 OpenCode —— 直接是函数参数

OpenCode 的 hook 是 JS/TS 函数，不是 stdin 脚本。每个事件有 typed 的 `(input, output)` 签名：

```ts
"tool.execute.before": async (input, output) => {
  // input.tool       —— 工具名（如 "read"、"bash"）
  // input.sessionID  —— 会话标识
  // output.args      —— 工具参数（可改）
}
```

- `"tool.execute.after"` 在 `output` 上多带结果；
- `"shell.env"` 给你 `output.env` 可改；
- 通用 `event` 回调收到 `{ event }`，`event.type` 标识事件。
- 插件构造时还会拿到上下文对象 `{ project, directory, worktree, client, $ }`，用 `client.app.log({...})` 结构化日志，`$`（Bun shell）跑命令。

### 3.4 Pi —— 注册函数里的 event / ctx

```ts
pi.on("before_agent_start", async (event, ctx) => {
  // event.prompt        —— 用户提示词文本
  // event.systemPrompt  —— 本轮系统提示词
  // event.images        —— 附带的图片（如有）
});

pi.on("tool_call", async (event, ctx) => {
  // event.toolName      —— "bash"、"read"、"write" 等
  // event.toolCallId    —— 唯一工具调用 id
  // event.input         —— 可改的工具参数
});

pi.on("tool_result", async (event, ctx) => {
  // event.toolName / event.input / event.content
  // event.details / event.isError
});
```

> 💡 在 handler 里做异步（比如 `fetch`）时，用 `ctx.signal`，这样用户按 Esc 能取消你的请求。

---

## 4. Hook 怎么"反客为主"影响 Agent

Hooks 不只是旁观者——它能改变下一步发生什么。

### 4.1 Claude Code

**退出码（命令型 hook）：**

- 退出 `0` —— 放行，无改动。
- 退出 `2` 且 stderr 写消息 —— 按事件语义拦截或继续（如 `PreToolUse` 拦下工具调用，`UserPromptSubmit` 清空提示词）。

**stdout 里的 JSON 做更细控制：**

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "No network access in this project"
  }
}
```

还支持顶层 `continue`、`stopReason`、`suppressOutput`、`systemMessage`，以及旧式 `{ "decision": "block", "reason": "..." }`。

**HTTP hook** 把同样 JSON 作为 2xx 响应体返回；非 2xx 或超时按"非阻塞错误"处理。

### 4.2 Codex

- 退出 `0` —— 成功；
- 退出 `2` + stderr 消息 —— 按事件拦截或继续。

stdout JSON 形状近似 Claude Code：

```json
{
  "systemMessage": "Injected context for the model",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "No network access in this project"
  }
}
```

对 `SessionStart` / `UserPromptSubmit` / `PostToolUse`，`hookSpecificOutput` 还能带 `additionalContext` 往对话里注入文本。

### 4.3 OpenCode

OpenCode 靠**改 `output` 对象**或**抛错**来影响 Agent。想改写工具调用就改 `output.args`；想拦下就抛错：

```ts
"tool.execute.before": async (input, output) => {
  if (input.tool === "bash" && /rm -rf/.test(output.args.command ?? "")) {
    throw new Error("dangerous command blocked by policy")
  }
}
```

没有退出码，没有 stdin JSON，全部在代码里完成。

### 4.4 Pi

Pi 靠**返回结构化值**或**改 event 状态**来影响 Agent：

```ts
pi.on("tool_call", async (event) => {
  if (event.toolName === "bash" && /rm -rf/.test(event.input.command as string)) {
    return { block: true, reason: "dangerous command blocked by policy" };
  }
});

pi.on("before_agent_start", async (event) => ({
  systemPrompt: event.systemPrompt + "\n\nAlways explain risky shell commands before running them.",
}));
```

- `tool_call` 返回 `{ block: true, reason }` 取消工具；
- 改 `event.input` 重写参数；
- `tool_result` 返回 `{ content, details, isError }` 改写结果；
- `before_agent_start` 返回 `message` 或 `systemPrompt` 注入上下文。

---

## 5. 选对事件：常见需求速查表

| 你的目标 | 该用的事件 |
|---------|-----------|
| 记录每次工具调用 | `PreToolUse` / `tool.execute.before` / `tool_call` |
| 编辑后跑 linter | `PostToolUse`（匹配 `Edit\|Write`）/ `tool.execute.after` / `tool_result` |
| 拦截危险命令 | `PreToolUse` + 退出码 2 / 抛错 / `tool_call` 返回 `{ block: true }` |
| 每轮注入仓库上下文 | `UserPromptSubmit` + `additionalContext`（Claude/Codex）/ OpenCode 用 `event` 监听 `message.updated` / Pi 用 `before_agent_start` |
| 持久化会话状态 | `Stop` / `SessionEnd` / OpenCode 的 `session.idle` / Pi 的 `agent_end` 或 `session_shutdown` |
| 给 shell 加环境变量 | OpenCode 的 `shell.env` / Pi 在扩展里改 `tool_call` 或包一层用户 bash 处理 |

---

## 6. 大佬总结（Key Takeaways）

1. **生命周期是通用的，方言是各平台的。** 先记 6 个核心节点，再查表对号入座。
2. **Claude Code 事件最多最细，handler 形式最丰富（4 种）；** Codex 集小但同源；OpenCode 用 typed 函数键；Pi 用扩展事件。
3. **输入方式分化：** Claude / Codex 走 stdin JSON；OpenCode / Pi 直接在函数里拿参数。
4. **影响方式分化：** Claude / Codex 用退出码 + stdout JSON；OpenCode 抛错 / 改 output；Pi 返回值 / 改 event。
5. **选事件 > 写配置。** 目标定了，事件就定了，剩下各平台写法大同小异。

> 💡 **一句话带走**：Hook 事件就是 Agent 生命里的"打卡点"。你只要想清楚——**在哪一个打卡点、想干点什么、用什么平台的"方言"去说**——就通了。

---

## 7. 下一节预告

> 先做个小测验热热手，然后我们会把这些事件**真正接进一个实时的 Gradio 仪表盘（Agent Activity Dashboard）**，亲眼看到每次工具调用、提示词、会话状态在屏幕上跳出来。
