"""Day27 LlamaIndex-style tool implementation."""

from __future__ import annotations

try:
    from llama_index.core.tools import FunctionTool
except ImportError:

    class FunctionTool:
        """Small fallback that mimics FunctionTool.from_defaults."""

        def __init__(self, fn):
            self.fn = fn

        @classmethod
        def from_defaults(cls, fn):
            return cls(fn)

        def call(self, *args, **kwargs):
            return self.fn(*args, **kwargs)


from common_tools import (
    alfred_answer_from_observations,
    choose_tools,
    offline_hub_stats,
    offline_weather_info,
    offline_web_search,
)


def search_web(query: str) -> str:
    """LlamaIndex-style search function."""
    return offline_web_search(query)


def get_weather_info(location: str) -> str:
    """LlamaIndex-style weather function."""
    return offline_weather_info(location)


def get_hub_stats(author: str) -> str:
    """LlamaIndex-style Hub statistics function."""
    return offline_hub_stats(author)


def call_tool(tool, *args, **kwargs) -> str:
    """Call a real or fallback LlamaIndex FunctionTool."""
    result = tool.call(*args, **kwargs)
    raw_output = getattr(result, "raw_output", None)

    if raw_output is not None:
        return str(raw_output)

    return str(result)


def run_llama_index_style_alfred(question: str) -> str:
    """Run an offline Alfred flow using LlamaIndex-style tools."""
    search_tool = FunctionTool.from_defaults(search_web)
    weather_tool = FunctionTool.from_defaults(get_weather_info)
    hub_tool = FunctionTool.from_defaults(get_hub_stats)
    selected_tools = choose_tools(question)
    observations: list[str] = []

    if "search" in selected_tools:
        observations.append(call_tool(search_tool, question))

    if "weather" in selected_tools:
        observations.append(call_tool(weather_tool, "Wayne Manor"))

    if "hub_stats" in selected_tools:
        observations.append(call_tool(hub_tool, "facebook"))

    return alfred_answer_from_observations(question, observations)


if __name__ == "__main__":
    question = "Is the weather good for fireworks, and what is Facebook's popular model?"
    print(run_llama_index_style_alfred(question))
