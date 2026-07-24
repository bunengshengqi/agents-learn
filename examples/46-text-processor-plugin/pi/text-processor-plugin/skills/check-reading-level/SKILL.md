---
name: check-reading-level
description: |
  Use this skill when the user wants to estimate how difficult an English
  passage is to read. The tool computes a Flesch-Kincaid grade level and
  maps it to a plain-language category (Elementary / Middle / High School
  / College). It is a rough English heuristic.
---

# check-reading-level

When the user asks "how hard is this text to read?", "what grade level is
this article written for?", or wants a rough readability estimate, call
the MCP tool `check_reading_level` from the `text-processor` server.

## When to use

Trigger this skill when the user wants any of the following:

- "这段英文阅读难度如何？"
- "What reading level is this passage written at?"
- "Is this text suitable for middle school students?"
- "Give me a Flesch-Kincaid grade."

Do NOT use this skill for Chinese text – the tool requires English words
and will raise an error otherwise.

## Tool call

Call the `check_reading_level` MCP tool on the `text-processor` server with:

- `text` (string, required): the English passage to evaluate.

The server returns a JSON object with:

- `grade_level` (Flesch-Kincaid grade, rounded to 1 decimal)
- `reading_level` (human-readable category)
- `words` (total English words)
- `sentences` (sentence count)
- `estimated_syllables`
- `warning` (acknowledging this is a heuristic)

## How to present the result

1. Show the `grade_level` and the `reading_level` category.
2. Briefly explain what the grade means (e.g. "grade 8 ≈ suitable for
   middle school readers").
3. Always pass through the `warning` field so the user knows this is a
   rough heuristic, not a professional assessment.

## Example user requests

- "这段英文阅读难度是什么水平？"
- "What grade level is this article written for?"
- "Is this text easy to read for a teenager?"
