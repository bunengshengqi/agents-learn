"""
Day16: component_flow_demo.py

不调用任何模型 API，只用打印流程帮助理解：
- LlamaIndex 组件是什么。
- LlamaHub 扮演什么角色。
- 一次 RAG 查询大概经过哪些步骤。

运行：

python component_flow_demo.py
"""

from __future__ import annotations


COMPONENTS = [
    ("Reader / Loader", "读取本地文件、网页、数据库、Notion、Obsidian 等数据"),
    ("Document", "LlamaIndex 内部表示的一份文档或文档片段"),
    ("Index", "把文档组织成方便查询的结构"),
    ("Retriever", "根据用户问题找出相关文档片段"),
    ("Query Engine", "把检索和 LLM 回答封装成一个查询接口"),
    ("Tool", "把查询能力包装成 Agent 可以调用的工具"),
    ("Agent", "根据目标决定要不要调用工具、调用哪个工具"),
    ("Workflow", "把复杂任务拆成稳定步骤"),
]


RAG_FLOW = [
    "用户提出问题",
    "Reader 读取 data/ 目录里的资料",
    "Index 建立索引",
    "Retriever 找出和问题相关的资料片段",
    "Query Engine 把资料片段交给 LLM",
    "LLM 基于资料生成答案",
]


LLAMAHUB_EXAMPLES = [
    ("llama-index-llms-openai-like", "OpenAI-compatible LLM，例如 DeepSeek 或 996tokens"),
    ("llama-index-readers-file", "读取本地文件"),
    ("llama-index-vector-stores-chroma", "接入 Chroma 向量数据库"),
    ("llama-index-embeddings-huggingface", "接入 Hugging Face embedding 模型"),
]


def print_section(title: str) -> None:
    """打印分隔标题。"""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def show_components() -> None:
    """展示 LlamaIndex 组件。"""
    print_section("一、LlamaIndex 组件")

    for name, description in COMPONENTS:
        print(f"- {name}: {description}")


def show_rag_flow() -> None:
    """展示 RAG 查询流程。"""
    print_section("二、一次 LlamaIndex RAG 查询流程")

    for index, step in enumerate(RAG_FLOW, start=1):
        print(f"{index}. {step}")


def show_llamahub_role() -> None:
    """展示 LlamaHub 的作用。"""
    print_section("三、LlamaHub 像插件目录")

    print("你需要什么能力，就安装对应的 LlamaIndex 集成包：\n")

    for package, usage in LLAMAHUB_EXAMPLES:
        print(f"- pip install {package}")
        print(f"  用途：{usage}")


def main() -> None:
    """运行 Day16 无 API 概念演示。"""
    show_components()
    show_rag_flow()
    show_llamahub_role()

    print_section("今日核心结论")
    print("LlamaIndex = 让大模型使用你的数据。")
    print("LlamaHub = LlamaIndex 的插件和集成目录。")


if __name__ == "__main__":
    main()
