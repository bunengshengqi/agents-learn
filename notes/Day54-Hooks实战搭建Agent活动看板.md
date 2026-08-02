# Day54 — Unit 5: Hands-On 用 Hooks 搭一个 Agent 活动看板

> 课程地址：https://huggingface.co/learn/context-course/unit5/hands-on  
> 课件源码：https://github.com/huggingface/context-course/blob/main/units/en/unit5/hands-on.mdx  
> 上一节：Day53 - Hook 事件与智能体生命周期

---

## 0. 这节课在干嘛？一句话说清

Day52 讲了 Hooks 是啥，Day53 摊开了所有事件。但有个扎心的事实：**Hook 如果只写在配置里、不把信息输出到某处，就等于白写。** 你根本看不到 Agent 在背后干了啥。

这节课就把 Hooks **真正接起来**：搭一个网页看板，让你的 Agent（不管是 Claude Code、Codex、OpenCode 还是 Pi）每动一下，看板上就实时跳一条记录。你能亲眼看到它调了什么工具、参数是啥、有没有在一个工具上死循环。

> 💡 **大佬视角**：这玩意儿就是 Agent 的"黑匣子行车记录仪"。模型自己记性不可靠、日志散落各处，而这个看板把所有平台的行为**归一化到同一张表**里——这就是可观测性（observability）最朴素的样子。

可运行示例已放在仓库：`examples/54-agent-activity-dashboard/`（含 `app.py`、四平台 hook 配置、README）。

---

## 1. 你要搭的东西长什么样？

一个 Python 进程同时干两件事：

```text
┌──────────────────────────────────────────────┐
│  同一个进程 (python app.py, 端口 8000)        │
│                                              │
│  (1) FastAPI 端点  POST /event              │
│        ↑ 任何平台的 hook 都能往这发请求       │
│                                              │
│  (2) Gradio 网页 UI                          │
│        ↑ 每秒轮询内存缓冲，实时重绘表格+图    │
└──────────────────────────────────────────────┘
```

- **FastAPI** 负责"收件"：hook 把事件 POST 过来，它存进内存。
- **Gradio** 负责"展示"：每秒刷新一次，把最近事件画成表格和条形图。

为什么要合成一个进程？因为这样部署最简单——一个端口、一套依赖，hosting 方便。

---

## 2. 项目初始化

```bash
mkdir agent-activity-dashboard
cd agent-activity-dashboard
pip install "gradio>=4.41" "fastapi" "uvicorn[standard]" "pandas"
```

`requirements.txt` 就这四行（已备在示例里）：

```text
gradio>=4.41
fastapi
uvicorn[standard]
pandas
```

---

## 3. Step 1：看板本体 `app.py`（逐段白话）

我把官方 `app.py` 拆成 5 块讲，你就不会被一堆代码吓到。

### 3.1 内存缓冲：`deque`

```python
MAX_EVENTS = 500
events: deque[dict] = deque(maxlen=MAX_EVENTS)
```

`deque` 是个"两端都能进出"的队列，`maxlen=500` 表示**最多留 500 条，超出自动丢最旧的**。这就是看板的"临时记事本"——重启进程就没了（要持久化得换数据库，后面 Step 5 会说）。

### 3.2 归一化函数 `_normalize()`：四平台"方言"翻译官

四个平台发来的 JSON 长得不一样（Claude 叫 `hook_event_name`，Codex 叫 `tool_name`，Pi 在 body 里直接给 `tool`……）。`_normalize()` 把它们**统一成一种形状**：

```python
{
  "timestamp": "2026-04-20T10:15:02Z",
  "platform": "claude-code",   # 从 body.platform 或请求头 X-Platform 来
  "event":    "PreToolUse",    # 从 body.event 或 body.hook_event_name 来
  "tool":     "Bash",          # 从 body.tool 或 body.tool_name 来
  "args":     "{...}",         # 从 body.args / tool_input / prompt 来，最长 200 字
}
```

> 💡 这就是为什么看板能"通吃"四个平台：不是每个平台写一套前端，而是**入口统一翻译**。这是整个项目最聪明的一笔。

### 3.3 接收器：`POST /event`

```python
@api.post("/event")
async def event(req: Request):
    try:
        body = await req.json()
    except Exception:
        body = {}
    record = _normalize(body, {k.lower(): v for k, v in req.headers.items()})
    events.appendleft(record)          # 新事件放最前
    return JSONResponse({})            # 返回空，绝不拖慢调用方
```

关键点：**返回空 `{}`**。hook 调用看板只是为了"报个信"，看板慢不慢不能拖住 Agent 干活。同理 Codex/OpenCode/Pi 的发请求都带了超时（`--max-time 2` / `AbortSignal.timeout(2000)`）和"失败也不报错"（`|| true` / `catch {}`），目的都是**看板挂了也不能让 Agent 卡住**。

### 3.4 Gradio 视图：表格 + 条形图 + 小结

- `events_df()`：把内存事件变 DataFrame，最新在上。
- `tool_counts_df()`：用 `Counter` 数每个工具被调了多少次，取前 15。
- `summary_md()`：汇总总事件数、出现过的平台、出现过的工具。
- `gr.Timer(1.0).tick(refresh, ...)`：每秒调一次 `refresh()`，把表格、图、小结重画一遍——这就是"实时"的来源。
- `Clear events` 按钮：清空缓冲。

### 3.5 挂载：`gr.mount_gradio_app`

```python
app = gr.mount_gradio_app(api, ui, path="/")
```

把 Gradio 挂到 FastAPI 上，所以 `/event` 和网页 UI **共用一个进程、一个端口 8000**。

跑起来：`python app.py`，浏览器开 `http://localhost:8000`。一开始空的，正常。

> [!tip] 顺序坑
> `/event` 路由定义在 Gradio 挂载之前，所以 POST 会命中接收器；其他路径才落到 UI。要是反过来，你的事件可能全进了 UI 而不是接收器。

---

## 4. Step 2：把四个平台接上来

核心就一句：**所有平台都往 `POST http://localhost:8000/event` 发 HTTP JSON。** 区别只在"怎么发"。

### 4.1 Claude Code —— 最省事（原生 HTTP hook）

`.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse":  [{ "matcher": "*", "hooks": [{ "type": "http", "url": "http://localhost:8000/event", "headers": { "X-Platform": "claude-code" } }] }],
    "PostToolUse": [{ "matcher": "*", "hooks": [{ "type": "http", "url": "http://localhost:8000/event", "headers": { "X-Platform": "claude-code" } }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "http", "url": "http://localhost:8000/event", "headers": { "X-Platform": "claude-code" } }] }],
    "Stop":            [{ "hooks": [{ "type": "http", "url": "http://localhost:8000/event", "headers": { "X-Platform": "claude-code" } }] }],
    "SessionStart":    [{ "hooks": [{ "type": "http", "url": "http://localhost:8000/event", "headers": { "X-Platform": "claude-code" } }] }]
  }
}
```

Claude Code 自带 `type: "http"` 的 hook，运行时自动 POST，payload 里已经有 `hook_event_name` / `tool_name` / `tool_input`，`_normalize` 直接认，`X-Platform` 头标成 `claude-code`。

测试提示：`List the files in this directory, then read README.md and summarize it.`

### 4.2 Codex —— 用 `jq` + `curl` 自己拼

先开 feature flag（`~/.codex/config.toml`）：

```toml
[features]
codex_hooks = true
```

再把 hook 写到 `~/.codex/hooks.json`。Codex 的 hook 是 shell 命令，所以每个事件都用 `jq` 抽出字段、拼成 JSON，再用 `curl` 发出去：

```json
"PreToolUse": [{ "matcher": "Bash", "hooks": [{ "type": "command", "command": "jq -c '{platform:\"codex\", event:\"PreToolUse\", tool:.tool_name, args:.tool_input}' | curl -s --max-time 2 -X POST -H 'Content-Type: application/json' --data-binary @- http://localhost:8000/event || true" }] }]
```

> ⚠️ 两个保命细节：`--max-time 2`（最多等 2 秒，超时拉倒）+ `|| true`（发失败也不让 Agent 报错卡住）。**永远别让看板成为 Agent 的单点故障。**

测试（重启 Codex 后）：`Run \`ls\` in this directory and then show me the first 20 lines of app.py.`

### 4.3 OpenCode —— 写个 TS 插件

`.opencode/plugins/dashboard.ts`：

```ts
import type { Plugin } from "@opencode-ai/plugin"
const URL = process.env.DASHBOARD_URL ?? "http://localhost:8000/event"
async function send(event: string, payload: Record<string, unknown>) {
  try {
    await fetch(URL, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform: "opencode", event, ...payload }),
      signal: AbortSignal.timeout(2000) })
  } catch { /* dashboard offline: never block */ }
}
export const DashboardPlugin: Plugin = async () => ({
  "tool.execute.before": async (input, output) => send("PreToolUse", { tool: input.tool, args: output.args }),
  "tool.execute.after":  async (input, output) => send("PostToolUse", { tool: input.tool, args: ... }),
  event: async ({ event }) => {
    if (event.type === "session.created") await send("SessionStart", {})
    if (event.type === "session.idle") await send("Stop", {})
  },
})
```

注意 OpenCode 没有 `UserPromptSubmit`，这里用通用 `event` 回调在 `session.created` → `SessionStart`、`session.idle` → `Stop` 做近似。首次用要：

```bash
cd .opencode && bun init -y && bun add -d @opencode-ai/plugin
```

测试：`Read README.md and list its sections.`

### 4.4 Pi —— 写个 TS 扩展

`.pi/extensions/dashboard.ts`：

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent"
const URL = process.env.DASHBOARD_URL ?? "http://localhost:8000/event"
async function send(event: string, payload: Record<string, unknown>) {
  try {
    await fetch(URL, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform: "pi", event, ...payload }),
      signal: AbortSignal.timeout(2000) })
  } catch { /* never block */ }
}
export default function (pi: ExtensionAPI) {
  pi.on("session_start",       async () => send("SessionStart", {}))
  pi.on("before_agent_start",  async (e) => send("UserPromptSubmit", { args: e.prompt }))
  pi.on("tool_call",           async (e) => send("PreToolUse", { tool: e.toolName, args: e.input }))
  pi.on("tool_result",         async (e) => send("PostToolUse", { tool: e.toolName, args: e.details ?? e.content }))
  pi.on("agent_end",           async () => send("Stop", {}))
}
```

Pi 用 `pi.on("事件名", handler)` 注册，事件名是蛇形（`session_start` / `tool_call` / `agent_end`），和 Day53 对得上。启动 Pi 或 `/reload` 后测试：`Read README.md and list its sections.`

---

## 5. 事件长啥样（统一后的 payload schema）

| 字段 | 含义 |
|------|------|
| `timestamp` | UTC 时间（秒级）+ `Z` |
| `platform` | `claude-code` / `codex` / `opencode` / `pi` / `unknown` |
| `event` | `PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `Stop` / `SessionStart` 等 |
| `tool` | 工具名（可能为空） |
| `args` | 参数摘要，截断到 200 字符 |

**原始映射**：`platform`←`body.platform` 或头 `x-platform`；`event`←`body.event`/`hook_event_name`；`tool`←`body.tool`/`tool_name`；`args`←`body.args`/`tool_input`/`prompt`。

---

## 6. Step 3：亲眼看着它跑

终端 1 跑 `python app.py`，终端 2 跑 Agent，看板会冒出类似：

```text
timestamp              platform     event            tool    args
2026-04-20T10:15:02Z   claude-code  UserPromptSubmit          List the files…
2026-04-20T10:15:03Z   claude-code  PreToolUse       Bash    {"command":"ls"}
2026-04-20T10:15:03Z   claude-code  PostToolUse      Bash    {"exit_code":0,…}
2026-04-20T10:15:04Z   claude-code  PreToolUse       Read    {"path":"README…}
2026-04-20T10:15:04Z   claude-code  PostToolUse      Read    {"content":"# …
2026-04-20T10:15:06Z   claude-code  Stop                     …
```

条形图随工具调用实时累积。**一眼就能看出 Agent 是不是卡在同一工具上死循环**——这是光看模型输出永远发现不了的。

---

## 7. Step 4：顺手加一道护栏（guardrail）

既然已经在 `PreToolUse` 拦截了，不如顺手挡掉危险命令。给 Claude Code 的 `PreToolUse` 再加一个 `type: "command"` 的 hook（排在 http hook 之前）：

```json
"PreToolUse": [
  { "matcher": "Bash", "hooks": [{ "type": "command",
    "command": "jq -r '.tool_input.command // \"\"' | grep -Eq 'rm -rf|:\\(\\)\\{.*\\|.*&.*\\}:' && { echo 'blocked: dangerous shell pattern' >&2; exit 2; } || exit 0" }] },
  { "matcher": "*", "hooks": [{ "type": "http", "url": "http://localhost:8000/event", "headers": { "X-Platform": "claude-code" } }] }
]
```

退出码 `2` + stderr 消息 = 拦下这次工具调用。让 Agent 执行 `rm -rf /tmp/hook-guardrail-demo-delete-me`，会被拒绝并记进看板。

> 💡 其他平台的等价写法：OpenCode 在 `tool.execute.before` 里 `throw new Error("blocked: dangerous shell pattern")`；Codex 退出码 2，或打印 `jq -c '{hookSpecificOutput:{hookEventName:"PreToolUse", permissionDecision:"deny", permissionDecisionReason:"…"}}'`。**这就是 Day53 讲的"hook 如何影响 Agent"的实战落地。**

---

## 8. Step 5：部署到 Hugging Face Spaces（可选）

把 `app.py` + `requirements.txt` 推到 Spaces，hook URL 改成 `https://你的用户名-agent-dashboard.hf.space/event`。注意三件事：

1. **脱敏**：payload 可能含密钥，要在 `_normalize` 里处理掉。
2. **认证**：公开 Space 要加认证，或保持私有并用 token。
3. **持久化**：内存缓冲重启即失，要长期存得换 SQLite 或 Spaces volume。

---

## 9. 大佬总结（Key Takeaways）

1. **Hook 不输出就等于零。** 看板把原始事件变成可观察的视图，这是可观测性的最小可用形态。
2. **归一化是灵魂。** 四平台 payload 各异，入口统一翻译成一种形状，前端只写一套。
3. **健壮性第一。** 看板挂了绝不能拖垮 Agent：超时 + 失败不报错（`|| true` / `catch` / 空返回）。
4. **一个进程双表面。** FastAPI 收事件 + Gradio 展示，同端口同进程，部署简单。
5. **顺手就能加护栏。** 拦截危险命令只是多一个退出码 2 的 hook——Day53 的理论在这直接落地。

> 💡 **一句话带走**：Hooks 不是配置里的一行字，而是 Agent 的"黑匣子"。今天你亲手把它接亮了——之后无论是调试、审计还是防呆，你都能看见底下到底发生了什么。

---

## 10. 下一节预告

> Unit 5 收官：回顾 Hooks 在可观测性、护栏、自动化胶水三方面的定位，并展望 Agent 工程下一步往哪走。
