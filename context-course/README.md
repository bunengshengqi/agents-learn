# Context Course 实践代码

本目录保存 Day32 之后的 Hugging Face Context Course 实践代码、测试和综合项目。

课程笔记统一保存在项目根目录的 `notes/` 中，本目录不重复保存长篇理论课件。

## 学习主线

| 阶段 | 主题 | 计划目录 |
|---|---|---|
| Unit 0 | 课程介绍与环境准备 | `unit0-onboarding/` |
| Unit 1 | Agent Skills | `unit1-agent-skills/` |
| Unit 2 | MCP | `unit2-mcp/` |
| Unit 3 | Plugins | `unit3-plugins/` |
| Unit 4 | Subagents | `unit4-subagents/` |
| Unit 5 | Hooks | `unit5-hooks/` |
| Unit 6 | Nano Harness | `unit6-nano-harness/` |
| 综合项目 | 音频内容生产 Agent | `capstone/audio-content-agent/` |

目录将在学习到对应单元时创建，避免提前生成没有实际内容的空目录。

## 目录约定

```text
context-course/
├── README.md
├── unit0-onboarding/
├── unit1-agent-skills/
├── unit2-mcp/
├── unit3-plugins/
├── unit4-subagents/
├── unit5-hooks/
├── unit6-nano-harness/
├── shared/
├── tests/
└── capstone/
    └── audio-content-agent/
```

## 学习原则

每个单元至少需要留下：

1. 一个可以真实执行的实现；
2. 正常、边界和异常测试；
3. 一份运行说明；
4. 一次失败案例复盘；
5. 一个可以复用到综合项目中的能力。

Unit 0 主要完成课程理解、环境确认和项目规划，没有必要为了形式编写无意义的示例代码。

## 当前进度

- [x] Day32：课程介绍、Context Engineering 基础与环境说明
- [x] Day33：Agent Skills 概念、背景、规范与设计原则
- [ ] Unit 1：Agent Skills
- [ ] Unit 2：MCP
- [ ] Unit 3：Plugins
- [ ] Unit 4：Subagents
- [ ] Unit 5：Hooks
- [ ] Unit 6：Nano Harness
- [ ] 综合项目：音频内容生产 Agent

## 课程资料

- [Hugging Face Context Course](https://huggingface.co/learn/context-course/unit0/introduction)
- [Context Course GitHub](https://github.com/huggingface/context-course)
- [Day32 原始教材](https://github.com/huggingface/context-course/blob/main/units/en/unit0/introduction.mdx)
