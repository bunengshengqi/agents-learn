"""Part 2/3：Gradio Web UI + 远程 Streamable HTTP MCP Server。"""

from __future__ import annotations

import gradio as gr

import text_tools


def _run_safely(function, *args):
    """把业务层 ValueError 转换为网页和 MCP 都容易理解的 Gradio 错误。"""
    try:
        return function(*args)
    except ValueError as error:
        raise gr.Error(str(error)) from error


def analyze_text(text: str) -> str:
    """Analyze text and return statistics as JSON.

    Args:
        text: The text to analyze, from 1 to 50,000 characters.

    Returns:
        A JSON string with character, word, sentence, and line statistics.
    """
    return _run_safely(text_tools.analyze_text, text)


def extract_keywords(text: str, count: int = 5) -> str:
    """Extract frequent English keywords from text.

    Args:
        text: The English text from which to extract keywords.
        count: The number of keywords to return, from 1 to 20.

    Returns:
        A JSON string containing keywords and their frequencies.
    """
    return _run_safely(text_tools.extract_keywords, text, count)


def check_reading_level(text: str) -> str:
    """Estimate the reading difficulty of English text.

    Args:
        text: The English passage to evaluate.

    Returns:
        A JSON string with an approximate grade and plain-language level.
    """
    return _run_safely(text_tools.check_reading_level, text)


def check_writing_basics(text: str) -> str:
    """Check a few deterministic English writing rules.

    Args:
        text: The English text to check.

    Returns:
        A JSON string with repeated-space, long-sentence, and punctuation warnings.
    """
    return _run_safely(text_tools.check_writing_basics, text)


def summarize_text(text: str, max_sentences: int = 2) -> str:
    """Create a deterministic extractive summary.

    Args:
        text: The text to summarize.
        max_sentences: The maximum number of leading sentences to keep, from 1 to 5.

    Returns:
        A JSON string with the selected leading sentences and metadata.
    """
    return _run_safely(text_tools.summarize_text, text, max_sentences)


def reverse_text(text: str) -> str:
    """Reverse all characters in text. This tool has no web widget.

    Args:
        text: The text whose character order should be reversed.

    Returns:
        The text in reverse character order.
    """
    return _run_safely(text_tools.reverse_text, text)


with gr.Blocks(title="Day 43 · Text Processor MCP") as demo:
    # 没有网页组件的 API/MCP Tool，必须在 Blocks 上下文里注册。
    gr.api(reverse_text, api_name="reverse_text", queue=False)

    gr.Markdown(
        """
        # Day 43：Text Processor MCP

        同一套业务逻辑提供网页和 MCP 两种入口。阅读难度、关键词和写作检查主要面向英文，
        摘要是可复现的首句抽取，不会调用大模型。
        """
    )

    with gr.Tab("文本统计"):
        analyze_input = gr.Textbox(label="输入文本", lines=8)
        analyze_output = gr.Code(label="统计结果", language="json")
        gr.Button("分析", variant="primary").click(
            analyze_text,
            analyze_input,
            analyze_output,
            api_name="analyze_text",
            queue=False,
        )

    with gr.Tab("英文关键词"):
        keywords_input = gr.Textbox(label="输入英文文本", lines=8)
        keyword_count = gr.Slider(1, 20, value=5, step=1, label="关键词数量")
        keywords_output = gr.Code(label="关键词", language="json")
        gr.Button("提取").click(
            extract_keywords,
            [keywords_input, keyword_count],
            keywords_output,
            api_name="extract_keywords",
            queue=False,
        )

    with gr.Tab("英文阅读难度"):
        reading_input = gr.Textbox(label="输入英文段落", lines=8)
        reading_output = gr.Code(label="难度估算", language="json")
        gr.Button("估算").click(
            check_reading_level,
            reading_input,
            reading_output,
            api_name="check_reading_level",
            queue=False,
        )

    with gr.Tab("基础写作检查"):
        writing_input = gr.Textbox(label="输入英文文本", lines=8)
        writing_output = gr.Code(label="规则检查", language="json")
        gr.Button("检查").click(
            check_writing_basics,
            writing_input,
            writing_output,
            api_name="check_writing_basics",
            queue=False,
        )

    with gr.Tab("抽取式摘要"):
        summary_input = gr.Textbox(label="输入文本", lines=8)
        sentence_count = gr.Slider(1, 5, value=2, step=1, label="保留句数")
        summary_output = gr.Code(label="摘要", language="json")
        gr.Button("生成摘要").click(
            summarize_text,
            [summary_input, sentence_count],
            summary_output,
            api_name="summarize_text",
            queue=False,
        )

    gr.Markdown(
        "`reverse_text` 只注册为 API/MCP Tool，不占用网页标签页。"
    )


if __name__ == "__main__":
    demo.launch(mcp_server=True, server_name="0.0.0.0")
