"""
Day13: duckduckgo_agent_example.py

这是课程页中“基于 DuckDuckGo 的基础检索”的真实网页检索版本。

注意：
- 这个脚本需要网络。
- 这个脚本会使用你的真实模型 API。
- DuckDuckGoSearchTool 需要 ddgs 依赖，已写入 requirements.txt。

运行：

python duckduckgo_agent_example.py
"""

from __future__ import annotations

from smolagents import CodeAgent

from model_config import build_model


def main() -> None:
    try:
        from smolagents import DuckDuckGoSearchTool
    except ImportError as exc:
        raise RuntimeError(
            "缺少 DuckDuckGoSearchTool 依赖。请先运行："
            "pip install -r examples/13-smolagents-retrieval-agent-practice/requirements.txt"
        ) from exc

    search_tool = DuckDuckGoSearchTool()

    agent = CodeAgent(
        tools=[search_tool],
        model=build_model(),
        max_steps=6,
    )

    response = agent.run(
        """
请使用 DuckDuckGo 搜索真实网页资料：
luxury superhero-themed party ideas, decorations, entertainment, catering.

请基于搜索结果，用中文总结一份简洁方案，并说明信息来自网页检索。
"""
    )
    print("11111111111111111111")
    print(response)
    print("11111111111111111111")

if __name__ == "__main__":
    main()
