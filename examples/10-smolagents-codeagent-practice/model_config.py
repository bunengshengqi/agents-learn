"""
Day10: model_config.py

这个文件专门负责模型配置。

你需要提前配置环境变量：

export OPENAI_API_KEY="你的 API Key"
export OPENAI_BASE_URL="你的 base_url，可选"
export OPENAI_MODEL="你的模型名称"

如果使用 OpenAI 官方，OPENAI_BASE_URL 可以不配置。
如果使用中转站，一般需要配置 OPENAI_BASE_URL。
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from smolagents import OpenAIServerModel


def _require_env(name: str) -> str:
    """读取必填环境变量，并给出适合学习项目的错误提示。"""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"缺少 {name}。请先在项目根目录的 .env 中配置 {name}。")

    return value


def build_model() -> OpenAIServerModel:
    """
    创建 smolagents 使用的模型对象。

    OpenAIServerModel 直接使用 OpenAI-compatible 接口，适合本项目一直使用的
    OPENAI_API_KEY / OPENAI_BASE_URL / OPENAI_MODEL 配置方式。
    """
    load_dotenv()

    api_key = _require_env("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model_id = _require_env("OPENAI_MODEL")

    model_kwargs = {
        "model_id": model_id,
        "api_key": api_key,
        "client_kwargs": {"timeout": 60.0},
        "temperature": 0.1,
    }

    if base_url:
        model_kwargs["api_base"] = base_url

    return OpenAIServerModel(**model_kwargs)

