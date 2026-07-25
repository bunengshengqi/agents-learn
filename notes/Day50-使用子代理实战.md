# Day 50：在 Claude Code、Codex 与 Pi 中使用子代理

**课程来源**：Hugging Face Context Course — Unit 4: Using Subagents  
**原文链接**：https://huggingface.co/learn/context-course/unit4/using-subagents  
**GitHub 地址**：https://github.com/huggingface/context-course/blob/main/units/en/unit4/using-subagents.mdx  
**学习日期**：2026-07-25

---

## 一、这节课到底要学什么？

前两天我们已经学过：

- Day 48：子代理是什么、为什么需要子代理；
- Day 49：Fan-Out/Fan-In、Pipeline、Supervisor、Swarm 四种常见模式；
- Day 50：真正把子代理用起来。

> **这节课的重点不是再讲“子代理是什么”，而是学习如何在 Claude Code、Codex 和 Pi 中创建、调用、管理子代理。**

你可以把前两天理解成“学习组织管理理论”，今天则是“第一次真正带团队干活”。

读完本课，你应该能够回答以下问题：

1. 怎样用一句自然语言让父代理拆分任务并调用多个子代理？
2. 怎样创建一个拥有固定职责和工具权限的专业子代理？
3. 怎样查看子代理的执行状态与结果？
4. 多个子代理并行修改代码时，怎样避免文件冲突？
5. Claude Code、Codex 和 Pi 的子代理机制有什么区别？

---

## 二、先复习最重要的模型：Fan-Out / Fan-In

子代理最常见的工作方式是 **Fan-Out / Fan-In（分发—聚合）**。

```text
                     ┌── 子代理 A：研究框架 A ──┐
用户任务 → 父代理 ───┼── 子代理 B：研究框架 B ──┼→ 父代理汇总 → 最终答案
                     ├── 子代理 C：研究框架 C ──┤
                     └── 子代理 D：研究框架 D ──┘
```

整个过程分为四步：

1. **识别任务**：父代理判断任务能否拆成互相独立的部分；
2. **Fan-Out**：把不同部分分发给多个子代理；
3. **独立执行**：每个子代理在自己的上下文窗口中工作；
4. **Fan-In**：父代理收集结果、解决冲突、形成统一结论。

### 为什么最终汇总必须由父代理负责？

因为各个子代理只看到自己负责的一小块，它们可能：

- 使用不同的评价标准；
- 得出彼此矛盾的结论；
- 重复报告同一个问题；
- 缺少整个任务的全局背景。

因此，子代理交回来的不是“最终答案”，而是供父代理使用的**证据和中间结果**。

一个高质量的子代理报告最好包含：

```text
- Findings：发现了什么
- Sources：证据来自哪些文件、哪些行或哪些网页
- Confidence：对结论有多大把握
- Recommendations：建议父代理接下来怎么做
```

> **子代理负责把局部看深，父代理负责把全局看清。**

---

## 三、Claude Code：最简单的调用方式是直接说人话

在 Claude Code 中，最容易上手的方法不是先写配置，而是直接用自然语言描述你希望怎样分工。

例如：

```text
请比较 5 个主流机器学习框架。
为每个框架启动一个独立的子代理并行研究，
最后汇总它们的优点、缺点、适用场景和学习成本。
```

父代理可以据此：

1. 创建 5 个子代理；
2. 给每个子代理分配一个框架；
3. 让它们并行研究；
4. 等待研究结果返回；
5. 去重、比较并整理成最终表格。

### 好提示词的三个要素

#### 1. 明确说明要拆分

```text
把这项任务拆成 4 个互相独立的子任务。
```

#### 2. 明确说明是否并行

```text
这些子任务彼此独立，请并行执行。
```

#### 3. 明确说明父代理如何汇总

```text
等所有子代理完成后，请比较结论、消除重复项，
并按严重程度输出统一报告。
```

一个更完整的模板如下：

```text
请使用子代理完成以下任务：<总任务>。

分工要求：
1. 子代理 A：<职责 A>
2. 子代理 B：<职责 B>
3. 子代理 C：<职责 C>

执行要求：
- 三项任务互相独立，请并行执行；
- 每个子代理必须报告证据来源和置信度；
- 子代理不要直接修改文件，只做只读分析；
- 最后由父代理去重、解决冲突并给出统一结论。
```

### 初学者常见误区

不要只说：

```text
帮我检查一下这个项目。
```

这句话太宽泛。父代理不知道：

- 检查什么方面？
- 是否需要子代理？
- 每个子代理负责什么？
- 最终结果以什么格式呈现？

更好的说法是：

```text
请并行启动三个只读子代理：
一个检查安全问题，一个检查性能问题，一个检查测试覆盖率。
每个结论必须给出文件路径和行号，最后按严重程度汇总。
```

---

## 四、Claude Code：创建可复用的自定义子代理

自然语言适合临时任务。如果某类角色经常出现，例如研究员、架构师、安全审查员，就可以把它定义为一个**自定义代理（Custom Agent）**。

项目级代理通常放在：

```text
.claude/agents/
```

例如，新建 `.claude/agents/researcher.md`：

```markdown
---
name: researcher
description: Research-focused agent for deep file exploration
tools: Read, Grep, Glob, WebFetch
model: sonnet
---

You are an expert researcher.

Your job is to investigate the assigned topic and return:
1. Key findings
2. Source files and line numbers
3. Confidence level
4. Open questions

Do not modify files.
```

### 这个文件由两部分组成

#### 1. YAML Frontmatter：代理的“员工档案”

```yaml
name: researcher
description: Research-focused agent for deep file exploration
tools: Read, Grep, Glob, WebFetch
model: sonnet
```

它说明：

| 字段 | 作用 | 通俗理解 |
|---|---|---|
| `name` | 代理名称 | 员工姓名 |
| `description` | 适合处理什么任务 | 岗位说明 |
| `tools` | 允许使用哪些工具 | 门禁卡能打开哪些门 |
| `model` | 使用哪个模型 | 给员工配置哪种“大脑” |

#### 2. 正文：代理的系统指令

Frontmatter 下面的正文定义代理的行为方式，例如：

- 它扮演什么角色；
- 工作目标是什么；
- 输出格式是什么；
- 哪些事情不能做；
- 发现不确定信息时怎样处理。

### 为什么审查代理最好只读？

假设安全审查代理既能发现问题，又能直接修改代码，就会出现两个问题：

1. 它可能一边检查一边改变证据，导致审查结果不稳定；
2. 多个审查代理可能同时修改同一个文件，产生冲突。

因此，安全审查员、架构审查员、代码评审员通常只需要：

```text
Read、Grep、Glob
```

而不应获得写文件或执行危险命令的权限。

> **权限要遵循最小权限原则：完成任务需要什么，就只给什么。**

### 三个常见专业角色

```text
.claude/agents/
├── researcher.md          # 查资料、读文件、整理证据
├── architect.md           # 分析架构、模块边界和设计取舍
└── security-reviewer.md   # 只读检查安全问题
```

不要为了“看起来专业”创建十几个几乎用不到的角色。先从高频角色开始，等职责确实稳定后再固化。

---

## 五、用 CLAUDE.md 写团队级的委派规则

如果只是偶尔创建子代理，自然语言提示已经足够；如果整个团队希望始终遵守同一种委派方式，可以在 `CLAUDE.md` 中写规则。

例如：

```markdown
## Code Review Policy

- Changes under `auth/` must be reviewed by a read-only security reviewer.
- The reviewer must report file paths, line numbers, severity, and evidence.
- The parent agent resolves conflicts and writes the final review.

## Research Policy

- When a task requires reading more than 10 files, split the repository by subsystem.
- Assign one read-only subagent to each subsystem.
- Run independent investigations in parallel.
```

这相当于给团队写了一本“员工手册”：

- 什么情况下应该委派；
- 应该找哪类子代理；
- 子代理能使用哪些工具；
- 应该返回什么格式的结果。

### 一个必须记住的限制

> **CLAUDE.md 中的策略是对代理的指导，不是百分之百保证执行的硬触发器。**

同样，Claude Code 的 Hook（例如 `PostToolUse`）本身也不会自动帮你创建子代理。不要把下面两件事混为一谈：

| 机制 | 主要作用 |
|---|---|
| `CLAUDE.md` | 给代理提供项目规则和工作指导 |
| Hooks | 在特定生命周期事件发生时执行确定性的脚本或检查 |
| Subagents | 由父代理委派任务、独立工作并返回结果 |

如果你必须确保某个检查每次都执行，应该使用确定性的 Hook 或 CI；如果你希望代理根据任务语义灵活决定是否委派，可以把策略写进 `CLAUDE.md`。

---

## 六、Skills 与 Subagents 是什么关系？

**Skill** 是一套可复用的工作流程或领域知识，**Subagent** 是一个拥有独立上下文的执行者。

生活类比：

- 子代理 = 新来的员工；
- Skill = 员工可以翻阅的标准作业手册（SOP）。

例如，研究代理可以使用以下 Skills：

```text
hf-api-search
hf-dataset-fetch
```

这样它不仅知道“要研究 Hugging Face 数据集”，还知道应该按照什么步骤查询 API、获取数据并整理结果。

### 两者的区别

| 对比项 | Subagent | Skill |
|---|---|---|
| 本质 | 独立执行者 | 可复用流程/知识包 |
| 上下文 | 通常有自己的上下文窗口 | 加载到执行它的代理上下文中 |
| 用途 | 隔离任务、并行执行、专业分工 | 规范步骤、复用经验、减少重复提示 |
| 类比 | 员工 | 操作手册 |

它们不是竞争关系，而是组合关系：

```text
父代理
  └── 研究子代理
        ├── 使用 hf-api-search Skill
        └── 使用 hf-dataset-fetch Skill
```

---

## 七、后台执行与任务管理

当一个子代理运行时间较长时，不一定要让整个交互停在那里等待。

在 Claude Code 中，可以使用：

- **`Ctrl+B`**：把正在运行的任务移到后台；
- **`/tasks`**：查看后台任务，并重新进入相应任务。

可以把它理解为：

```text
前台 = 你正盯着员工工作
后台 = 员工继续干活，你先处理别的事
/tasks = 查看所有员工的任务看板
```

### 什么时候适合放到后台？

- 阅读大量文档；
- 扫描大型仓库；
- 运行耗时测试；
- 等待多个独立研究任务完成。

### 什么时候不适合？

- 子代理马上就会返回；
- 父代理下一步必须依赖它的结果；
- 执行过程中很可能需要你及时授权或决策。

后台执行不会改变依赖关系。如果任务 B 必须使用任务 A 的输出，那么把 A 放到后台也不能让 B 提前开始。

---

## 八、Claude Code 示例：Research → Review 流水线

假设任务是：调查项目的身份认证实现，并给出安全改进建议。

可以设计为：

```text
阶段 1：Research
  ├── 子代理 A：调查登录流程
  ├── 子代理 B：调查 Token 生命周期
  └── 子代理 C：调查权限校验

阶段 2：Review
  └── 安全审查代理检查三份研究结果

阶段 3：Synthesis
  └── 父代理去重、解决冲突、输出最终建议
```

这里实际上组合了两种模式：

1. 阶段 1 内部使用 **Fan-Out/Fan-In**，三个研究任务并行；
2. 阶段 1 → 阶段 2 → 阶段 3 使用 **Pipeline**，后一步依赖前一步。

可以这样向 Claude Code 描述：

```text
请分析这个项目的身份认证系统。

第一阶段并行启动三个只读研究子代理：
1. 调查登录和会话建立流程；
2. 调查 Token 的创建、刷新和失效；
3. 调查角色与权限校验。

每个代理必须返回文件路径、行号、证据和置信度。
研究完成后，再启动一个只读安全审查代理交叉检查三份结果。
最后由父代理输出统一报告，不要直接修改代码。
```

这个提示比“帮我看一下认证系统”可靠得多，因为它定义了：

- 分工；
- 并行关系；
- 权限；
- 输出契约；
- 汇总责任。

---

## 九、Codex：通过自然语言显式创建子代理

Codex 也支持子代理，但操作方式和 Claude Code 不完全相同。

### 1. 子代理通过自然语言请求创建

例如：

```text
Spawn one agent per item in this list, run them in parallel,
and combine the results into a comparison table.
```

一个重要事实是：

> **Codex 没有一个单独的 `codex-agent` 二进制程序，也不是靠特殊 CLI 命令创建子代理；它根据自然语言中的明确请求创建子代理。**

因此，提示词里最好明确出现：

- spawn agents；
- one agent per item；
- run in parallel；
- combine results。

### 2. Codex 的三种内置代理类型

| 类型 | 适用场景 | 通俗理解 |
|---|---|---|
| `default` | 通用任务 | 全能员工 |
| `worker` | 执行和实现任务 | 开发工程师 |
| `explorer` | 大量读取、搜索、理解代码库 | 代码侦察员 |

如果任务主要是读代码和找证据，优先选择 `explorer`；如果任务是根据清晰计划实现功能，则更适合 `worker`。

---

## 十、Codex：全局并发与深度配置

Codex 可以在 `codex.toml` 中配置子代理系统，例如：

```toml
[agents]
max_threads = 8
max_depth = 1
job_max_runtime_seconds = 3600
```

字段含义：

| 字段 | 含义 | 为什么需要限制 |
|---|---|---|
| `max_threads` | 最多同时运行多少个代理线程 | 防止并发过多、消耗失控 |
| `max_depth` | 子代理继续创建下级代理的最大深度 | 防止代理无限套娃 |
| `job_max_runtime_seconds` | 单个任务允许运行的最长时间 | 防止任务永久卡住 |

### 什么叫“深度”？

```text
深度 0：父代理
  └── 深度 1：子代理
        └── 深度 2：孙代理
              └── 深度 3：曾孙代理……
```

如果 `max_depth = 1`，通常意味着只允许父代理创建一层子代理，子代理不能继续无限扩张。

> **更多代理不等于更好。并发越大，成本、冲突、汇总难度和失败概率也可能越高。**

---

## 十一、Codex：创建自定义代理类型

Codex 的自定义代理通常使用 TOML 配置。例如 `.codex/agents/pr_explorer.toml`：

```toml
name = "pr_explorer"
description = "Maps the codebase and gathers evidence for PR reviews"
nickname_candidates = ["Scout", "Mapper"]
sandbox_mode = "read-only"
developer_instructions = """
Explore the relevant code paths without modifying files.
Return findings with file paths, line numbers, and evidence.
Separate confirmed facts from assumptions.
"""
```

另一个文档研究代理可以写成：

```toml
name = "docs_researcher"
description = "Researches official documentation and summarizes evidence"
sandbox_mode = "read-only"
developer_instructions = """
Prefer primary documentation.
Record source URLs for every important claim.
Report uncertainty and conflicting sources explicitly.
"""
```

常见字段包括：

| 字段 | 说明 |
|---|---|
| `name` | 代理类型名称 |
| `description` | 什么时候适合调用它 |
| `developer_instructions` | 代理必须遵守的工作指令 |
| `nickname_candidates` | 可选昵称 |
| `model` | 可选模型配置 |
| `sandbox_mode` | 沙箱权限，例如 `read-only` |
| `mcp_servers` | 可使用的 MCP 服务 |
| `skills.config` | 可加载的 Skill 配置 |

配置专业代理时，仍然要遵循三个原则：

1. **职责要窄**：`review everything` 不如 `review authentication security`；
2. **权限要小**：评审代理尽量设为 `read-only`；
3. **输出要结构化**：要求路径、行号、证据、严重程度和置信度。

---

## 十二、Codex：用 `/agent` 管理子代理

Codex 的 `/agent` 命令可以用来查看和管理代理线程。

你可以把它理解成一个“团队线程列表”：

- 查看哪些代理正在运行；
- 进入某个代理线程；
- 阅读当前进度；
- 用自然语言继续指导某个代理。

这和只看最终结果不同。对于耗时任务，中途观察可以帮助你发现：

- 子代理理解错了范围；
- 子代理卡在授权请求上；
- 某个任务已经没有继续运行的价值；
- 需要补充更明确的约束。

但是，不要频繁打断每个子代理。好的父代理应该在一开始就给出清晰的任务边界和输出契约。

---

## 十三、Codex：沙箱与审批如何继承？

Codex 子代理会继承父代理的沙箱和审批环境。

例如，如果父代理运行在权限很宽的模式下，那么子代理也可能获得相应权限；如果父代理受到只读沙箱限制，子代理也会受到相应约束。

这意味着：

> **启动父代理时授予的权限，可能不只是给一个代理，而是间接给整个子代理团队。**

因此要谨慎使用权限过宽的运行方式。尤其不能因为“子代理只是辅助角色”就默认它没有操作风险。

如果某个非当前线程中的子代理需要审批，请求会被带回父代理侧，供用户处理。

### 安全建议

- 研究和评审任务优先使用只读沙箱；
- 不要给不需要写权限的代理开放写权限；
- 高风险命令仍应由用户明确审批；
- 不要在多个代理间共享不必要的密钥和敏感信息。

---

## 十四、Codex：CSV 批处理——一行数据一个代理

当任务天然是一张表时，可以使用 `spawn_agents_on_csv` 批量创建子代理。

例如，有一个模型列表：

```csv
model_id,task,dataset
model-a,text-classification,dataset-1
model-b,summarization,dataset-2
model-c,translation,dataset-3
```

希望每一行都由独立代理评估，就可以配置：

```text
csv_path: models.csv
instruction: Evaluate {model_id} on {dataset} for {task}
id_column: model_id
output_schema: <结构化结果定义>
output_csv_path: evaluation_results.csv
max_concurrency: 4
max_runtime_seconds: 1800
```

### 它在做什么？

```text
models.csv
  ├── 第 1 行 → 子代理 A → 结果 A ──┐
  ├── 第 2 行 → 子代理 B → 结果 B ──┼→ evaluation_results.csv
  └── 第 3 行 → 子代理 C → 结果 C ──┘
```

其中 `{model_id}`、`{dataset}`、`{task}` 是列占位符。每个子代理拿到当前行的数据后执行同一套指令。

### 一个关键规则

> **每个 worker 必须且只能调用一次 `report_agent_job_result`。**

为什么？因为批处理系统需要明确知道：

- 这一行任务是否已经完成；
- 最终结果是什么；
- 应该把哪份结果写回输出 CSV。

如果一次都不报告，这一行永远像“未完成”；如果报告多次，系统无法判断哪一个才是最终结果。

### 适用场景

- 批量评测模型；
- 批量检查 URL；
- 批量分析日志文件；
- 一条工单一个代理；
- 一家竞品一个研究代理。

### 不适用场景

如果第 2 行必须使用第 1 行的结果，这就不是独立行任务，不适合直接并行批处理，更适合 Pipeline。

---

## 十五、Pi：子代理由扩展提供

Pi 与 Claude Code、Codex 最大的区别是：

> **Pi 的子代理不是默认内置能力，而是通过 subagent 扩展提供。**

课程给出的目录结构类似：

```bash
mkdir -p .pi/extensions/subagent .pi/agents .pi/prompts
```

这些目录分别承担：

```text
.pi/
├── extensions/subagent/  # 子代理扩展实现
├── agents/               # 自定义代理定义
└── prompts/              # 可复用工作流提示
```

Pi 的自定义研究代理可以写成：

```markdown
---
name: researcher
description: Research-focused agent for deep file exploration
tools: read, grep, find, ls
---

Investigate the assigned topic without modifying files.
Return key findings, evidence, and unresolved questions.
```

扩展加载后，可以通过自然语言把任务交给指定代理。每个子任务会在独立的 Pi 子进程和上下文中运行。

### Workflow Prompts

`.pi/prompts/` 中可以保存可复用的工作流提示，例如：

```text
/implement
/scout-and-plan
```

它们可以把一套经常重复的过程固定下来，例如：

```text
/scout-and-plan
  1. 先让侦察代理阅读代码库
  2. 再让规划代理生成实施方案
  3. 最后把方案交回父代理
```

### Pi 的核心特点

- 子代理能力由扩展提供，不是默认内置；
- 自定义代理放在 `.pi/agents/`；
- 工作流提示放在 `.pi/prompts/`；
- 每个子任务可运行在独立进程和独立上下文中；
- 具体工作流需要使用者自己调整。

---

## 十六、三种工具横向对比

| 对比项 | Claude Code | Codex | Pi |
|---|---|---|---|
| 子代理来源 | 内置 Agent 能力 | 通过自然语言显式创建 | 依赖 subagent 扩展 |
| 临时调用 | 自然语言委派 | 自然语言委派 | 扩展加载后自然语言委派 |
| 自定义代理位置 | `.claude/agents/*.md` | `.codex/agents/*.toml` 等配置 | `.pi/agents/*.md` |
| 内置代理类型 | 主要使用自定义角色 | `default`、`worker`、`explorer` | 无固定内置类型 |
| 任务管理 | `Ctrl+B`、`/tasks` | `/agent` | 依扩展与工作流而定 |
| 批量表格任务 | 可自行组织并发 | `spawn_agents_on_csv` | 需自行设计 |
| 隔离方式 | 可结合 Git worktree | 沙箱与审批继承父代理 | 独立 Pi 子进程 |

不需要死记所有配置语法。真正应该掌握的是共同思想：

1. 把任务边界说清楚；
2. 只并行真正独立的工作；
3. 给每个代理最小必要权限；
4. 让结果带上证据和置信度；
5. 最终由父代理统一判断。

---

## 十七、Worktree Isolation：并行写代码怎样避免打架？

如果多个子代理都只读文件，通常不会有 Git 冲突；但如果多个子代理需要并行修改代码，就可能互相覆盖。

错误示例：

```text
同一个项目目录
├── 子代理 A 正在修改 app.py
└── 子代理 B 也在修改 app.py
```

可能发生：

- A 的修改覆盖 B；
- B 读取到 A 改到一半的文件；
- Git diff 混在一起，无法区分是谁修改的；
- 测试结果对应不上正确代码版本。

解决方案是 **Git Worktree（工作树）隔离**。

```bash
git worktree add ../feature-a
git worktree add ../feature-b
```

概念上变成：

```text
主仓库
├── ../feature-a  → 子代理 A 的独立目录和分支
└── ../feature-b  → 子代理 B 的独立目录和分支
```

每个子代理在自己的目录中修改和测试，完成后再由父代理检查并合并结果。

### Worktree 不等于“自动没有冲突”

Worktree 解决的是**工作过程互相干扰**的问题。如果两个代理最终都修改了同一段代码，合并时仍然可能出现冲突。

因此最佳做法是：

1. 尽量让不同子代理负责不同文件或模块；
2. 必须改同一模块时，优先改为串行；
3. 并行编辑时使用独立 worktree；
4. 合并前分别运行测试；
5. 最终由父代理或人类审查合并结果。

> **Worktree 是给每个开发者一张独立办公桌，不是让两个人写同一行代码时自动达成一致。**

---

## 十八、真实案例：支付系统代码审查

任务：检查支付系统中的安全问题和性能问题。

### 方案设计

```text
                        ┌── 安全审查代理（只读）
支付系统 → 父代理 ──────┤   - SQL 注入
                        │   - Token 泄露
                        │   - 权限提升
                        │
                        └── 性能审查代理（只读）
                            - 慢查询
                            - N+1 查询
                            - 缓存缺失
                                 │
                                 ▼
                         父代理统一去重和定级
                                 │
                                 ▼
                           最终审查报告
```

### 为什么应该并行？

安全审查和性能审查的关注点不同，彼此通常没有数据依赖，可以同时进行。

### 为什么应该使用专业代理？

- 安全代理有专门的漏洞检查清单；
- 性能代理关注查询次数、复杂度和缓存；
- 两者不会因为关注范围过大而遗漏细节。

### 为什么必须由父代理汇总？

某个问题可能同时影响安全和性能，例如不受限制的批量查询：

- 性能代理认为它会造成数据库压力；
- 安全代理认为它可能导致越权读取大量数据。

父代理不能简单删除“重复项”，而应该把两个角度合并成一个更完整的问题说明。

### 推荐输出格式

```markdown
## [High] 支付记录接口缺少商户级权限过滤

- 文件：src/payments/api.py:87
- 安全影响：攻击者可能读取其他商户的交易记录
- 性能影响：无范围限制的查询可能扫描大量数据
- 证据：<相关代码与数据流>
- 置信度：高
- 建议：增加商户范围过滤、索引与分页限制
```

这就是结构化结果的价值：父代理更容易比较、去重和排序。

---

## 十九、实践中的最佳做法

### 1. 先用自然语言，重复出现后再固化配置

不要一开始就创建大量代理文件。先观察哪些角色真的高频出现，再把稳定角色写入 `.claude/agents/`、`.codex/agents/` 或 `.pi/agents/`。

### 2. 子任务必须有清晰边界

差的任务：

```text
研究整个项目。
```

好的任务：

```text
只分析 src/auth/ 下的 Token 创建、验证和刷新流程；
不要分析前端，不要修改文件。
```

### 3. 并行只适用于独立任务

如果 B 依赖 A 的结果，就应该等待 A 完成，而不是盲目并行。

### 4. 审查代理默认只读

让评审者修改代码，会把“发现问题”和“解决问题”混在一起。先报告、再由父代理决定是否修复，通常更安全。

### 5. 要求证据，不只要结论

```text
❌ 认证代码可能有问题。
✅ src/auth/token.py:42 未检查 token audience，可能接受发给其他服务的 token。
```

### 6. 由父代理处理冲突

不要要求子代理彼此直接争论到得出最终答案。父代理掌握全局任务和评价标准，应该承担最终决策责任。

### 7. 控制并发、时间与成本

不要为了一个小任务启动十个代理。并发会增加：

- Token 消耗；
- API 与工具调用压力；
- 权限审批次数；
- 结果去重难度；
- 失败和超时概率。

### 8. 并行修改使用隔离环境

优先让代理修改不同文件；确实需要并行编码时，使用 Git worktree 或等价隔离机制。

---

## 二十、常见错误与纠正方法

| 错误做法 | 会发生什么 | 正确做法 |
|---|---|---|
| 为一个很小的任务创建多个代理 | 启动和汇总成本大于收益 | 父代理直接完成 |
| 没有定义子任务范围 | 多个代理重复阅读和重复报告 | 明确目录、主题和禁止范围 |
| 不限制评审代理权限 | 评审过程中意外修改代码 | 使用只读工具或只读沙箱 |
| 把强依赖任务硬并行 | 后续代理缺少前置结果 | 使用 Pipeline 串行阶段 |
| 多个代理在同一目录修改同一文件 | 覆盖、脏状态、测试失真 | 分文件或使用 worktree |
| 只要求“给结论” | 父代理无法核验 | 要求路径、行号、证据、置信度 |
| 直接拼接所有结果 | 重复、矛盾、标准不统一 | 父代理去重、验证、统一定级 |
| 认为 CLAUDE.md 是硬触发器 | 关键检查可能没有按预想启动 | 强制检查交给 Hook/CI，委派策略写 CLAUDE.md |
| 给父代理过宽权限后忽略继承 | 子代理也可能获得高权限 | 从父代理入口执行最小权限原则 |

---

## 二十一、如何判断要不要使用子代理？

可以使用下面的决策树：

```text
任务是否很小、几分钟内可完成？
├── 是 → 使用单代理
└── 否
    │
    ├── 能否拆成多个互不依赖的部分？
    │   ├── 是 → Fan-Out/Fan-In，并行子代理
    │   └── 否
    │
    ├── 是否有明确前后阶段？
    │   ├── 是 → Pipeline
    │   └── 否
    │
    ├── 是否需要不同专业视角？
    │   ├── 是 → 专业子代理 / Supervisor / Review
    │   └── 否 → 单代理可能已经足够
    │
    └── 是否需要多个代理并行写代码？
        ├── 是 → 分文件，并使用 worktree 隔离
        └── 否 → 只读并行通常更安全
```

记忆口诀：

> **任务要够大，边界要够清，工作要独立，结果要汇总。**

---

## 二十二、核心 Takeaways

1. **子代理最常见的执行形态是 Fan-Out/Fan-In。**  
   父代理分发独立任务，子代理并行执行，父代理最终聚合。

2. **Claude Code 可以直接通过自然语言调用子代理。**  
   高频专业角色可以定义在 `.claude/agents/*.md` 中。

3. **CLAUDE.md 适合记录委派策略，但不是保证自动创建子代理的硬触发器。**  
   Hooks 也不会天然替你创建子代理；确定性的强制检查应交给 Hook 或 CI。

4. **Skill 与 Subagent 可以组合使用。**  
   子代理是执行者，Skill 是它使用的标准流程和领域知识。

5. **Codex 通过自然语言显式请求创建子代理。**  
   它有 `default`、`worker`、`explorer` 三种内置类型，也支持 TOML 自定义代理。

6. **Codex 的沙箱和审批会从父代理继承。**  
   给父代理的权限可能影响整个代理团队，因此必须坚持最小权限。

7. **`spawn_agents_on_csv` 适合“一行数据一个独立任务”的批处理。**  
   每个 worker 必须且只能调用一次 `report_agent_job_result`。

8. **Pi 的子代理依赖扩展，不是默认内置能力。**  
   可通过 `.pi/agents/` 定义角色，通过 `.pi/prompts/` 固化工作流。

9. **多个子代理并行修改代码时要使用 worktree 等隔离机制。**  
   隔离可以避免工作过程互相覆盖，但最终合并仍可能产生语义或 Git 冲突。

10. **父代理不是转发器，而是团队负责人。**  
    它必须检查证据、解决矛盾、去除重复、统一标准并形成最终答案。

---

## 二十三、今日面试题

### Q1：什么是 Fan-Out/Fan-In？父代理在其中承担什么责任？

**参考答案**：

Fan-Out/Fan-In 是先把互相独立的任务分发给多个子代理并行执行，再把各自结果收回并聚合的模式。父代理负责划分任务、约束权限与输出格式，并在结果返回后核验证据、消除重复、处理冲突、统一评价标准，最终生成完整答案。

---

### Q2：Claude Code 中怎样创建一个可复用的专业子代理？

**参考答案**：

可以在 `.claude/agents/` 下创建 Markdown 文件。文件的 YAML Frontmatter 描述代理名称、用途、工具和模型，正文描述角色、工作规则、禁止事项和输出格式。研究或审查类代理应尽量只授予 Read、Grep、Glob 等只读工具。

---

### Q3：为什么说 CLAUDE.md 的委派策略不是硬触发器？

**参考答案**：

CLAUDE.md 是提供给代理的行为指导，代理会结合任务语义进行判断，但它不等同于每次必然执行的确定性程序。Hooks 也不会自动创建子代理。如果某项检查必须每次发生，应使用 Hook、测试或 CI 等确定性机制来强制执行。

---

### Q4：Codex 的 `worker` 和 `explorer` 有什么区别？

**参考答案**：

`worker` 更适合根据明确任务执行实现工作，`explorer` 更适合大量读取、搜索和理解代码库。评审和调研任务通常优先使用只读的 `explorer`，编码实现任务更适合 `worker`。

---

### Q5：什么任务适合使用 `spawn_agents_on_csv`？最重要的结果报告规则是什么？

**参考答案**：

它适合每一行都能独立处理的表格型批任务，例如一行一个模型、一行一个 URL 或一行一个工单。每个 worker 必须且只能调用一次 `report_agent_job_result`，让系统能够明确记录该行的唯一最终结果。

---

### Q6：为什么多个编码子代理需要 Git worktree？

**参考答案**：

多个代理在同一工作目录并行修改文件，可能互相覆盖、读取到中间状态，并让 Git diff 和测试结果混杂。Worktree 能给每个代理提供独立目录和分支，隔离修改过程。但如果多个代理最终修改同一段代码，合并时依然可能冲突，因此还应尽量按文件或模块划分任务。

---

### Q7：设计子代理时为什么要遵循最小权限原则？

**参考答案**：

子代理只应获得完成任务所需的工具和数据权限。权限过宽会增加误修改、敏感信息泄露和高风险命令执行的可能性。特别是在权限会从父代理继承的系统中，父代理入口的权限配置可能影响整个子代理团队。

---

### Q8：请为一次支付系统审查设计子代理分工。

**参考答案**：

可以并行启动两个只读代理：安全审查代理检查 SQL 注入、Token 泄露、越权和权限提升；性能审查代理检查慢查询、N+1 查询、索引和缓存缺失。每个代理返回文件路径、行号、证据、严重程度和置信度，最后由父代理合并重复问题、处理交叉影响并输出统一报告。

---

## 二十四、一句话总结

> **使用子代理的关键，不是“多叫几个人”，而是让正确的代理在清晰边界、最小权限和独立上下文中完成合适的任务，再由父代理负责任地汇总。**

Claude Code、Codex 和 Pi 的配置方式不同，但它们共享同一套工程原则：**合理拆分、独立并行、权限隔离、结构化汇报、统一决策**。

---

## 二十五、参考资料

- Hugging Face Context Course — Using Subagents：https://huggingface.co/learn/context-course/unit4/using-subagents
- GitHub 原文：https://github.com/huggingface/context-course/blob/main/units/en/unit4/using-subagents.mdx
