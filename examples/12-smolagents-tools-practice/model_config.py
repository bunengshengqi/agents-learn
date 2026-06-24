"""
Day12: model_config.py

这个文件专门负责模型配置。
Day12 的重点是工具系统，模型配置继续沿用 OpenAI-compatible 接口。
"""

from __future__ import annotations  # 允许在类型注解中延迟解析类型，减少前向引用问题。

import os  # 用来读取环境变量。
from typing import Any  # 用 Any 表示不同 smolagents 版本可能返回的模型对象类型。

from dotenv import load_dotenv  # 用来加载项目根目录中的 .env 配置。
from smolagents import OpenAIServerModel  # OpenAI-compatible 模型封装。
from smolagents.models import REMOVE_PARAMETER  # 用来从请求参数中移除某些不兼容字段。


def _require_env(name: str) -> str:
    """读取必填环境变量，并给出适合学习项目的错误提示。"""
    value = os.getenv(name)  # 按环境变量名称读取配置值。

    if not value:  # 如果没有读到值，说明用户还没配置好 .env。
        raise RuntimeError(f"缺少 {name}。请先在项目根目录的 .env 中配置 {name}。")  # 给出明确报错。

    return value  # 返回已经确认存在的环境变量值。


def build_model() -> Any:
    """
    创建 smolagents 使用的模型对象。

    这里保留 Day11 的兼容处理：删除 tool_choice 参数，避免部分
    OpenAI-compatible 中转模型在 thinking mode 下拒绝该参数。
    """
    load_dotenv()  # 加载 .env 文件，让 os.getenv 可以读到里面的配置。

    api_key = _require_env("OPENAI_API_KEY")  # 读取必填 API Key。
    model_id = _require_env("OPENAI_MODEL")  # 读取必填模型名称。
    base_url = os.getenv("OPENAI_BASE_URL")  # 读取可选的 OpenAI-compatible 中转地址。

    model_kwargs: dict[str, Any] = {  # 统一收集创建模型对象所需的参数。
        "model_id": model_id,  # 告诉 smolagents 使用哪个模型。
        "api_key": api_key,  # 传入 API Key。
        "client_kwargs": {"timeout": 60.0},  # 设置请求超时时间，避免一直卡住。
        "temperature": 0.1,  # 降低随机性，让练习输出更稳定。
        "tool_choice": REMOVE_PARAMETER,  # 删除部分中转模型不支持的 tool_choice 参数。
    }  # 模型参数字典结束。

    if base_url:  # 如果用户配置了中转地址，就使用它。
        model_kwargs["api_base"] = base_url  # smolagents 的 OpenAIServerModel 使用 api_base 表示接口地址。

    return OpenAIServerModel(**model_kwargs)  # 创建并返回模型对象。
