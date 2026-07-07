"""Print a Mermaid flow map for Day27 tools."""


def main() -> None:
    """Print the Day27 tool integration flow."""
    flow_lines = [
        "flowchart TD",
        "    A[User question] --> B[Alfred analyzes intent]",
        "    B --> C{Which tools are needed?}",
        "    C -->|current info| D[web_search]",
        "    C -->|fireworks planning| E[weather_info]",
        "    C -->|AI developer topic| F[hub_stats]",
        "    D --> G[Collect observations]",
        "    E --> G",
        "    F --> G",
        "    G --> H[Alfred composes final answer]",
        "    H --> I[Return response]",
    ]
    print("\n".join(flow_lines))


if __name__ == "__main__":
    main()
