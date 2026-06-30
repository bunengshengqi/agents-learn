"""
第17天：统一模型配置

修正版重点：
1. DeepSeek 使用 OpenAILike，而不是 OpenAI。
2. OpenAI 适配器会校验官方 OpenAI 模型名，所以不认识 deepseek-v4-flash。
3. OpenAILike 专门用于 DeepSeek、Qwen、Moonshot 等 OpenAI-compatible API。
4. 手动设置 context_window，避免 Unknown model 报错。
"""

import os
from dotenv import load_dotenv

from llama_index.core import Settings
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.huggingface import HuggingFaceEmbedding


def get_env_value(*names: str, default: str | None = None) -> str | None:
    """兼容多种 .env 写法。"""
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def init_models() -> None:
    """初始化 LlamaIndex 全局模型配置。"""
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
            "没有读取到 API Key。请检查 .env 中是否配置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY。"
        )

    # 关键修复：DeepSeek 走 OpenAI-compatible API，用 OpenAILike。
    Settings.llm = OpenAILike(
        model=model,
        api_key=api_key,
        api_base=base_url,
        temperature=0.2,
        is_chat_model=True,
        context_window=64000,
        max_tokens=2048,
    )

    # 本地中文 Embedding 模型。第一次运行会下载，后续使用本地缓存。
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-zh-v1.5"
    )


if __name__ == "__main__":
    init_models()
    print("模型配置完成")
    print("DeepSeek 已通过 OpenAILike 接入")
    print(f"LLM: {Settings.llm}")
    print(f"Embedding: {Settings.embed_model}")
