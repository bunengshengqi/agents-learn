"""可选：同一个 Python 函数同时提供 Web UI 和 MCP Tool。

安装：pip install "gradio[mcp]"
运行：python gradio_app.py
Web UI：http://127.0.0.1:7860
MCP endpoint：http://127.0.0.1:7860/gradio_api/mcp/
"""

import gradio as gr


def letter_counter(text: str, letter: str) -> int:
    """Count how often one letter appears in text.

    Args:
        text: The input text.
        letter: The letter to count.
    """

    if len(letter) != 1:
        raise gr.Error("Please enter exactly one letter.")
    return text.lower().count(letter.lower())


with gr.Blocks() as demo:
    gr.Markdown("# Day40：Gradio + MCP")
    text_input = gr.Textbox(label="输入文本")
    letter_input = gr.Textbox(label="要统计的单个字母")
    count_output = gr.Number(label="出现次数")
    gr.Button("统计").click(
        letter_counter,
        inputs=[text_input, letter_input],
        outputs=count_output,
    )


if __name__ == "__main__":
    demo.launch(mcp_server=True)
