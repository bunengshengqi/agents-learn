"""Day 42：同一套 Python 函数，同时提供 Gradio Web UI 与 MCP Server。"""

from __future__ import annotations

import json
import re
from collections import Counter

import gradio as gr


MAX_TEXT_LENGTH = 20_000


def _validate_text(text: str) -> str:
    """验证文本并返回去除首尾空白后的内容。"""
    cleaned = text.strip()
    if not cleaned:
        raise gr.Error("请输入非空文本。")
    if len(cleaned) > MAX_TEXT_LENGTH:
        raise gr.Error(f"文本不能超过 {MAX_TEXT_LENGTH} 个字符。")
    return cleaned


def analyze_text(text: str) -> str:
    """Analyze text and return basic statistics as JSON.

    Args:
        text: The text to analyze. It must contain 1 to 20,000 characters.

    Returns:
        A JSON string containing characters, words, lines, and average word length.
    """
    cleaned = _validate_text(text)
    words = re.findall(r"\b\w+\b", cleaned, flags=re.UNICODE)
    result = {
        "characters": len(cleaned),
        "words": len(words),
        "lines": len(cleaned.splitlines()),
        "average_word_length": (
            round(sum(len(word) for word in words) / len(words), 2) if words else 0
        ),
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


def reverse_text(text: str) -> str:
    """Reverse the order of all characters in text.

    Args:
        text: The text whose character order should be reversed.

    Returns:
        The text with all characters in reverse order.
    """
    return _validate_text(text)[::-1]


def count_vowels(text: str) -> int:
    """Count English vowels in text.

    Args:
        text: The text in which to count a, e, i, o, and u.

    Returns:
        The total number of English vowels, ignoring letter case.
    """
    cleaned = _validate_text(text)
    return sum(character in "aeiouAEIOU" for character in cleaned)


def extract_keywords(text: str, limit: int = 5) -> list[str]:
    """Extract frequent English keywords from text. This tool has no web widget.

    Args:
        text: The English text from which to extract keywords.
        limit: The maximum number of keywords to return, from 1 to 20.

    Returns:
        A list of lowercase keywords ordered by frequency.
    """
    cleaned = _validate_text(text)
    if not 1 <= limit <= 20:
        raise gr.Error("limit 必须在 1 到 20 之间。")

    stop_words = {"a", "an", "and", "are", "for", "in", "is", "of", "the", "to"}
    words = re.findall(r"[A-Za-z][A-Za-z'-]+", cleaned.lower())
    counts = Counter(word for word in words if word not in stop_words)
    return [word for word, _ in counts.most_common(limit)]


@gr.mcp.resource("course://day42/guide", mime_type="text/markdown")
def course_guide() -> str:
    """Return a read-only guide for the Day 42 Gradio MCP application."""
    return """# Day 42 Gradio MCP

- Humans use the Gradio web page.
- Agents connect to `/gradio_api/mcp/`.
- UI event functions become MCP tools.
- `extract_keywords` is an MCP/API-only tool created with `@gr.api()`.
"""


@gr.mcp.prompt()
def explain_text_analysis(audience: str = "beginner") -> str:
    """Create a reusable prompt for explaining text-analysis results."""
    return (
        f"Explain the text-analysis JSON to a {audience}. "
        "Define every field, avoid jargon, and give one concrete example."
    )


with gr.Blocks(title="Day 42 · Gradio MCP Text Toolkit") as demo:
    # gr.api() 必须在当前 Gradio 版本的 Blocks 上下文中注册。
    gr.api(extract_keywords, api_name="extract_keywords", queue=False)
    # Resource/Prompt 装饰器提供 MCP 元数据；gr.api() 把函数挂载进这个应用。
    gr.api(course_guide, api_name="course_guide", queue=False)
    gr.api(
        explain_text_analysis,
        api_name="explain_text_analysis",
        queue=False,
    )

    gr.Markdown(
        """
        # Day 42：Gradio Web UI + MCP Server

        人可以点击下面的网页控件；Agent 可以连接同一应用的
        `/gradio_api/mcp/` endpoint 调用相同能力。
        """
    )

    with gr.Tab("文本统计"):
        analyze_input = gr.Textbox(label="输入文本", lines=7)
        analyze_output = gr.Code(label="统计结果", language="json")
        analyze_button = gr.Button("开始统计", variant="primary")
        analyze_button.click(
            analyze_text,
            inputs=analyze_input,
            outputs=analyze_output,
            api_name="analyze_text",
            api_description="Analyze text and return basic statistics as JSON.",
            queue=False,
        )

    with gr.Tab("反转文本"):
        reverse_input = gr.Textbox(label="输入文本", lines=5)
        reverse_output = gr.Textbox(label="反转结果", lines=5)
        reverse_button = gr.Button("反转")
        reverse_button.click(
            reverse_text,
            inputs=reverse_input,
            outputs=reverse_output,
            api_name="reverse_text",
            queue=False,
        )

    with gr.Tab("统计英文元音"):
        vowel_input = gr.Textbox(label="输入英文文本", lines=5)
        vowel_output = gr.Number(label="a/e/i/o/u 总数", precision=0)
        vowel_button = gr.Button("统计")
        vowel_button.click(
            count_vowels,
            inputs=vowel_input,
            outputs=vowel_output,
            api_name="count_vowels",
            queue=False,
        )

    gr.Markdown(
        """
        `extract_keywords` 没有网页控件，它由 `@gr.api()` 注册，供 API/MCP Client 使用。
        页面底部 **Use via API or MCP** 可以查看自动生成的 Schema 和连接配置。
        """
    )


if __name__ == "__main__":
    demo.launch(mcp_server=True, server_name="0.0.0.0")
