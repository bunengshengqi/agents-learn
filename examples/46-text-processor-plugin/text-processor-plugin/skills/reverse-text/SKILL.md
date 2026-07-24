---
name: reverse-text
description: |
  Use this skill when the user wants to reverse the character order of a
  text – every character (including spaces and punctuation) is reversed
  in place. Useful for puzzles, obfuscation checks, or playful demos.
---

# reverse-text

When the user asks to "reverse this text", "flip the characters", or
wants to see the string written backwards, call the MCP tool
`reverse_text` from the `text-processor` server.

## When to use

Trigger this skill when the user wants any of the following:

- "把这段文字反转。"
- "Reverse this string."
- "Read this text backwards."
- "Flip the characters of this paragraph."

Do NOT use this skill when the user wants to reverse word order only –
this tool reverses character order, which usually breaks words apart.

## Tool call

Call the `reverse_text` MCP tool on the `text-processor` server with:

- `text` (string, required): the text whose characters to reverse.

The server returns a JSON string containing the reversed text directly
(so the tool output is a string, not an object).

## How to present the result

1. Show the reversed string.
2. Mention that the operation is at the character level, so words will
   be broken into mirrored letters.
3. If the user wanted word-order reversal, note that this tool does not
   do that and suggest a small wrapper.

## Example user requests

- "请把这段文字反转。"
- "Reverse this paragraph."
- "What does this text look like backwards?"
