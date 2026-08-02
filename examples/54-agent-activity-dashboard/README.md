# Day54 示例：Agent Activity Dashboard（实时活动看板）

把 Day52/53 学的 Hooks 真正接起来——一个 **Gradio + FastAPI** 应用，通过 HTTP 接收四个 Agent 平台（Claude Code / Codex / OpenCode / Pi）发来的 hook 事件，实时展示工具调用、提示词和会话状态。

## 1. 跑起看板（接收器 + UI，同一个进程）

```bash
cd examples/54-agent-activity-dashboard
pip install -r requirements.txt
python app.py
```

浏览器打开 http://localhost:8000 。一开始是空的，属于正常——等你的 Agent 开始干活、hook 往这里发事件后，表格和条形图就会跳动。

> 原理速记：`app.py` 里 FastAPI 的 `POST /event` 路由先于 Gradio 挂载，所以发事件请求命中接收器，其他访问都进 UI。看板用内存里的 `deque`（最多 500 条）当缓冲，`gr.Timer(1.0)` 每秒重渲染一次。

## 2. 给你的 Agent 接上 hook

所有平台都是往 `POST http://localhost:8000/event` 发 JSON。`app.py` 的 `_normalize()` 会把四种不同形状统一成 `{timestamp, platform, event, tool, args}`。

下面每个文件放进对应位置即可（本仓库的 `hooks/` 子目录里已备好可直接复制的版本）：

### 2.1 Claude Code
把 `hooks/claude-code/settings.json` 的内容写到你的 `.claude/settings.json`（或某个插件的 `hooks/hooks.json`）。
它是 `type: "http"` 的 hook，运行时自动 POST 到看板，并带 `X-Platform: claude-code` 头。
测试：新会话里说 `List the files in this directory, then read README.md and summarize it.`

### 2.2 Codex
1. 在 `~/.codex/config.toml` 开启：`[features] codex_hooks = true`
2. 把 `hooks/codex/hooks.json` 写到 `~/.codex/hooks.json` 或 `<仓库>/.codex/hooks.json`。
   依赖 `jq` 和 `curl`。每个 hook 用 `jq` 抽出字段、`curl` 用 `--max-time 2` 发出，`|| true` 保证看板离线也不卡住 Agent。
测试（重启 Codex 后）：`Run \`ls\` in this directory and then show me the first 20 lines of app.py.`

### 2.3 OpenCode
把 `hooks/opencode/dashboard.ts` 放到 `.opencode/plugins/dashboard.ts`，然后：
```bash
cd .opencode
bun init -y
bun add -d @opencode-ai/plugin
```
重启 OpenCode 后测试：`Read README.md and list its sections.`

### 2.4 Pi
把 `hooks/pi/dashboard.ts` 放到 `.pi/extensions/dashboard.ts`（或 `~/.pi/agent/extensions/`），启动 Pi 或 `/reload`。
测试：`Read README.md and list its sections.`

## 3. 统一后的事件结构（payload schema）

| 字段 | 含义 |
|------|------|
| `timestamp` | UTC 时间（秒级）+ `Z`，如 `2026-04-20T10:15:02Z` |
| `platform` | 来源：`claude-code` / `codex` / `opencode` / `pi` / `unknown` |
| `event` | 事件名：`PreToolUse` / `PostToolUse` / `UserPromptSubmit` / `Stop` / `SessionStart` 等 |
| `tool` | 工具名（可能为空） |
| `args` | 参数摘要，最长截断到 200 字符 |

归一化映射：`platform`←`body.platform` 或头 `x-platform`；`event`←`body.event` 或 `body.hook_event_name`；`tool`←`body.tool` 或 `body.tool_name`；`args`←`body.args`/`tool_input`/`prompt`。

## 4. 加一道护栏（可选）

在 Claude Code 的 `PreToolUse` 里再加一个 `type: "command"` 的 hook，遇到 `rm -rf` 之类的危险命令就退出码 `2` 拦截（详见课件 Step 4）。OpenCode 用 `throw new Error(...)`，Codex 用退出码 2 或打印 `hookSpecificOutput` 的 deny。

## 5. 部署到 Hugging Face Spaces（可选）

把 `app.py` 和 `requirements.txt` 推到 Spaces，hook URL 改成 `https://你的用户名-agent-dashboard.hf.space/event`。注意：payload 可能含敏感信息，要在 `_normalize` 里脱敏；公开 Space 需加认证或保持私有；内存缓冲重启即失，要持久化可换 SQLite 或 Spaces volume。

## 目录结构
```
agent-activity-dashboard/
├── app.py                  # Gradio + FastAPI 服务端
├── requirements.txt
├── README.md
└── hooks/
    ├── claude-code/settings.json   # → .claude/settings.json
    ├── codex/hooks.json            # → ~/.codex/hooks.json
    ├── opencode/dashboard.ts       # → .opencode/plugins/dashboard.ts
    └── pi/dashboard.ts             # → .pi/extensions/dashboard.ts
```
