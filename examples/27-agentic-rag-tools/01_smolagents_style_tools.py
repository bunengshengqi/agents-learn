"""Day27 smolagents-style tool implementation."""

from __future__ import annotations

try:
    from smolagents import Tool
except ImportError:

    class Tool:
        """Small fallback that mimics the part of smolagents.Tool used here."""

        name = "tool"
        description = ""
        inputs = {}
        output_type = "string"

        def __call__(self, *args, **kwargs):
            return self.forward(*args, **kwargs)


from common_tools import (
    alfred_answer_from_observations,
    choose_tools,
    offline_hub_stats,
    offline_weather_info,
    offline_web_search,
)


class SearchTool(Tool):
    """smolagents-style web search tool."""

    name = "web_search"
    description = "Searches the web for current or general information."
    inputs = {"query": {"type": "string", "description": "The search query."}}
    output_type = "string"

    def forward(self, query: str) -> str:
        return offline_web_search(query)


class WeatherInfoTool(Tool):
    """smolagents-style weather tool."""

    name = "weather_info"
    description = "Fetches weather information for a given location."
    inputs = {"location": {"type": "string", "description": "The location to check."}}
    output_type = "string"

    def forward(self, location: str) -> str:
        return offline_weather_info(location)


class HubStatsTool(Tool):
    """smolagents-style Hugging Face Hub statistics tool."""

    name = "hub_stats"
    description = "Fetches the most downloaded model from a specific Hub author."
    inputs = {"author": {"type": "string", "description": "The Hub author or organization."}}
    output_type = "string"

    def forward(self, author: str) -> str:
        return offline_hub_stats(author)


def run_smolagents_style_alfred(question: str) -> str:
    """Run an offline Alfred flow using smolagents-style tools."""
    search_tool = SearchTool()
    weather_tool = WeatherInfoTool()
    hub_tool = HubStatsTool()
    selected_tools = choose_tools(question)
    observations: list[str] = []

    if "search" in selected_tools:
        observations.append(search_tool(question))

    if "weather" in selected_tools:
        observations.append(weather_tool("Wayne Manor"))

    if "hub_stats" in selected_tools:
        observations.append(hub_tool("facebook"))

    return alfred_answer_from_observations(question, observations)


if __name__ == "__main__":
    question = "What is Facebook and what's their most popular model?"
    print(run_smolagents_style_alfred(question))
