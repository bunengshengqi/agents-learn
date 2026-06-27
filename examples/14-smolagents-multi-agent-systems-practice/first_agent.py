"""
Day14: first_agent.py

这是第 14 天的多智能体系统主练习。

本文件演示：
1. 创建一个专业子 Agent：research_agent。
2. 创建一个 Manager / Orchestrator Agent：manager_agent。
3. Manager 通过 managed_agents 管理子 Agent。
4. Manager 自己也可以使用工具，比如货运飞行时间计算工具。
5. 使用 manager_agent.visualize() 查看团队结构。

运行：

python first_agent.py
"""

from __future__ import annotations

from smolagents import CodeAgent

from model_config import build_model
from tools import get_manager_tools, get_research_tools


def build_research_agent() -> CodeAgent:
    """
    创建研究员子 Agent。

    这个 Agent 不是总负责人，它只负责查找拍摄地点和城市坐标。
    作为 managed_agent 时，必须设置 name 和 description。
    """
    return CodeAgent(
        name="research_agent",
        description=(
            "负责查询影视拍摄地点和城市坐标。"
            "当任务需要查找 Batman 拍摄城市、城市经纬度或候选地点时调用它。"
        ),
        tools=get_research_tools(),
        model=build_model(),
        max_steps=6,
    )


def build_manager_agent() -> CodeAgent:
    """
    创建 Manager / Orchestrator Agent。

    判断它是编排智能体的关键：
    - 它有 managed_agents。
    - 它负责把任务委派给 research_agent。
    - 它负责使用自己的工具计算飞行时间。
    - 它负责整合最终答案。
    """
    research_agent = build_research_agent()

    return CodeAgent(
        name="manager_agent",
        description="负责任务拆解、子任务委派、结果整合和最终回答的管理智能体。",
        tools=get_manager_tools(),
        managed_agents=[research_agent],
        model=build_model(),
        max_steps=10,
        additional_authorized_imports=["math"],
    )


def show_team_structure(manager_agent: CodeAgent) -> None:
    """
    打印团队结构。

    visualize() 会展示：
    - Manager Agent 的工具。
    - Manager 管理的子 Agent。
    - 子 Agent 的 description 和工具。
    """
    print("=" * 80)
    print("团队结构：manager_agent.visualize()")
    print("=" * 80)
    manager_agent.visualize()


def run_logistics_demo(manager_agent: CodeAgent) -> None:
    """
    运行一个多智能体物流任务。

    这个任务会迫使 Manager：
    1. 委派 research_agent 查询 Batman 相关拍摄城市和坐标。
    2. 自己调用 calculate_cargo_travel_time 计算到 Sydney 的飞行时间。
    3. 综合 research_agent 的结果和计算结果。
    """
    task = """
请完成一个多智能体协作任务：

目标：假设我们要把一批电影道具从 Nolan 版 Batman 常见拍摄城市之一运到 Sydney。

请你：
1. 先把“查找 Batman 常见拍摄城市和城市坐标”的任务委派给 research_agent。
2. 从 research_agent 返回的信息里选择 Chicago 作为出发城市。
3. 使用 calculate_cargo_travel_time 计算 Chicago 到 Sydney 的货运飞行时间。
4. 用中文说明：
   - 哪个 Agent 做了研究任务；
   - Manager 自己调用了哪个工具；
   - 预估货运飞行时间是多少小时；
   - 为什么这个系统属于多智能体系统。
"""

    print("\n" + "=" * 80)
    print("练习：Manager Agent 编排 research_agent + 工具")
    print("=" * 80)

    answer = manager_agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def main() -> None:
    manager_agent = build_manager_agent()

    show_team_structure(manager_agent)
    run_logistics_demo(manager_agent)


if __name__ == "__main__":
    main()

