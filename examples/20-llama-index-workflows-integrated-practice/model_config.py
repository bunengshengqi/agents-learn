"""
Shared OpenAI-compatible model config for Day20 integrated practice.

The scripts read the project root .env:

OPENAI_API_KEY=your key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
"""

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from llama_index.llms.openai_like import OpenAILike


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_env_value(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def build_llm(max_tokens: int = 1024, temperature: float = 0.1, function_calling: bool = False) -> Any:
    load_dotenv(PROJECT_ROOT / ".env")
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
        raise RuntimeError("没有读取到 API Key，请检查项目根目录 .env。")

    return OpenAILike(
        model=model,
        api_key=api_key,
        api_base=base_url,
        temperature=temperature,
        is_chat_model=True,
        is_function_calling_model=function_calling,
        context_window=64000,
        max_tokens=max_tokens,
        timeout=60,
    )
