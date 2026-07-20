"""检查 Day 41 的 Codex MCP TOML 示例是否符合基本安全与结构规则。"""

from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path


SECRET_NAME = re.compile(r"(?:token|secret|password|api[_-]?key)", re.IGNORECASE)
PLACEHOLDER = re.compile(r"^(?:YOUR_|<|\$\{|example|replace)", re.IGNORECASE)
PATH_PLACEHOLDER = re.compile(r"(?:ABSOLUTE/PATH|PATH/TO|your/path)", re.IGNORECASE)


def validate(path: Path) -> list[str]:
    """读取 TOML 并返回发现的问题；空列表代表通过检查。"""
    with path.open("rb") as file:
        config = tomllib.load(file)

    problems: list[str] = []
    servers = config.get("mcp_servers")
    if not isinstance(servers, dict) or not servers:
        return ["缺少非空的 [mcp_servers.<name>] 配置"]

    for name, server in servers.items():
        if not isinstance(server, dict):
            problems.append(f"{name}: Server 配置必须是 TOML table")
            continue

        has_command = isinstance(server.get("command"), str)
        has_url = isinstance(server.get("url"), str)
        if has_command == has_url:
            problems.append(f"{name}: command 与 url 必须且只能配置一个")

        if has_command:
            command = server["command"]
            if PATH_PLACEHOLDER.search(command):
                problems.append(f"{name}: command 仍包含示例占位路径")
            if "/" in command and not Path(command).is_absolute():
                problems.append(f"{name}: 含路径的 command 应使用绝对路径")

            for arg in server.get("args", []):
                if isinstance(arg, str) and (arg.endswith(".py") or "/" in arg):
                    if PATH_PLACEHOLDER.search(arg):
                        problems.append(f"{name}: 参数仍包含示例占位路径：{arg}")
                    if not Path(arg).is_absolute():
                        problems.append(f"{name}: 脚本或文件参数应使用绝对路径：{arg}")

            cwd = server.get("cwd")
            if isinstance(cwd, str) and PATH_PLACEHOLDER.search(cwd):
                problems.append(f"{name}: cwd 仍包含示例占位路径")

        if has_url and not server["url"].startswith("https://"):
            problems.append(f"{name}: 远程 Server 建议使用 https://")

        env = server.get("env", {})
        if isinstance(env, dict):
            for key, value in env.items():
                if SECRET_NAME.search(key) and isinstance(value, str) and not PLACEHOLDER.search(value):
                    problems.append(f"{name}: {key} 疑似把真实密钥写进了配置")

        headers = server.get("http_headers", {})
        if isinstance(headers, dict):
            for key, value in headers.items():
                if key.lower() == "authorization" and isinstance(value, str):
                    problems.append(f"{name}: 不要在 http_headers 中硬编码 Authorization")

    return problems


def main() -> int:
    """解析命令行参数，打印检查结果并设置退出码。"""
    parser = argparse.ArgumentParser(description="检查 Codex MCP TOML 配置")
    parser.add_argument("path", type=Path, help="要检查的 config.toml")
    args = parser.parse_args()

    try:
        problems = validate(args.path)
    except (OSError, tomllib.TOMLDecodeError) as error:
        print(f"❌ 无法读取配置：{error}")
        return 2

    if problems:
        print("❌ 配置检查未通过：")
        for problem in problems:
            print(f"- {problem}")
        return 1

    print(f"✅ 配置检查通过：{args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
