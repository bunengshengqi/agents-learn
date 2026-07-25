# Day 51：多智能体工作流实战——研究 → 实现 → 验证流水线

**课程来源**：Hugging Face Context Course — Unit 4: Hands-On (Multi-Agent Workflow)  
**原文链接**：https://huggingface.co/learn/context-course/unit4/hands-on  
**GitHub 地址**：https://github.com/huggingface/context-course/blob/main/units/en/unit4/hands-on.mdx  
**学习日期**：2026-07-25

---

## 一、这节课到底要学什么？

前三天我们已经学过：

- Day 48：子代理是什么、为什么需要子代理；
- Day 49：Fan-Out/Fan-In、Pipeline、Supervisor、Swarm 四种常见模式；
- Day 50：如何在 Claude Code、Codex、Pi 中创建、调用、管理子代理。

> **今天是本单元的动手实践课：把前面所有理论拼成一条真实可跑的流水线，亲手搭一支“AI 研发小队”。**

如果说前三天是“学习组织管理理论”和“熟悉工具”，那么今天就是“正式开工，用一条流水线交付一个功能”。

本节课要搭建的流水线叫 **研究 → 实现 → 验证（research → implement → verify）**：

- 一个**研究员**子代理摸清现有代码；
- 一个**施工员**子代理写下改动；
- 两个**只读审查员**（安全 + 性能）并行签字放行，然后才允许合并。

读完本课，你应该能够回答：

1. 一条完整的多智能体流水线由哪些角色组成？各自负责什么？
2. 为什么只有施工员能写代码，其它三个角色都只读？
3. 在 `.claude/agents/` 中怎样定义一个专职子代理？
4. 为什么工作流要写进 `CLAUDE.md` / `AGENTS.md`？
5. Fan-Out（扇出并行）和 Pipeline（顺序流水线）分别在什么时候用？
6. “委派（Delegation）”和“自动化（Automation）”有什么区别？不能混用什么？

---

## 二、先看全景图：这条流水线长什么样

```text
       用户："帮我加一个 OAuth2 登录功能"
                    │
                    ▼
        ┌───────────────────────┐
        │  研究员 researcher     │  只读：Read / Grep / Glob
        │  摸清现有代码结构       │  → 输出“现状报告”
        └───────────────────────┘
                    │ 把报告交给下一棒
                    ▼
        ┌───────────────────────┐
        │  施工员 implementer    │  可写：Read / Write / Bash
        │  照着报告写新代码       │  → 输出“新代码 + 测试”
        └───────────────────────┘
                    │ 交给两个验收员（同时进行）
          ┌─────────┴─────────┐
          ▼                   ▼
   ┌─────────────┐     ┌──────────────┐
   │ 安全审查员   │     │ 性能审查员    │   都只读
   │ 查漏洞       │     │ 查性能瓶颈    │
   └─────────────┘     └──────────────┘
          └─────────┬─────────┘
                    ▼
        父代理汇总所有结论 → 交给用户拍板是否合并
```

记住这张图，后面每一步都是在往这张图里填一个方块。

> **一句话概括：你不再让一个 AI 全包，而是组建一支分工明确的 AI 小队——一个侦察、一个施工、两个验收，像工厂流水线一样协作。**

---

## 三、为什么要分工，而不是让一个 AI 全干？

打个比方：盖房子时，你不会让同一个人既画图纸、又搬砖、又做质检——因为他会累、会偏心（自己盖的房子自己验收当然说没问题）。

拆成不同角色后，好处很清楚：

| 好处 | 说明 |
|---|---|
| **目标单一** | 每个角色只做一件事，不容易跑偏 |
| **权限最小** | 每个角色只拿必要工具，更安全（施工队不该有拆迁大锤） |
| **验收独立** | 审查员和施工员不是同一个，不会给自己的活放水 |
| **可以并行** | 安全审查和性能审查互不依赖，能同时进行，省时间 |

---

## 四、Step 0：建项目骨架

课程同时给了三个平台（Claude Code / Codex / Pi）的写法，思路完全一样，只是**文件格式和目录不同**。本笔记以 **Claude Code** 为主线讲解，其它平台在第十二章统一对照。

**Claude Code 版：**

```bash
mkdir code-quality-pipeline      # 建项目文件夹
cd code-quality-pipeline

mkdir -p .claude/agents          # 存放“子代理定义”的文件夹
touch main.py                    # 将来要写的代码文件
touch .claude/CLAUDE.md          # 项目规矩说明书
```

关键就两处：

```text
.claude/
├── agents/       # 每个子代理一个文件，定义它“是谁、能用什么工具”
└── CLAUDE.md     # 写给整个团队看的“工作流程规范”
```

---

## 五、Step 1：定义 4 个专职子代理

在 Claude Code 中，每个子代理是一个 Markdown 文件，分两部分：**顶部的“身份证”（YAML Frontmatter）** + **下面的“岗位职责”（正文提示词）**。

### 1. 研究员 `.claude/agents/researcher.md`

```markdown
---
name: researcher
description: Explores codebase and documents architecture
tools: Read, Grep, Glob        ← 只给“看”的工具，不给“写”
model: sonnet
---
You are an architecture researcher. Your job is to:
1. Explore the codebase structure
2. Identify key modules, dependencies, and patterns
3. Document the architecture clearly
4. Note areas for improvement

Be thorough. Read 10+ files to build a complete picture.
```

逐字段解释这张“身份证”：

| 字段 | 作用 | 通俗理解 |
|---|---|---|
| `name` | 代理名称，父代理靠它点名派活 | 员工姓名 |
| `description` | 一句话说明用途，帮父代理判断“该派给谁” | 岗位说明 |
| `tools` | 🔑 **最重要**：允许使用哪些工具 | 门禁卡能开哪些门 |
| `model` | 使用哪个模型 | 给员工配哪种“大脑” |

### 2. 施工员 `.claude/agents/implementer.md`

```markdown
---
name: implementer
description: Writes code based on specifications
tools: Read, Write, Glob, Bash    ← 唯一有“写”和“执行”权限的角色
model: sonnet
---
You are a skilled developer. Your job is to:
1. Read the specification and architecture docs
2. Write clean, well-tested code
3. Follow existing patterns and conventions
4. Document your changes

Focus on correctness and maintainability.
```

### 3. 安全审查员 `.claude/agents/security-reviewer.md`

```markdown
---
name: security-reviewer
description: Reviews code for vulnerabilities
tools: Read, Grep                 ← 只读
model: sonnet
---
You are a security expert. Your job is to:
1. Review code for security vulnerabilities
2. Check for data leakage, injection attacks, etc.
3. Recommend fixes
4. Assess overall security posture

Be thorough. This code might be production-critical.
```

### 4. 性能审查员 `.claude/agents/performance-reviewer.md`

```markdown
---
name: performance-reviewer
description: Reviews code for performance issues
tools: Read, Grep                 ← 只读
model: sonnet
---
You are a performance specialist. Your job is to:
1. Identify performance bottlenecks
2. Suggest optimizations
3. Calculate impact
4. Recommend best practices

Be specific with numbers and concrete suggestions.
```

### 一张表看懂 4 个角色的权限差异

| 角色 | 工具权限 | 能不能改代码 | 职责 |
|---|---|---|---|
| **researcher**（研究员） | Read, Grep, Glob | ❌ 只读 | 摸清现有代码 |
| **implementer**（施工员） | Read, Write, Glob, **Bash** | ✅ 可写可执行 | 真正写代码 |
| **security-reviewer**（安全审查） | Read, Grep | ❌ 只读 | 查漏洞：数据泄露、注入等 |
| **performance-reviewer**（性能审查） | Read, Grep | ❌ 只读 | 查性能：瓶颈、优化建议 |

> **看懂这张表就抓住了精髓：只有施工员能“写”，其他三个都只能“看”。研究和验收阶段绝不动你的代码，风险被牢牢锁住——这就是“最小权限原则”。**

---

## 六、Step 2：把工作流写进 CLAUDE.md

Step 1 定义的是“每个人是谁”，这一步定义的是“**团队按什么流程干活**”。

写进 `.claude/CLAUDE.md` 的好处是：**全队每次都按同一套流程走**，不会今天这样、明天那样。

```markdown
# Code Quality Pipeline

## Architecture
This project uses a multi-agent workflow:
1. **Research** — Understand existing code
2. **Implement** — Write new features
3. **Verify** — Security and performance review

## Workflow Triggers

### Before Implementation（实现之前）
When the user asks for a new feature:
1. Use the researcher subagent first
2. Have it explore the codebase (15+ files)
3. Document architecture and relevant patterns
4. Pass findings to implementation stage

### During Implementation（实现过程中）
1. Spawn the implementer subagent
2. Provide it with: feature spec + architecture findings + existing patterns
3. Have it write the code

### Before Merge（合并之前）
1. Spawn security-reviewer and performance-reviewer in parallel
2. Both are read-only (no Write access)
3. Collect findings
4. Report to user before committing
```

> 💡 **给小白的重点**：`CLAUDE.md` 就像贴在车间墙上的《操作规程》。AI 每次干活前都会读它，所以你把流程写进去，等于“一次约定，长期生效”。

---

## 七、Step 3：实际使用——一句话让整条流水线跑起来

准备工作做完，用起来极简单。你只要给父代理一段话：

```text
我想加 OAuth2 认证。

1. 用 researcher 子代理探索现有认证系统，认真读 auth 模块（15+ 文件），
   记录当前架构和模式。
2. 用 implementer 子代理写 OAuth2 集成，基于研究发现，遵循现有模式。
3. 完成后，让 security-reviewer 和 performance-reviewer 并行审查代码，
   我想在合并前看到漏洞和瓶颈。
```

课程给出的**典型运行结果**（帮助你理解每一步都发生了什么）：

```text
Step 1: 启动研究员...
  ✓ 探索 auth/ 目录
  ✓ 读了 18 个相关文件
  ✓ 记录模式和依赖
  → 发现：现系统用 JWT + Redis 缓存，每小时轮换 token，每次 API 调用都校验。

Step 2: 启动施工员...
  ✓ 写 OAuth2 provider 集成
  ✓ 沿用现有 JWT 模式
  ✓ 加了测试
  → 产出：450 行新代码 + 测试

Step 3: 并行启动安全 + 性能审查员...
  ✓ 安全审查：强制 HTTPS？✓  token 已哈希？✓  日志无密钥？✓
    建议：给 OAuth 端点加限流
  ✓ 性能审查：每次认证 3 次数据库查询（符合预期）
    建议：缓存 OAuth provider 元数据

准备好合并了吗？请审阅以上结论。
```

注意最后一步：AI **没有擅自合并**，而是把结论摆给你，由**你拍板**。这是刻意设计的“人在回路（human in the loop）”。

---

## 八、Step 4：进阶玩法一——扇出并行研究（Fan-Out）

如果代码库很大，一个研究员读不过来，就派**多个研究员同时**读不同部分：

```text
Research codebase structure

[研究员 1：探索 backend/]      [研究员 2：探索 frontend/]     [研究员 3：探索 infrastructure/]
├─ authentication/            ├─ components/                ├─ docker/
├─ database/                  ├─ state/                     ├─ kubernetes/
└─ api/                       └─ pages/                     └─ monitoring/

三个并行跑 → 父代理汇总成一份完整架构总览
```

对应指令：

```text
Use 3 subagents to research our codebase:
- Researcher 1: Backend architecture
- Researcher 2: Frontend architecture
- Researcher 3: Infrastructure setup

Each should explore 15+ files and document patterns.
Then combine findings into an architecture overview.
```

> **好处**：三个同时干，速度快；每个只专注一块，读得深。这就是“分而治之”。

---

## 九、Step 5：进阶玩法二——经典流水线（Pipeline）

比“研究 → 实现 → 验证”更长的一条链，适合更正式的开发：

```text
Stage 1 架构设计   └─ Designer 子代理：定 schema、定接口
Stage 2 实现       └─ Developer 子代理：照设计写代码
Stage 3 安全审查   └─ Security 子代理：查漏洞
Stage 4 测试       └─ QA 子代理：写测试并跑
Stage 5 部署规划   └─ DevOps 子代理：规划部署策略

父代理：汇总所有结论并呈现给用户
```

对应指令的关键约束：

```text
Each stage is a subagent. Run sequentially
(output of stage N → input to stage N+1).
```

### Fan-Out 与 Pipeline 的关键区别

| 模式 | 执行方式 | 适用条件 | 例子 |
|---|---|---|---|
| **Fan-Out（扇出）** | 多个子代理**并行** | 各任务**互不依赖** | 两个审查员同时干；三个研究员分别读前后端 |
| **Pipeline（流水线）** | 一个接一个**串行** | 后一步**依赖**前一步的输出 | 施工必须等研究做完；测试必须等实现做完 |

> **判断口诀：后一步是否需要前一步的结果？需要 → 串行 Pipeline；不需要 → 并行 Fan-Out。**

---

## 十、最重要的一课：别把“自动化”和“委派”混为一谈

这节课有个进阶提醒，很多人会踩坑，单独拎出来讲。

有两种“让 AI 自动做事”的机制，别搞混：

| | **委派（Delegation）** | **自动化（Automation）** |
|---|---|---|
| 是什么 | 让**子代理**去思考、判断、干活 | 到某个时机**机械地**跑一段固定脚本 |
| 例子 | “派研究员去摸清架构” | “每次写完文件后，自动跑一遍 lint / 测试” |
| 用什么实现 | `CLAUDE.md` / `AGENTS.md` 里的流程说明 | **Hooks**（钩子）、扩展、配置文件 |

课程给的例子：如果你想“每次改动代码后自动跑检查脚本”，**不要**为此再造一个子代理，而是用 Claude Code 的 **hooks**（`.claude/settings.json`）：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/run-checks.sh" }
        ]
      }
    ]
  }
}
```

意思是：**每当** AI 用了 Write 或 Edit 工具，**自动**执行 `run-checks.sh`。这种“固定动作、无需思考”的事，交给 hook 又快又稳，不该浪费一个会思考的代理。

> 🎯 **一句话记住**：需要**判断**的交给子代理（委派）；**机械重复**的交给 hooks（自动化）。**Hooks、扩展、运行时设置是给工作流“打辅助”的，不是用来“驱动”子代理编排的。**

---

## 十一、三个平台对照（知道差异即可）

思路完全相同，只有文件格式和放置位置不同：

| 对比项 | Claude Code | Codex | Pi |
|---|---|---|---|
| 子代理定义文件 | `.claude/agents/*.md` | `.codex/agents/*.toml` | `.pi/agents/*.md` |
| 团队规范文件 | `.claude/CLAUDE.md` | `AGENTS.md` | `AGENTS.md` |
| “只读”怎么设 | `tools:` 里只给读类工具 | `sandbox_mode = "read-only"` | `tools:` 里只给读类工具 |
| 自动化机制 | hooks（settings.json） | `.codex/config.toml` 限制 | extensions（`.ts` 扩展） |
| 特殊准备 | 无 | 无 | 需先装 subagent 扩展到 `.pi/extensions/subagent/` |

**Codex 版子代理示例**（`.codex/agents/security-reviewer.toml`）：

```toml
name = "security_reviewer"
description = "Read-only reviewer focused on vulnerabilities, secrets, and privilege boundaries."
sandbox_mode = "read-only"
developer_instructions = """
Lead with concrete security risks.
Prioritize data leakage, injection, auth mistakes, and unsafe defaults.
"""
```

**Pi 版子代理示例**（`.pi/agents/security-reviewer.md`）：

```markdown
---
name: security-reviewer
description: Reviews code for vulnerabilities
tools: read, grep, find, ls
---
You are a security expert. Your job is to:
1. Review code for security vulnerabilities
2. Check for data leakage, injection attacks, and unsafe secrets handling
3. Recommend fixes
4. Assess overall security posture
```

> 你用的是 **Claude Code**，照第一列做即可。三个平台的自动化机制也各不相同：Codex 用 `config.toml` 限制线程上限，Pi 用扩展（如 `.pi/extensions/pipeline-guard.ts` 拦截危险命令）。

---

## 十二、最终产物长什么样

流水线跑完，可以把各角色结论汇成一份**结构化报告**（便于机器或团队消费）：

```json
{
  "researcher": {
    "architecture": {
      "modules": ["auth", "api", "database"],
      "patterns": ["MVC", "Repository pattern", "Middleware"],
      "dependencies": ["Express.js", "MongoDB", "Redis"]
    }
  },
  "implementer": {
    "files_created": ["oauth2.js", "oauth2.test.js"],
    "lines_of_code": 450,
    "test_coverage": 94
  },
  "security_reviewer": {
    "vulnerabilities": 0,
    "warnings": 1,
    "recommendations": ["Add rate limiting"]
  },
  "performance_reviewer": {
    "database_queries_per_request": 3,
    "bottlenecks": 0,
    "recommendations": ["Cache provider metadata"]
  }
}
```

> **结构化输出的价值**：父代理更容易比较、去重、排序，你也能一眼看清每个角色的产出。

---

## 十三、本项目演示的最佳实践

课程明确列出这条流水线示范了哪些工程原则：

1. **清晰的阶段分离**——研究、实现、验证各司其职；
2. **专职代理**——每个代理有专属工具和提示词，不贪多；
3. **并行执行**——安全与性能审查同时进行，省时间；
4. **流水线衔接**——每个阶段的输出喂给下一阶段；
5. **仓库级指令**——工作流写进 `CLAUDE.md` / `AGENTS.md`，全队一致。

---

## 十四、常见错误与纠正方法

| 错误做法 | 会发生什么 | 正确做法 |
|---|---|---|
| 让审查员也能写代码 | 一边检查一边改证据，结果不稳定；多审查员改同一文件冲突 | 审查员一律只读（Read/Grep） |
| 施工和研究硬并行 | 施工员缺少研究结果，凭空乱写 | 用 Pipeline 串行：研究 → 实现 |
| 两个审查员串行跑 | 白白多花一倍时间 | 互不依赖 → 并行 Fan-Out |
| 为“自动跑测试”造一个子代理 | 浪费一个会思考的代理，还不稳定 | 用 hooks / CI 做确定性自动化 |
| 把 CLAUDE.md 当硬触发器 | 关键步骤可能没按预想启动 | 强制检查交给 hook/CI，委派策略写 CLAUDE.md |
| AI 审查完直接合并 | 绕过人的最终判断 | 报告给用户，由用户拍板合并 |
| 给一个小任务开一堆代理 | 启动和汇总成本大于收益 | 小任务单代理直接完成 |

---

## 十五、如何判断该用哪种编排？

```text
任务是否很小、几分钟能完成？
├── 是 → 单代理直接做
└── 否
    │
    ├── 能拆成互不依赖的部分吗？
    │   ├── 是 → Fan-Out 并行（如三个研究员分别读前后端）
    │   └── 否 ↓
    │
    ├── 有明确的前后阶段依赖吗？
    │   ├── 是 → Pipeline 串行（研究→实现→验证）
    │   └── 否 ↓
    │
    └── 需要不同专业视角把关吗？
        ├── 是 → 专职审查代理（安全 + 性能，只读，并行）
        └── 否 → 单代理可能已经够用
```

记忆口诀：

> **任务够大，边界够清，独立就并行，依赖就串行，验收要独立，合并靠人拍板。**

---

## 十六、核心 Takeaways

1. **一条完整流水线 = 研究 → 实现 → 验证。**  
   研究员探索、施工员写码、安全 + 性能审查员并行把关，父代理汇总。

2. **专职代理定义在 `.claude/agents/*.md`（或 `.codex/*.toml`、`.pi/*.md`）。**  
   每个文件 = 身份证（frontmatter）+ 岗位职责（正文）。

3. **工作流写进 `CLAUDE.md` / `AGENTS.md`，保证全队一致。**  
   它是《操作规程》，一次约定、长期生效。

4. **权限最小化是关键设计：只有施工员能写，其余全只读。**  
   审查员只读，才不会一边检查一边改证据，也不会互相覆盖。

5. **Fan-Out 用于独立并行，Pipeline 用于依赖串行。**  
   后一步要不要前一步结果，决定串行还是并行。

6. **委派 ≠ 自动化。**  
   会思考、要判断的交给子代理；机械重复的交给 hooks / 扩展 / CI。别用 hooks 去“驱动”子代理编排。

7. **AI 不擅自合并，最终由人拍板。**  
   流水线产出结构化报告，人在回路做决策。

---

## 十七、今日面试题

### Q1：请描述“研究 → 实现 → 验证”流水线的四个角色及其权限。

**参考答案**：

- researcher（研究员）：Read/Grep/Glob，只读，摸清现有代码结构与模式；
- implementer（施工员）：Read/Write/Glob/Bash，唯一可写可执行，负责写代码和测试；
- security-reviewer（安全审查）：Read/Grep，只读，查漏洞（数据泄露、注入等）；
- performance-reviewer（性能审查）：Read/Grep，只读，查性能瓶颈并给优化建议。

---

### Q2：为什么审查员必须只读，只有施工员能写？

**参考答案**：

若审查员能写代码，会带来两个问题：一是它可能一边检查一边修改证据，导致审查结果不稳定；二是多个审查员可能并行修改同一文件产生冲突。只让施工员拥有写权限，符合最小权限原则，也保证审查阶段绝不改动代码，风险可控。

---

### Q3：安全审查和性能审查为什么可以并行，而研究和实现却要串行？

**参考答案**：

安全和性能关注点不同、彼此没有数据依赖，可以同时进行（Fan-Out），节省时间。而实现必须基于研究结果，后一步依赖前一步的输出，属于典型的 Pipeline，必须串行。判断标准就是：后一步是否需要前一步的结果。

---

### Q4：`CLAUDE.md` 在这条流水线里起什么作用？它是硬触发器吗？

**参考答案**：

`CLAUDE.md` 记录团队级工作流（何时研究、何时实现、合并前必须并行审查等），保证全队按同一流程干活。但它是给代理的**行为指导**，不是每次必然执行的硬触发器。若某项检查必须每次发生，应交给 hooks / CI 等确定性机制。

---

### Q5：想“每次改文件后自动跑测试”，应该用子代理还是 hooks？为什么？

**参考答案**：

应该用 hooks（如 Claude Code 的 `PostToolUse` 匹配 `Write|Edit` 后执行检查脚本）。因为这是“固定动作、无需思考”的机械自动化，用 hooks 又快又稳。子代理是用来做需要判断和思考的委派任务的，不该拿来做机械重复的事，二者不能混用。

---

### Q6：为什么流水线最后一步不是让 AI 自动合并，而是报告给用户？

**参考答案**：

这是刻意设计的“人在回路（human in the loop）”。审查结论可能包含风险与建议（如需加限流、需缓存元数据），是否可接受、是否合并应由人做最终判断。AI 负责把结构化报告摆清楚，人负责拍板，避免绕过人类决策。

---

## 十八、一句话总结

> **多智能体工作流的精髓，不是“多叫几个 AI”，而是把一个任务拆成分工明确、权限最小、边界清晰的角色——研究、实现、验证各司其职，独立就并行、依赖就串行，最后由父代理汇总、由人拍板。**

Claude Code、Codex、Pi 的配置格式不同，但共享同一套工程原则：**清晰分阶段、专职代理、最小权限、结构化汇报、委派与自动化分离**。

---

## 十九、参考资料

- Hugging Face Context Course — Hands-On: Multi-Agent Workflow：https://huggingface.co/learn/context-course/unit4/hands-on
- GitHub 原文：https://github.com/huggingface/context-course/blob/main/units/en/unit4/hands-on.mdx
