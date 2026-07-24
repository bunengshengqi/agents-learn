// Day46 OpenCode plugin for the text-processor MCP server.
//
// OpenCode is "code-first": the plugin entry is a TypeScript module that
// returns a map of lifecycle event handlers. MCP servers are configured
// separately in `opencode.json` under the `mcp` key.
//
// Usage:
//   1. Copy this file (and opencode.json) to your OpenCode project root.
//   2. Adjust the absolute paths in `opencode.json` if needed.
//   3. Run `opencode` and use `opencode mcp list` to verify the MCP server
//      is connected.
//   4. Ask the Agent to analyze text — the MCP tools will be available.

import type { Plugin } from "@opencode-ai/plugin"

export const TextProcessorPlugin: Plugin = async ({ client }) => {
  // Log once when the plugin is loaded so it's easy to verify it's active.
  await client.app.log({
    body: {
      service: "text-processor-plugin",
      level: "info",
      message: "Text Processor plugin initialized",
    },
  })

  return {
    // Run before every tool call. We use this to log when an analyze_text
    // call is about to happen — handy for tracing and debugging.
    "tool.execute.before": async (input, output) => {
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

    // Run after every tool call. Surface the call count so we can see the
    // plugin is wired up correctly.
    "tool.execute.after": async (input, output) => {
      if (input.tool === "extract_keywords") {
        await client.app.log({
          body: {
            service: "text-processor-plugin",
            level: "info",
            message: "extract_keywords finished",
          },
        })
      }
    },
  }
}

export default TextProcessorPlugin
