"""Day24 示例 3：工具错误处理演示。

这不是完整 Agent，只是单独演示课程里提到的错误处理原则：
- 文件不存在
- 文件类型不支持
- 除以 0
"""

from pathlib import Path

from langchain_core.tools import tool


@tool
def extract_text(file_path: str) -> str:
    """Extract text from a local text-like document file."""
    path = Path(file_path)
    if not path.exists():
        return f"ERROR: file not found: {file_path}"

    if path.suffix.lower() not in {".txt", ".md", ".csv"}:
        return f"ERROR: unsupported file type for this demo: {path.suffix}"

    return path.read_text(encoding="utf-8")


@tool
def divide(a: float, b: float) -> str:
    """Divide a by b and return a clear error when b is 0."""
    if b == 0:
        return "ERROR: cannot divide by zero"
    return str(a / b)


if __name__ == "__main__":
    print("Missing file:")
    print(extract_text.invoke({"file_path": "missing-file.txt"}))

    print("\nUnsupported file:")
    print(extract_text.invoke({"file_path": __file__}))

    print("\nDivide by zero:")
    print(divide.invoke({"a": 100, "b": 0}))

    print("\nSuccessful divide:")
    print(divide.invoke({"a": 1200, "b": 40}))
