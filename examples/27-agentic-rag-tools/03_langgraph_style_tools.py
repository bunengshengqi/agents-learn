"""Day27 LangGraph-style tool implementation."""

from __future__ import annotations

from dataclasses import dataclass

try:
    from langchain_core.tools import Tool
except ImportError:

    @dataclass
    class Tool:
        """Small fallback that mimics langchain_core.tools.Tool."""

        name: str
        func: object
        description: str

        def invoke(self, arg: str) -> str:
            return self.func(arg)


from common_tools import (
    alfred_answer_from_observations,
    choose_tools,
    offline_hub_stats,
    offline_weather_info,
    offline_web_search,
)


def build_langgraph_style_tools() -> dict[str, Tool]:
    """Build LangGraph/LangChain-style Tool objects."""
    return {
        "search": Tool(
            name="web_search",
            func=offline_web_search,
            description="Searches the web for current or general information.",
        ),
        "weather": Tool(
            name="get_weather_info",
            func=offline_weather_info,
            description="Fetches weather information for a given location.",
        ),
        "hub_stats": Tool(
            name="get_hub_stats",
            func=offline_hub_stats,
            description="Fetches the most downloaded model from a Hub author.",
        ),
    }


def run_langgraph_style_alfred(question: str) -> str:
    """Run an offline LangGraph-style tool routing loop."""
    tools = build_langgraph_style_tools()
    selected_tools = choose_tools(question)
    observations: list[str] = []

    if "search" in selected_tools:
        observations.append(tools["search"].invoke(question))

    if "weather" in selected_tools:
        observations.append(tools["weather"].invoke("Wayne Manor"))

    if "hub_stats" in selected_tools:
        observations.append(tools["hub_stats"].invoke("facebook"))

    return alfred_answer_from_observations(question, observations)


def explain_real_langgraph_shape() -> str:
    """Return the real LangGraph shape that this offline script mirrors."""
    return (
        "Real LangGraph shape: START -> assistant -> tools_condition -> "
        "ToolNode(tools) -> assistant -> END."
    )


if __name__ == "__main__":
    question = "Who is Facebook and what's their most popular model?"
    print(explain_real_langgraph_shape())
    print(run_langgraph_style_alfred(question))
