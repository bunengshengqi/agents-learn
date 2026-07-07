"""Compare smolagents, LlamaIndex, and LangGraph style outputs."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


BASE_DIR = Path(__file__).parent


def load_function(file_name: str, function_name: str):
    """Load a function from a sibling Python file."""
    module_path = BASE_DIR / file_name
    spec = importlib.util.spec_from_file_location(file_name.replace(".py", ""), module_path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return getattr(module, function_name)


def main() -> None:
    """Run the same question through three framework styles."""
    question = "Is the weather good for fireworks, and what is Facebook's most popular model?"

    runners = [
        (
            "smolagents",
            load_function("01_smolagents_style_tools.py", "run_smolagents_style_alfred"),
        ),
        (
            "llama-index",
            load_function("02_llama_index_style_tools.py", "run_llama_index_style_alfred"),
        ),
        (
            "langgraph",
            load_function("03_langgraph_style_tools.py", "run_langgraph_style_alfred"),
        ),
    ]

    for name, runner in runners:
        print("=" * 80)
        print(name)
        print(runner(question))


if __name__ == "__main__":
    main()
