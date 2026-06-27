"""
Day14: manual_orchestration_demo.py

这个脚本不调用大模型。
它用普通 Python 函数模拟“编排”的动作，帮助你先理解多智能体系统的流程。

运行：

python manual_orchestration_demo.py
"""

from __future__ import annotations

from tools import calculate_cargo_travel_time, get_city_coordinates, search_filming_locations


def main() -> None:
    print("=" * 80)
    print("手动模拟多智能体编排")
    print("=" * 80)

    print("\n1. Manager 决定先让 Research Agent 查资料")
    research_result = search_filming_locations("Batman filming locations")
    print(research_result)

    print("\n2. Manager 选择 Chicago 作为出发城市，并查询 Sydney 坐标")
    chicago_coords = get_city_coordinates("Chicago")
    sydney_coords = get_city_coordinates("Sydney")
    print(f"Chicago 坐标：{chicago_coords}")
    print(f"Sydney 坐标：{sydney_coords}")

    print("\n3. Manager 使用自己的工具计算货运飞行时间")
    travel_time = calculate_cargo_travel_time(chicago_coords, sydney_coords)
    print(f"Chicago 到 Sydney 预估货运飞行时间：{travel_time} 小时")

    print("\n4. 这就是编排原则：专业查询交给 Research Agent，确定性计算交给工具，最终答案由 Manager 整合。")


if __name__ == "__main__":
    main()

