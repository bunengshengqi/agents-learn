---
name: analyze-text
description: |
  Use this skill when the user wants basic statistics about a text –
  character count, word count, sentence count, line count, unique words,
  or average word / sentence length. This is the deterministic statistics
  tool, not a semantic analysis tool.
---

# analyze-text

When the user asks for text statistics, readability metadata, or a quick
overview of a passage, call the MCP tool `analyze_text` from the
`text-processor` server.

## When to use

Trigger this skill when the user wants any of the following:

- "这段文字有多少字？"
- "Analyze this paragraph for me."
- "Give me the word count and sentence count."
- "How many unique words are in this passage?"
- "What's the average sentence length?"

Do NOT use this skill for semantic analysis, topic detection, or language
detection – it is purely numerical.

## Tool call

Call the `analyze_text` MCP tool on the `text-processor` server with the
following argument:

- `text` (string, required): the full input text, 1–50,000 characters.

The server returns a JSON object with the following keys:

- `total_characters`
- `characters_without_whitespace`
- `total_words`
- `unique_words`
- `total_sentences`
- `total_lines`
- `average_word_length`
- `average_sentence_length`

## How to present the result

1. Parse the returned JSON object.
2. Present the numbers in a friendly, tabular or bullet form.
3. Mention that this is a deterministic heuristic, not a semantic analysis.
4. If the user wanted meaning-level insights, recommend combining this
   with `extract-keywords` or `check-writing-basics`.

## Example user requests

- "这段文字有多少词、多少句？"
- "Analyze this paragraph for me."
- "How many unique words are in the following text?"
