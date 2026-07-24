// Day46 Pi extension for the text-processor MCP server.
//
// Pi's "extension" hook is a function that receives the Pi runtime and
// can register lifecycle callbacks. This is the equivalent of a Hook in
// Claude Code or a plugin event handler in OpenCode.
//
// Usage:
//   1. From this directory, run `pi install . -l` to install locally.
//   2. If you also want the MCP tools, run `pi install npm:pi-mcp-adapter`
//      and make sure a `.mcp.json` points at the Day43 server.
//   3. Run `pi /reload` to activate.

export default function textProcessorExtension(pi: any) {
  pi.on("load", () => {
    console.log("Text Processor Pi extension loaded")
  })

  // Optional: hook tool calls so we can see when text-processor tools fire.
  pi.on("tool_call", (toolName: string) => {
    if (toolName && toolName.startsWith("text-processor.")) {
      console.log(`[text-processor-plugin] calling ${toolName}`)
    }
  })
}
