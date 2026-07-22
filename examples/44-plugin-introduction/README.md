# Day 44：插件概念最小示例

这个目录只用于理解插件结构，不会自动安装或启用任何插件。完整讲解见 [Day44 学习笔记](../../notes/Day44-第三单元插件入门.md)。

```text
day44-hello-plugin/
├── .codex-plugin/
│   └── plugin.json       插件清单：它是谁、版本、包含哪些组件
└── skills/
    └── hello/
        └── SKILL.md      插件内的一项可复用工作流
```

## 检查示例

运行项目自带的教学检查：

```bash
python3 examples/44-plugin-introduction/validate_example.py
```

也可以使用 Codex 内置 `plugin-creator` 技能附带的严格验证器：

```bash
.venv/bin/python ~/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  examples/44-plugin-introduction/day44-hello-plugin
```

## 为什么没有 marketplace.json？

因为第44天只学习概念和最小结构。Marketplace 是“插件目录”，安装会改变 Codex 的可用扩展和本机配置；本示例刻意不执行安装。后续学习构建和分发插件时再添加 marketplace。

## 为什么没有 MCP、Hook 和 Connector？

它们都是可选组件。一个插件只要有合法 manifest，就可以只打包一个 Skill。先掌握最小模型，再逐步增加权限和复杂度。
