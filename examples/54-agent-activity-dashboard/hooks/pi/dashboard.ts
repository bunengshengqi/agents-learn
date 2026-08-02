import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

const URL = process.env.DASHBOARD_URL ?? "http://localhost:8000/event";

async function send(event: string, payload: Record<string, unknown>) {
  try {
    await fetch(URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform: "pi", event, ...payload }),
      signal: AbortSignal.timeout(2000),
    });
  } catch {
    // dashboard may be offline; never block the agent
  }
}

export default function (pi: ExtensionAPI) {
  pi.on("session_start", async () => {
    await send("SessionStart", {});
  });

  pi.on("before_agent_start", async (event) => {
    await send("UserPromptSubmit", { args: event.prompt });
  });

  pi.on("tool_call", async (event) => {
    await send("PreToolUse", { tool: event.toolName, args: event.input });
  });

  pi.on("tool_result", async (event) => {
    await send("PostToolUse", {
      tool: event.toolName,
      args: event.details ?? event.content,
    });
  });

  pi.on("agent_end", async () => {
    await send("Stop", {});
  });
}
