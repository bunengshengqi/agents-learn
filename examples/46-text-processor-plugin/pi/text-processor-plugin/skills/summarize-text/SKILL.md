---
name: summarize-text
description: |
  Use this skill when the user wants a quick deterministic summary of a
  text. The tool returns the first N sentences of the passage as an
  "extractive summary" – it does NOT call an LLM or rephrase anything.
---

# summarize-text

When the user asks "give me a short version of this text" or "summarize
the first few sentences", call the MCP tool `summarize_text` from the
`text-processor` server.

## When to use

Trigger this skill when the user wants any of the following:

- "总结一下这段文字。"
- "Summarize this in 2 sentences."
- "Give me the gist of the opening paragraphs."
- "Provide a quick TL;DR."

Do NOT use this skill when the user wants an LLM-style abstractive
summary. If they need semantic compression, recommend running a
local LLM instead.

## Tool call

Call the `summarize_text` MCP tool on the `text-processor` server with:

- `text` (string, required): the text to summarize.
- `max_sentences` (integer, optional, default 2): number of leading
  sentences to keep, from 1 to 5.

The server returns a JSON object with:

- `summary` (the concatenated selected sentences)
- `source_sentences` (total sentence count of the input)
- `selected_sentences` (how many were actually kept)
- `method` (always "lead-sentence extractive summary; no LLM is used")

## How to present the result

1. Show the `summary` text.
2. Note how many sentences were selected vs. available.
3. Always pass through the `method` field so the user knows this is
   extractive, not abstractive.

## Example user requests

- "用 2 句话总结一下。"
- "TL;DR in 3 sentences."
- "Give me the first 2 sentences of this article."
