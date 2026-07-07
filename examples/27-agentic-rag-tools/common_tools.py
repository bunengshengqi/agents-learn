"""Shared offline tools for Day27 examples."""

from __future__ import annotations


WEB_RESULTS = {
    "facebook": (
        "Facebook is a social networking and technology company known for its "
        "social platform, and it is part of Meta Platforms."
    ),
    "france president": (
        "The current President of France is Emmanuel Macron. This mock result is "
        "for local learning only; use real search for live facts."
    ),
    "ai news": (
        "A safe AI conversation topic is the rapid growth of open-source language "
        "models and responsible evaluation."
    ),
}


WEATHER_RESULTS = {
    "paris": {"condition": "Clear", "temp_c": 24, "wind": "Low"},
    "gotham": {"condition": "Windy", "temp_c": 18, "wind": "High"},
    "wayne manor": {"condition": "Clear", "temp_c": 21, "wind": "Low"},
}


HUB_STATS = {
    "facebook": {
        "model_id": "facebook/esmfold_v1",
        "downloads": 13202321,
    },
    "google": {
        "model_id": "google-bert/bert-base-uncased",
        "downloads": 9845123,
    },
    "Qwen": {
        "model_id": "Qwen/Qwen2.5-Coder-32B-Instruct",
        "downloads": 6512345,
    },
}


def offline_web_search(query: str) -> str:
    """Return a deterministic mock web search result."""
    normalized = query.lower()

    if "facebook" in normalized:
        return WEB_RESULTS["facebook"]

    if "france" in normalized or "president" in normalized:
        return WEB_RESULTS["france president"]

    if "ai" in normalized or "news" in normalized:
        return WEB_RESULTS["ai news"]

    return "No mock web result found. Replace offline_web_search with a real search API."


def offline_weather_info(location: str) -> str:
    """Return deterministic mock weather information."""
    normalized = location.lower()
    data = WEATHER_RESULTS.get(normalized)

    if data is None:
        data = {"condition": "Clear", "temp_c": 22, "wind": "Low"}

    return (
        f"Weather in {location}: {data['condition']}, "
        f"{data['temp_c']}°C, wind={data['wind']}."
    )


def offline_hub_stats(author: str) -> str:
    """Return deterministic mock Hugging Face Hub statistics."""
    data = HUB_STATS.get(author)

    if data is None:
        normalized_author = author.lower()
        for known_author, known_data in HUB_STATS.items():
            if known_author.lower() == normalized_author:
                data = known_data
                break

    if data is None:
        return f"No mock Hub model statistics found for author {author}."

    return (
        f"The most downloaded model by {author} is {data['model_id']} "
        f"with {data['downloads']:,} downloads."
    )


def choose_tools(question: str) -> list[str]:
    """Choose which tools Alfred should use for a question."""
    normalized = question.lower()
    selected: list[str] = []

    if any(word in normalized for word in ["who", "what", "current", "news", "facebook"]):
        selected.append("search")

    if any(word in normalized for word in ["weather", "fireworks", "rain", "wind"]):
        selected.append("weather")

    if any(word in normalized for word in ["model", "hub", "downloads", "popular"]):
        selected.append("hub_stats")

    if not selected:
        selected.append("search")

    return selected


def alfred_answer_from_observations(question: str, observations: list[str]) -> str:
    """Compose Alfred's final answer from tool observations."""
    return (
        f"Question: {question}\n"
        "Alfred gathered:\n"
        + "\n".join(f"- {item}" for item in observations)
        + "\nFinal answer: Alfred can now answer with current context and tool evidence."
    )
