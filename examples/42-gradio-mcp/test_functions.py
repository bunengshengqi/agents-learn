"""不启动网络服务，快速验证 Day 42 的核心业务函数。"""

from app import analyze_text, count_vowels, extract_keywords, reverse_text


def main() -> None:
    """执行可重复的函数级断言。"""
    assert '"words": 2' in analyze_text("Hello MCP")
    assert reverse_text("Agent") == "tnegA"
    assert count_vowels("Gradio MCP") == 3
    assert extract_keywords("agent agent mcp tools tools tools", 2) == ["tools", "agent"]
    print("✅ Day42 核心函数测试通过")


if __name__ == "__main__":
    main()
