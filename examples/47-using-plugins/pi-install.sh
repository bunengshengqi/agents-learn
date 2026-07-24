#!/usr/bin/env bash
# Day47 Pi 安装命令片段
# 复制粘贴到终端执行即可
# 注意：路径请改成你本机的仓库根目录

REPO_ROOT="/Users/yuyuan/Desktop/agents-learn"

# 1. 安装 Pi package
pi install "$REPO_ROOT/examples/46-text-processor-plugin/pi/text-processor-plugin" -l

# 2. 如果需要 MCP 工具，先装适配器
pi install npm:pi-mcp-adapter

# 3. 在 Pi 内 /reload 激活
# pi /reload
