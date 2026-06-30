"""
第18天代码 04：ToolSpecs 示例说明

ToolSpecs:
社区预设工具包。
例如 GmailToolSpec 可以一次性提供：
- 搜索邮件
- 读取邮件
- 发送邮件
- 创建草稿
- 读取附件等

注意：
这个示例是结构演示，不直接连接 Gmail。
真正运行 Gmail 工具通常还需要 Google OAuth 凭证。

运行：
python 04_toolspecs_gmail_preview.py
"""


def main() -> None:
    print("====== ToolSpecs 场景说明 ======")
    print("ToolSpecs 不是单个函数，而是一组工具。")
    print("例如 GmailToolSpec 可以提供搜索邮件、读取邮件、发送邮件、创建草稿等工具。")
    print()

    print("安装示例：")
    print("pip install llama-index-tools-google")
    print()

    print("代码结构示例：")
    code = """
from llama_index.tools.google import GmailToolSpec

gmail_spec = GmailToolSpec()
gmail_tools = gmail_spec.to_tool_list()

for tool in gmail_tools:
    print(tool.metadata.name, tool.metadata.description)
"""
    print(code)

    print("适合场景：连接 Gmail、Google Drive、Slack、GitHub 等第三方服务。")


if __name__ == "__main__":
    main()
