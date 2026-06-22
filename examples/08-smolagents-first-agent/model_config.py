"""
OpenAI-compatible model configuration for Day 8 smolagents examples.

This module intentionally does not depend on a Hugging Face token. It reads
OpenAI-compatible settings from environment variables and builds a smolagents
model object with OpenAIModel.
"""

import os
from typing import Any

from dotenv import load_dotenv


load_dotenv()


def get_required_env(name: str) -> str:
    """Read a required environment variable and raise a clear error if missing."""
    value = os.getenv(name)

    if not value:
        raise ValueError(f"缺少环境变量：{name}。请先在项目根目录创建 .env 文件。")

    return value


def build_model() -> Any:
    """
    Build a smolagents model from OpenAI-compatible environment variables.

    Newer smolagents versions provide OpenAIModel. Older versions may still use
    OpenAIServerModel, so this keeps a small compatibility fallback for learners.
    """
    api_key = get_required_env("OPENAI_API_KEY")
    api_base = get_required_env("OPENAI_BASE_URL")
    model_id = get_required_env("OPENAI_MODEL")

    try:
        from smolagents import OpenAIModel

        return OpenAIModel(
            model_id=model_id,
            api_base=api_base,
            api_key=api_key,
            temperature=0.1,
            max_tokens=1024,
        )
    except ImportError:
        from smolagents import OpenAIServerModel

        return OpenAIServerModel(
            model_id=model_id,
            api_base=api_base,
            api_key=api_key,
            temperature=0.1,
            max_tokens=1024,
        )


def main() -> None:
    """Print a safe configuration summary without leaking the API key."""
    model_id = get_required_env("OPENAI_MODEL")
    api_base = get_required_env("OPENAI_BASE_URL")
    api_key = get_required_env("OPENAI_API_KEY")

    print("配置检查通过：")
    print(f"OPENAI_MODEL={model_id}")
    print(f"OPENAI_BASE_URL={api_base}")
    print(f"OPENAI_API_KEY={'*' * min(len(api_key), 8)}")


if __name__ == "__main__":
    main()
