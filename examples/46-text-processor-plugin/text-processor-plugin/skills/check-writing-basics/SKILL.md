---
name: check-writing-basics
description: |
  Use this skill when the user wants a quick rule-based check of basic
  English writing hygiene: repeated spaces, very long sentences (> 30
  words), and missing terminal punctuation. This is NOT a spell or grammar
  checker.
---

# check-writing-basics

When the user asks "are there any obvious problems with this text?",
"check my writing", or wants a quick linter-style review, call the MCP
tool `check_writing_basics` from the `text-processor` server.

## When to use

Trigger this skill when the user wants any of the following:

- "检查一下这段文字的基础写作问题。"
- "Any obvious issues with this paragraph?"
- "Is my text well-formatted?"
- "Quick editing pass on this draft."

Do NOT use this skill expecting it to detect spelling errors, grammar
errors, or style issues. It only checks a small set of deterministic
rules.

## Tool call

Call the `check_writing_basics` MCP tool on the `text-processor` server with:

- `text` (string, required): the English text to inspect.

The server returns a JSON object with:

- `issue_count` (total number of issue occurrences)
- `issues` (array of objects with `rule`, `count`, `message`)
- `warning` (re-states that this is rule-based)

The current rules are:

| Rule | Trigger |
|---|---|
| `repeated_spaces` | Two or more consecutive spaces |
| `long_sentences` | English sentence longer than 30 words |
| `terminal_punctuation` | Final character is not `.`, `!`, `?`, `。`, `！`, `？` |

## How to present the result

1. Summarize the issue count.
2. List each rule with its count and message.
3. End with the warning: this is not a spell or grammar checker.

## Example user requests

- "这段文字有哪些基础写作问题？"
- "Quick edit pass on this email."
- "Anything obviously wrong with this paragraph?"
