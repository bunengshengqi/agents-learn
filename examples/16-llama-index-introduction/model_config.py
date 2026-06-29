"""
Day16: model_config.py

这个文件负责为 LlamaIndex 创建 OpenAI-compatible LLM。

继续沿用项目根目录的 .env：

OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=你的 OpenAI-compatible 地址
OPENAI_MODEL=你的模型名称
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv


def _require_env(name: str) -> str:
    """读取必填环境变量，并给出适合学习项目的错误提示。"""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"缺少 {name}。请先在项目根目录的 .env 中配置 {name}。")

    return value


def build_llm() -> Any:
    """
    创建 LlamaIndex 使用的 OpenAI-compatible LLM。

    这里使用 `llama-index-llms-openai-like`，适合 DeepSeek、996tokens
    或其他兼容 OpenAI Chat Completions 的 API。
    """
    load_dotenv()

    api_key = _require_env("OPENAI_API_KEY")
    model = _require_env("OPENAI_MODEL")
    api_base = os.getenv("OPENAI_BASE_URL")

    if not api_base:
        raise RuntimeError("缺少 OPENAI_BASE_URL。OpenAI-compatible 中转 API 通常需要配置它。")

    from llama_index.llms.openai_like import OpenAILike

    return OpenAILike(
        model=model,
        api_base=api_base,
        api_key=api_key,
        is_chat_model=True,
        is_function_calling_model=False,
        temperature=0.1,
        max_tokens=512,
        timeout=60,
    )
