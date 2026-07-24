---
name: extract-keywords
description: |
  Use this skill when the user wants to extract the most frequent
  English keywords from a passage. The tool strips stopwords and counts
  case-insensitive word frequencies. It is English-only.
---

# extract-keywords

When the user asks for the "main words", "topics", or "keywords" of an
English passage, call the MCP tool `extract_keywords` from the
`text-processor` server.

## When to use

Trigger this skill when the user wants any of the following:

- "提取这段英文的关键词。"
- "What are the main topics of this article?"
- "Which words appear most often in this passage?"
- "Give me the top 10 keywords."

Do NOT use this skill for Chinese text. The tool only considers English
letters (a–z, A–Z), so the result will be empty for Chinese-only input.

## Tool call

Call the `extract_keywords` MCP tool on the `text-processor` server with:

- `text` (string, required): the English text, 1–50,000 characters.
- `count` (integer, optional, default 5): number of keywords to return,
  from 1 to 20.

The server returns a JSON object shaped like:

```json
{
  "keywords": [
    {"word": "machine", "frequency": 3},
    {"word": "learning", "frequency": 2}
  ]
}
```

## How to present the result

1. Parse the JSON and list words with their frequencies.
2. If the user asked for topics, briefly summarize what the top words
   suggest about the text.
3. Mention the limitation: this is frequency-based, not semantic, and
   English-only.

## Example user requests

- "请提取下面这段英文文本的关键词。"
- "Top 5 keywords from this article."
- "What words repeat the most in this paragraph?"
