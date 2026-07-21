"""纯文本处理逻辑。

这个模块不依赖 MCP 或 Gradio，因此可以被本地 Server、Web 应用和测试共同复用。
"""

from __future__ import annotations

import json
import re
from collections import Counter


MAX_TEXT_LENGTH = 50_000
ENGLISH_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "been",
    "but",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "were",
    "with",
}


def _validate_text(text: str) -> str:
    """验证公共输入，防止空文本和超大请求。"""
    if not isinstance(text, str):
        raise ValueError("text 必须是字符串")
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("text 不能为空")
    if len(cleaned) > MAX_TEXT_LENGTH:
        raise ValueError(f"text 不能超过 {MAX_TEXT_LENGTH} 个字符")
    return cleaned


def _english_words(text: str) -> list[str]:
    """提取英文单词；阅读难度和关键词算法都使用它。"""
    return re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)


def _sentences(text: str) -> list[str]:
    """按照中英文句末标点进行简单切句。"""
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?。！？])\s*", text) if sentence.strip()]


def _json(data: object) -> str:
    """统一输出格式，让网页用户与 Agent 都能轻松阅读。"""
    return json.dumps(data, ensure_ascii=False, indent=2)


def analyze_text(text: str) -> str:
    """Analyze text and return statistics as JSON.

    Args:
        text: The text to analyze, from 1 to 50,000 characters.

    Returns:
        A JSON string with character, word, sentence, and line statistics.
    """
    cleaned = _validate_text(text)
    words = re.findall(r"\b\w+\b", cleaned, flags=re.UNICODE)
    sentences = _sentences(cleaned)
    characters_without_whitespace = sum(not char.isspace() for char in cleaned)

    result = {
        "total_characters": len(cleaned),
        "characters_without_whitespace": characters_without_whitespace,
        "total_words": len(words),
        "unique_words": len({word.casefold() for word in words}),
        "total_sentences": len(sentences),
        "total_lines": len(cleaned.splitlines()),
        "average_word_length": (
            round(sum(len(word) for word in words) / len(words), 2) if words else 0
        ),
        "average_sentence_length": (
            round(len(words) / len(sentences), 2) if sentences else 0
        ),
    }
    return _json(result)


def extract_keywords(text: str, count: int = 5) -> str:
    """Extract frequent English keywords from text.

    Args:
        text: The English text from which to extract keywords.
        count: The number of keywords to return, from 1 to 20.

    Returns:
        A JSON string containing keywords and their frequencies.
    """
    cleaned = _validate_text(text)
    if isinstance(count, bool) or not isinstance(count, (int, float)):
        raise ValueError("count 必须是 1 到 20 之间的整数")
    if not float(count).is_integer() or not 1 <= count <= 20:
        raise ValueError("count 必须在 1 到 20 之间")
    count = int(count)

    normalized_words = [word.casefold() for word in _english_words(cleaned)]
    meaningful_words = [
        word for word in normalized_words if word not in ENGLISH_STOPWORDS and len(word) > 1
    ]
    frequencies = Counter(meaningful_words)
    keywords = [
        {"word": word, "frequency": frequency}
        for word, frequency in frequencies.most_common(count)
    ]
    return _json({"keywords": keywords})


def _estimate_syllables(word: str) -> int:
    """粗略估算一个英文单词的音节数，不替代语言学词典。"""
    normalized = word.casefold()
    vowel_groups = re.findall(r"[aeiouy]+", normalized)
    syllables = len(vowel_groups)
    if normalized.endswith("e") and syllables > 1 and not normalized.endswith(("le", "ye")):
        syllables -= 1
    return max(syllables, 1)


def check_reading_level(text: str) -> str:
    """Estimate the reading difficulty of English text.

    Args:
        text: The English passage whose approximate reading level should be estimated.

    Returns:
        A JSON string with Flesch-Kincaid grade and a plain-language level.
    """
    cleaned = _validate_text(text)
    words = _english_words(cleaned)
    if not words:
        raise ValueError("阅读难度工具只支持包含英文单词的文本")

    sentence_count = max(len(_sentences(cleaned)), 1)
    syllable_count = sum(_estimate_syllables(word) for word in words)
    grade = 0.39 * (len(words) / sentence_count)
    grade += 11.8 * (syllable_count / len(words)) - 15.59
    grade = max(0, round(grade, 1))

    if grade < 6:
        level = "Elementary School"
    elif grade < 9:
        level = "Middle School"
    elif grade < 13:
        level = "High School"
    else:
        level = "College/Academic"

    return _json(
        {
            "grade_level": grade,
            "reading_level": level,
            "words": len(words),
            "sentences": sentence_count,
            "estimated_syllables": syllable_count,
            "warning": "This is an English heuristic, not a professional assessment.",
        }
    )


def check_writing_basics(text: str) -> str:
    """Check a few deterministic English writing rules.

    Args:
        text: The English text to check for repeated spaces and simple sentence issues.

    Returns:
        A JSON string with rule-based warnings and counts.
    """
    cleaned = _validate_text(text)
    issues: list[dict[str, str | int]] = []

    repeated_spaces = len(re.findall(r" {2,}", cleaned))
    if repeated_spaces:
        issues.append(
            {
                "rule": "repeated_spaces",
                "count": repeated_spaces,
                "message": "Replace consecutive spaces with one space.",
            }
        )

    sentences = _sentences(cleaned)
    long_sentences = sum(len(_english_words(sentence)) > 30 for sentence in sentences)
    if long_sentences:
        issues.append(
            {
                "rule": "long_sentences",
                "count": long_sentences,
                "message": "Consider splitting English sentences longer than 30 words.",
            }
        )

    missing_terminal_punctuation = int(cleaned[-1] not in ".!?。！？")
    if missing_terminal_punctuation:
        issues.append(
            {
                "rule": "terminal_punctuation",
                "count": 1,
                "message": "Consider ending the final sentence with punctuation.",
            }
        )

    return _json(
        {
            "issue_count": sum(int(issue["count"]) for issue in issues),
            "issues": issues,
            "warning": "This checks a few deterministic rules; it is not a spell checker or grammar model.",
        }
    )


def summarize_text(text: str, max_sentences: int = 2) -> str:
    """Create a deterministic extractive summary from the first sentences.

    Args:
        text: The text to summarize.
        max_sentences: The maximum number of leading sentences to keep, from 1 to 5.

    Returns:
        A JSON string containing an extractive summary and metadata.
    """
    cleaned = _validate_text(text)
    if isinstance(max_sentences, bool) or not isinstance(max_sentences, (int, float)):
        raise ValueError("max_sentences 必须是 1 到 5 之间的整数")
    if not float(max_sentences).is_integer() or not 1 <= max_sentences <= 5:
        raise ValueError("max_sentences 必须在 1 到 5 之间")
    max_sentences = int(max_sentences)

    sentences = _sentences(cleaned)
    selected = sentences[:max_sentences]
    return _json(
        {
            "summary": " ".join(selected),
            "source_sentences": len(sentences),
            "selected_sentences": len(selected),
            "method": "lead-sentence extractive summary; no LLM is used",
        }
    )


def reverse_text(text: str) -> str:
    """Reverse all characters in text.

    Args:
        text: The text whose character order should be reversed.

    Returns:
        The text in reverse character order.
    """
    return _validate_text(text)[::-1]
