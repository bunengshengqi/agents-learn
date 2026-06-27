"""
Day14: tools.py

这个文件放 Day14 多智能体系统会用到的工具。

重点：
- 子 Agent 可以有自己的工具。
- Manager Agent 也可以有自己的工具。
- Manager 还能把任务委派给 managed_agents。
"""

from __future__ import annotations

import math
from typing import Optional, Tuple

from smolagents import tool


@tool
def search_filming_locations(topic: str) -> str:
    """
    查询模拟影视拍摄地点资料。

    Args:
        topic: 查询主题，比如 Batman、Dark Knight、filming locations。
    """
    topic_lower = topic.lower()

    if "batman" in topic_lower or "dark knight" in topic_lower:
        return """
检索到的拍摄地点资料：
1. Chicago, USA：常被用于 Nolan 版 Batman / The Dark Knight 系列中的 Gotham 城市场景。
2. London, UK：部分 Batman 相关电影使用英国摄影棚和城市素材。
3. Hong Kong, China：The Dark Knight 中出现过香港高楼动作场景。
4. Pittsburgh, USA：The Dark Knight Rises 曾使用 Pittsburgh 拍摄 Gotham 相关场景。
"""

    return "没有找到相关影视拍摄地点资料。"


@tool
def get_city_coordinates(city: str) -> Tuple[float, float]:
    """
    查询城市坐标。

    Args:
        city: 城市名称，比如 Chicago、Sydney、London、Hong Kong、Pittsburgh。
    """
    coordinates = {
        "Chicago": (41.8781, -87.6298),
        "Sydney": (-33.8688, 151.2093),
        "London": (51.5074, -0.1278),
        "Hong Kong": (22.3193, 114.1694),
        "Pittsburgh": (40.4406, -79.9959),
    }
    return coordinates.get(city, (0.0, 0.0))


@tool
def calculate_cargo_travel_time(
    origin_coords: Tuple[float, float],
    destination_coords: Tuple[float, float],
    cruising_speed_kmh: Optional[float] = 750.0,
) -> float:
    """
    计算货运飞机在地球两点之间的预估飞行时间。

    Args:
        origin_coords: 起点坐标，格式为 (latitude, longitude)。
        destination_coords: 终点坐标，格式为 (latitude, longitude)。
        cruising_speed_kmh: 巡航速度，单位 km/h，默认 750。
    """

    def to_radians(degrees: float) -> float:
        return degrees * (math.pi / 180)

    lat1, lon1 = map(to_radians, origin_coords)
    lat2, lon2 = map(to_radians, destination_coords)

    earth_radius_km = 6371.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.asin(math.sqrt(a))
    distance = earth_radius_km * c

    actual_distance = distance * 1.1
    flight_time = (actual_distance / cruising_speed_kmh) + 1.0

    return round(flight_time, 2)


def get_research_tools() -> list:
    """返回研究员子 Agent 使用的工具。"""
    return [
        search_filming_locations,
        get_city_coordinates,
    ]


def get_manager_tools() -> list:
    """返回 Manager Agent 使用的工具。"""
    return [
        calculate_cargo_travel_time,
    ]

