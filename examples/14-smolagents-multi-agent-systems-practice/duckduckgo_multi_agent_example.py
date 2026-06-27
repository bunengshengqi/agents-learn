"""
Day14: duckduckgo_multi_agent_example.py

这是可选的真实网页检索多智能体版本。

它会使用：
- 你的真实模型 API。
- DuckDuckGoSearchTool 真实网页检索。
- Manager Agent + Web Agent 的多智能体结构。

运行前需要：

pip install -r examples/14-smolagents-multi-agent-systems-practice/requirements.txt

运行：

python duckduckgo_multi_agent_example.py
"""

from __future__ import annotations

from smolagents import CodeAgent

from model_config import build_model
from tools import get_manager_tools


def build_web_agent() -> CodeAgent:
    """创建真实网页搜索子 Agent。"""
    try:
        from smolagents import DuckDuckGoSearchTool
    except ImportError as exc:
        raise RuntimeError(
            "缺少 DuckDuckGoSearchTool 依赖。请先运行："
            "pip install -r examples/14-smolagents-multi-agent-systems-practice/requirements.txt"
        ) from exc

    return CodeAgent(
        name="web_agent",
        description="负责使用 DuckDuckGo 搜索真实网页信息，并返回简洁摘要和来源。",
        tools=[DuckDuckGoSearchTool()],
        model=build_model(),
        max_steps=6,
    )


def build_manager_agent() -> CodeAgent:
    """创建管理真实 Web Agent 的 Manager Agent。"""
    web_agent = build_web_agent()

    return CodeAgent(
        name="manager_agent",
        description="负责委派网页搜索任务、调用计算工具，并整合最终答案。",
        tools=get_manager_tools(),
        managed_agents=[web_agent],
        model=build_model(),
        max_steps=10,
        additional_authorized_imports=["math"],
    )


def main() -> None:
    manager_agent = build_manager_agent()

    print("=" * 80)
    print("真实网页检索多智能体团队结构")
    print("=" * 80)
    manager_agent.visualize()

    task = """
请作为 Manager Agent 完成任务：
1. 委派 web_agent 搜索 Nolan Batman filming locations，并找出一个常见拍摄城市。
2. 使用 calculate_cargo_travel_time 估算该城市到 Sydney 的货运飞行时间。
3. 最后用中文回答，并说明哪些信息来自 web_agent，哪些结果来自计算工具。

如果 web_agent 没有给出精确坐标，请使用你已知的常见城市坐标进行估算，并明确说明这是估算。
"""

    response = manager_agent.run(task)

    print("\nFinal Answer:")
    print(response)


if __name__ == "__main__":
    main()

