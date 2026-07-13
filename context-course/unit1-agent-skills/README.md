# Unit 1：Agent Skills

本目录保存 Hugging Face Context Course Unit 1 的 Skills 实践代码、测试数据和运行说明。

理论笔记统一保存在项目根目录的 `notes/` 中。

## 学习目标

完成本单元后，需要能够：

1. 解释 Skill、Prompt、Tool 和 MCP 的区别；
2. 按 Agent Skills Specification 创建合法的 Skill；
3. 编写准确的 `name` 和 `description`；
4. 使用 `scripts/`、`references/` 和 `assets/` 组织资源；
5. 设计应该触发与不应该触发的测试问题；
6. 根据真实执行记录持续改进 Skill；
7. 完成音频文稿创作 Skill。

## 计划结构

```text
unit1-agent-skills/
├── README.md
├── first-skill/                 # 教材基础练习
├── audio-script-writing/        # 本项目的业务 Skill
└── tests/                       # 触发测试和输出质量测试
```

子目录将在对应实践日创建，避免提前添加没有内容的空目录。

## 当前进度

- [x] Day33：Skills 概念、产生背景、规范与设计原则
- [ ] Skills 与 Prompt 的深入对比
- [ ] `SKILL.md` 格式
- [ ] Skill 安装与调用
- [ ] 第一个可运行 Skill
- [ ] 触发评测与输出质量评测
- [ ] 音频文稿创作 Skill

## 官方资料

- [Unit 1：Agent Skills](https://huggingface.co/learn/context-course/unit1/introduction)
- [Unit 1 GitHub 原文](https://github.com/huggingface/context-course/blob/main/units/en/unit1/introduction.mdx)
- [What Are Agent Skills?](https://huggingface.co/learn/context-course/unit1/what-are-skills)
- [The SKILL.md Format](https://huggingface.co/learn/context-course/unit1/skill-format)
- [Agent Skills Specification](https://agentskills.io/specification)
