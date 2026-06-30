"""
第19天统一模型配置

继续使用项目根目录 .env：

OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash

本目录默认让 AgentWorkflow 使用 ReActAgent，因为 ReAct 对 OpenAI-compatible
中转模型兼容性更稳。如果你确认模型和 API 支持 function calling，可以把
function_calling=True 传给 build_llm。
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from llama_index.llms.openai_like import OpenAILike


def get_env_value(*names: str, default: str | None = None) -> str | None:
    """按顺序读取多个环境变量名，兼容 OPENAI_* 和 DEEPSEEK_*。"""
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def build_llm(function_calling: bool = False) -> Any:
    """
    创建 LlamaIndex 使用的 OpenAI-compatible LLM。

    Args:
        function_calling: 是否把模型声明为支持函数调用。默认 False，
            这样 AgentWorkflow.from_tools_or_functions 会选择 ReActAgent。
    """
    load_dotenv()

    api_key = get_env_value("DEEPSEEK_API_KEY", "OPENAI_API_KEY")
    base_url = get_env_value(
        "DEEPSEEK_BASE_URL",
        "OPENAI_BASE_URL",
        "OPENAI_API_URL",
        default="https://api.deepseek.com",
    )
    model = get_env_value(
        "DEEPSEEK_MODEL",
        "OPENAI_MODEL",
        default="deepseek-v4-flash",
    )

    if not api_key:
        raise RuntimeError("没有读取到 API Key，请检查 .env 中的 OPENAI_API_KEY 或 DEEPSEEK_API_KEY。")

    return OpenAILike(
        model=model,
        api_key=api_key,
        api_base=base_url,
        temperature=0.1,
        is_chat_model=True,
        is_function_calling_model=function_calling,
        context_window=64000,
        max_tokens=1024,
        timeout=60,
    )


if __name__ == "__main__":
    llm = build_llm()
    print("模型配置完成")
    print(f"LLM: {llm.model}")
    print(f"Function calling declared: {llm.metadata.is_function_calling_model}")
