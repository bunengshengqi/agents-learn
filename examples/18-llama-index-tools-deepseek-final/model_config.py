"""
第18天统一模型配置

重点：
1. DeepSeek / OpenAI-compatible API 使用 OpenAILike。
2. 不使用 llama_index.llms.openai.OpenAI，避免 Unknown model 报错。
3. Agent 调用工具时，需要声明 is_function_calling_model=True。
"""

import os
from dotenv import load_dotenv

from llama_index.core import Settings
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def get_env_value(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def init_models() -> None:
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
        raise ValueError(
            "没有读取到 API Key，请检查 .env 中的 OPENAI_API_KEY 或 DEEPSEEK_API_KEY。"
        )

    Settings.llm = OpenAILike(
        model=model,
        api_key=api_key,
        api_base=base_url,
        temperature=0.2,
        is_chat_model=True,
        is_function_calling_model=True,
        context_window=64000,
        max_tokens=2048,
    )

    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-zh-v1.5"
    )


if __name__ == "__main__":
    init_models()
    print("模型配置完成")
    print("LLM: DeepSeek / OpenAI-compatible API via OpenAILike")
    print("Embedding: BAAI/bge-small-zh-v1.5")
