"""
Day13: model_config.py

这个文件专门负责模型配置。
Day13 的重点是检索智能体和 Agentic RAG，模型配置继续沿用 OpenAI-compatible 接口。
"""

from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from smolagents import OpenAIServerModel
from smolagents.models import REMOVE_PARAMETER


def _require_env(name: str) -> str:
    """读取必填环境变量，并给出适合学习项目的错误提示。"""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"缺少 {name}。请先在项目根目录的 .env 中配置 {name}。")

    return value


def build_model() -> Any:
    """
    创建 smolagents 使用的模型对象。

    这里保留 Day11/Day12 的兼容处理：删除 tool_choice 参数，避免部分
    OpenAI-compatible 中转模型在 thinking mode 下拒绝该参数。
    """
    load_dotenv()

    api_key = _require_env("OPENAI_API_KEY")
    model_id = _require_env("OPENAI_MODEL")
    base_url = os.getenv("OPENAI_BASE_URL")

    model_kwargs: dict[str, Any] = {
        "model_id": model_id,
        "api_key": api_key,
        "client_kwargs": {"timeout": 60.0},
        "temperature": 0.1,
        "tool_choice": REMOVE_PARAMETER,
    }

    if base_url:
        model_kwargs["api_base"] = base_url

    return OpenAIServerModel(**model_kwargs)

