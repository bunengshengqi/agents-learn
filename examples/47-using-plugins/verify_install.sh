#!/usr/bin/env bash
# Day47 装前自检脚本
# 运行：bash examples/47-using-plugins/verify_install.sh

set -euo pipefail

# 1. 定位本仓库根目录
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
EXAMPLE_DIR="$REPO_ROOT/examples/47-using-plugins"
PLUGIN_DIR="$REPO_ROOT/examples/46-text-processor-plugin"
SERVER_DIR="$REPO_ROOT/examples/43-text-processor-mcp"

echo "==> 1. 检查所有 JSON 文件"
for f in \
  "$EXAMPLE_DIR/marketplace.json" \
  "$EXAMPLE_DIR/agents/plugins/marketplace.json" \
  "$EXAMPLE_DIR/.opencode/package.json" \
  "$PLUGIN_DIR/text-processor-plugin/.claude-plugin/plugin.json" \
  "$PLUGIN_DIR/text-processor-plugin/.codex-plugin/plugin.json" \
  "$PLUGIN_DIR/text-processor-plugin/.mcp.json" \
  "$PLUGIN_DIR/pi/text-processor-plugin/package.json" \
  "$PLUGIN_DIR/opencode/opencode.json"
do
  python3 -m json.tool "$f" > /dev/null && echo "  OK  $f" || { echo "  FAIL $f"; exit 1; }
done

echo "==> 2. 检查 SKILL.md 数量（应为 12 = 6 + 6）"
SKILL_COUNT=$(find "$PLUGIN_DIR" -name "SKILL.md" | wc -l | tr -d ' ')
if [ "$SKILL_COUNT" -ne 12 ]; then
  echo "  FAIL 期望 12 个 SKILL.md，实际 $SKILL_COUNT"
  exit 1
fi
echo "  OK  12 个 SKILL.md 都到位"

echo "==> 3. 检查 Day43 MCP server 可执行"
if [ -f "$SERVER_DIR/server.py" ]; then
  echo "  OK  server.py 存在"
else
  echo "  FAIL 找不到 $SERVER_DIR/server.py"
  exit 1
fi

echo "==> 4. 检查路径引用一致"
# marketplace.json 里的 source 路径应能解析到 plugin.json
SOURCE_REL="../46-text-processor-plugin/text-processor-plugin"
RESOLVED="$EXAMPLE_DIR/$SOURCE_REL/.claude-plugin/plugin.json"
if [ -f "$RESOLVED" ]; then
  echo "  OK  marketplace.json 路径解析正确"
else
  echo "  FAIL $RESOLVED 不存在"
  exit 1
fi

echo "✅ All files validated"
