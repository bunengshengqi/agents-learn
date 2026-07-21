"""验证与框架无关的纯业务逻辑。"""

from __future__ import annotations

import json

import text_tools


def main() -> None:
    """执行正常输入、边界输入和错误输入断言。"""
    stats = json.loads(text_tools.analyze_text("Hello MCP. Hello Agent!"))
    assert stats["total_words"] == 4
    assert stats["total_sentences"] == 2
    assert stats["unique_words"] == 3

    keywords = json.loads(text_tools.extract_keywords("agent agent mcp tools tools tools", 2))
    assert keywords["keywords"][0] == {"word": "tools", "frequency": 3}

    reading = json.loads(text_tools.check_reading_level("The cat sat on the mat."))
    assert reading["reading_level"] == "Elementary School"

    writing = json.loads(text_tools.check_writing_basics("Hello  agent"))
    assert writing["issue_count"] == 2

    summary = json.loads(text_tools.summarize_text("One. Two! Three?", 2))
    assert summary["summary"] == "One. Two!"
    assert summary["selected_sentences"] == 2

    assert text_tools.reverse_text("Agent") == "tnegA"

    try:
        text_tools.extract_keywords("hello", 21)
    except ValueError as error:
        assert "1 到 20" in str(error)
    else:
        raise AssertionError("count=21 应该触发 ValueError")

    try:
        text_tools.extract_keywords("hello agent", 2.5)
    except ValueError as error:
        assert "1 到 20" in str(error)
    else:
        raise AssertionError("count=2.5 应该触发 ValueError")

    print("✅ Day43 纯业务函数测试通过")


if __name__ == "__main__":
    main()
