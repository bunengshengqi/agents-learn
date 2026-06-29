"""
Day16: llamahub_install_demo.py

这个脚本不调用模型 API。

它演示如何理解 LlamaHub：
- 安装包名是什么。
- import 路径是什么。
- 当前环境是否已经安装了对应集成。

运行：

python llamahub_install_demo.py
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationInfo:
    """一个 LlamaHub / LlamaIndex 集成的学习信息。"""

    name: str
    package: str
    import_path: str
    object_name: str
    usage: str


INTEGRATIONS = [
    IntegrationInfo(
        name="OpenAI-compatible LLM",
        package="llama-index-llms-openai-like",
        import_path="llama_index.llms.openai_like",
        object_name="OpenAILike",
        usage="接 DeepSeek、996tokens 或其他 OpenAI-compatible Chat API。",
    ),
    IntegrationInfo(
        name="File Reader",
        package="llama-index-readers-file",
        import_path="llama_index.readers.file",
        object_name="FlatReader / PDFReader 等",
        usage="读取本地 txt、md、pdf、docx 等文件。",
    ),
    IntegrationInfo(
        name="Core",
        package="llama-index-core",
        import_path="llama_index.core",
        object_name="VectorStoreIndex / SummaryIndex / Settings",
        usage="LlamaIndex 的核心组件。",
    ),
]


def is_importable(import_path: str) -> bool:
    """检查当前 Python 环境是否能 import 某个集成。"""
    try:
        importlib.import_module(import_path)
    except ImportError:
        return False

    return True


def main() -> None:
    """打印 LlamaHub 集成安装和导入信息。"""
    print("=" * 80)
    print("Day16: LlamaHub 安装 / import 对照表")
    print("=" * 80)

    for item in INTEGRATIONS:
        installed = "已安装" if is_importable(item.import_path) else "未安装"

        print(f"\n名称：{item.name}")
        print(f"用途：{item.usage}")
        print(f"安装：pip install {item.package}")
        print(f"导入：from {item.import_path} import {item.object_name}")
        print(f"当前环境：{installed}")

    print("\n结论：LlamaHub 不是必须 import 的库，而是帮你找到这些集成包和 import 路径的目录。")


if __name__ == "__main__":
    main()
