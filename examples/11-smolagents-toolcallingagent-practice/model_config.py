"""
Day11: model_config.py

这个文件专门负责模型配置，让 Agent 代码不用关心 API Key 和模型地址。

必填环境变量：

OPENAI_API_KEY=your_api_key
OPENAI_MODEL=your_model_name

可选环境变量：

OPENAI_BASE_URL=https://your-openai-compatible-endpoint/v1
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
    创建 ToolCallingAgent 使用的模型对象。

    ToolCallingAgent 依赖模型服务商的原生工具调用能力，所以这里配置的
    模型最好支持 tool/function calling。
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
        # 部分 OpenAI-compatible 中转模型在 thinking mode 下不支持 tool_choice。
        # 删除这个参数后，仍会传 tools schema，让模型自动决定是否调用工具。
        "tool_choice": REMOVE_PARAMETER,
    }

    if base_url:
        model_kwargs["api_base"] = base_url

    return OpenAIServerModel(**model_kwargs)
