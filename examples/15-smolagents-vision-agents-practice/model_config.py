"""
Day15: model_config.py

这个文件专门负责模型配置。

Day15 的练习重点是视觉智能体，但你当前使用 DeepSeek API，而不是 GPT-4o。
所以这里继续使用 OpenAI-compatible 的文本/推理模型配置，让 DeepSeek 负责：
- 任务理解
- 工具调用
- 观察结果总结
- 最终推理
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

    注意：
    - 这里的模型是 DeepSeek / OpenAI-compatible 文本模型。
    - 它负责读工具返回的文字 observation。
    - 它不被假设为可以直接读取图片。
    - 删除 tool_choice 参数，是为了兼容部分 DeepSeek / 中转 API 的限制。
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

