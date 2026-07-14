---
title: Day35 - SKILL.md 格式、目录结构、字段与编写原则
date: 2026-07-14
tags:
  - AI-Agent
  - Context-Engineering
  - Agent-Skills
  - SKILL-md
  - Progressive-Disclosure
  - HuggingFace-Context-Course
---

# 第35天：SKILL.md 格式、目录结构、字段与编写原则

> [!abstract] 本章定位
> 第35天继续学习 Hugging Face Context Course Unit 1。本章围绕 `SKILL.md` 的文件格式、目录结构、Frontmatter 字段、Body Content、文件引用和脚本设计展开，并区分三类容易混淆的信息：Agent Skills 开放规范的硬性要求、Hugging Face 课程的编写建议，以及不同 Agent 产品自己的实现约束。

## 0. 学习资料

- 在线教材：[The SKILL.md Format](https://huggingface.co/learn/context-course/unit1/skill-format)
- GitHub 原文：[skill-format.mdx](https://github.com/huggingface/context-course/blob/main/units/en/unit1/skill-format.mdx)
- 开放规范：[Agent Skills Specification](https://agentskills.io/specification)
- 技能校验工具：[skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref)

---

## 1. 本章一句话总结

```text
SKILL.md 不是一篇普通说明文，而是一个 Agent 可发现、可触发、可执行的任务说明入口；
Frontmatter 负责告诉 Agent“这是什么、什么时候用”，
Body 负责告诉 Agent“触发以后怎么做”，
scripts、references、assets 负责提供按需使用的执行代码、知识资料和输出素材。
```

一个 Skill 的完整工作过程可以概括为：

```text
扫描 name 和 description
→ 判断当前任务是否匹配
→ 加载 SKILL.md 的 Markdown 正文
→ 按需读取 references、运行 scripts、使用 assets
→ 执行任务并验证结果
```

这就是 Agent Skills 的“渐进式披露”（Progressive Disclosure）：不是一开始把所有内容都塞进上下文，而是用到哪一层，再加载哪一层。

---

## 2. 问题一：SKILL.md 格式是什么样的？

### 2.1 基本组成

一份标准 `SKILL.md` 由两部分组成：

```markdown
---
name: dataset-publishing
description: Publish datasets to Hugging Face Hub. Use when uploading datasets, creating dataset cards, or managing dataset versions.
---

# Dataset Publishing

## Workflow

1. Check authentication.
2. Validate the dataset.
3. Create the dataset card.
4. Upload and verify the result.
```

第一部分是 YAML Frontmatter，第二部分是 Markdown Body。

| 部分 | 主要作用 | Agent 何时读取 |
|---|---|---|
| YAML Frontmatter | 识别 Skill、判断是否触发 | Skill 发现阶段 |
| Markdown Body | 提供步骤、规则、示例和验收方式 | Skill 被触发后 |

### 2.2 Frontmatter 的边界

Frontmatter 必须：

1. 位于文件最顶部；
2. 用单独一行的 `---` 开始；
3. 用单独一行的 `---` 结束；
4. 中间使用合法 YAML；
5. 至少包含 `name` 和 `description`。

常见错误：

```yaml
# 错误：缺少结束分隔线
---
name: my-skill
description: Do something useful.

# 错误：冒号后的值破坏 YAML 结构
description: Use when: processing PDFs

# 推荐：有特殊标点时用引号包起来
description: "Process PDF files. Use when extracting text or merging documents."
```

### 2.3 最小可用 Skill

```text
text-cleaning/
└── SKILL.md
```

```markdown
---
name: text-cleaning
description: Clean and normalize text files. Use when removing duplicate whitespace, fixing line endings, or standardizing plain-text input.
---

# Text Cleaning

1. Inspect the input encoding and line endings.
2. Preserve meaningful paragraph boundaries.
3. Normalize repeated whitespace.
4. Save the result as UTF-8.
5. Compare the cleaned output with the original before delivery.
```

这已经是一份合法的最小 Skill。`scripts/`、`references/` 和 `assets/` 都不是必需的。

---

## 3. 问题二：目录结构是什么样的？

### 3.1 课程中的标准结构

```text
skill-name/
├── SKILL.md              # 必需：元数据和核心操作说明
├── scripts/              # 可选：可执行代码
│   ├── validate.py
│   └── deploy.sh
├── references/           # 可选：按需读取的文档和知识
│   ├── api-reference.md
│   └── examples.md
└── assets/               # 可选：模板、图片、配置、静态数据
    ├── template.yaml
    └── config-example.json
```

### 3.2 各结构分别解决什么问题？

| 结构 | 必需性 | 存放内容 | 核心问题 |
|---|---|---|---|
| `SKILL.md` | 必需 | 触发元数据、核心流程、规则、导航 | Agent 如何发现并使用该能力？ |
| `scripts/` | 可选 | Python、Bash、JavaScript 等可执行代码 | 哪些步骤需要稳定、重复、确定地执行？ |
| `references/` | 可选 | API 文档、Schema、政策、案例、详细指南 | Agent 在什么情况下需要补充知识？ |
| `assets/` | 可选 | 模板、图片、字体、配置样例、静态数据 | Agent 生成最终结果时需要使用什么素材？ |

### 3.3 `SKILL.md` 应该怎么写？

只放完成任务必需的核心内容：

- 任务的标准工作流；
- 关键决策规则；
- 必须遵守的限制；
- 输入、输出和验收标准；
- 何时读取某个 reference；
- 何时运行某个 script；
- 常见错误及恢复方式。

不要把所有背景资料都复制进来。`SKILL.md` 被触发后通常会整体进入上下文，正文越臃肿，Agent 留给真实任务的上下文就越少。

### 3.4 `scripts/` 应该怎么写？

适合放入脚本的任务通常具有以下特征：

- 同一段代码会反复生成；
- 结果必须稳定、可复现；
- 手工处理容易出错；
- 需要做机械转换、批量处理或格式校验；
- 语言推理不是任务的核心，计算和规则执行才是。

例如：

```text
scripts/
├── validate_dataset.py     # 验证字段、空值和数据类型
├── generate_card.py        # 根据固定模板生成模型卡
└── check_links.sh          # 检查文档中的链接
```

脚本需要做到：

1. 功能边界清楚；
2. 依赖自包含或写清楚；
3. 出错时给出有用的信息；
4. 处理常见边界情况；
5. 编写后真实运行和验证；
6. 不把密钥、令牌或环境专属绝对路径写死。

### 3.5 `references/` 应该怎么写？

`references/` 放的是“Agent 做任务时可能需要查询，但不必每次都读”的资料。

例如：

```text
references/
├── api-reference.md       # API 参数、返回结构和错误码
├── dataset-schema.md      # 字段定义和约束
├── publishing-policy.md   # 发布规范
└── troubleshooting.md     # 常见故障及恢复步骤
```

编写原则：

- 一个文件聚焦一个主题；
- 文件名要能看出内容；
- 在 `SKILL.md` 中写清楚何时读取；
- 避免同一内容在 Body 和 reference 中重复；
- 长文件应有目录，便于 Agent 快速定位；
- 避免 references 再引用更深层的 references，防止形成查找迷宫。

好的导航写法：

```markdown
Before calling the publishing API, read
[the API reference](references/api-reference.md).

If authentication fails, read
[the troubleshooting guide](references/troubleshooting.md).
```

### 3.6 `assets/` 应该怎么写？

`assets/` 不是知识说明书，而是产出过程中要直接复制、修改或嵌入的静态资源。

例如：

```text
assets/
├── report-template.docx
├── dataset-card-template.md
├── logo.png
├── brand-font.ttf
└── config-example.yaml
```

判断方法：

```text
Agent 需要阅读它来理解任务 → references/
Agent 需要执行它来完成任务 → scripts/
Agent 需要把它用于最终产出 → assets/
```

### 3.7 目录和文件名遵循什么规则？

Skill 根目录名称应当：

- 使用小写英文字母、数字和连字符；
- 长度为 1–64 个字符；
- 不能以连字符开头或结尾；
- 不能出现连续连字符；
- 与 Frontmatter 中的 `name` 完全一致。

```text
有效：dataset-publishing
有效：pdf2text
无效：Dataset-Publishing
无效：dataset_publishing
无效：-dataset
无效：dataset--publishing
```

所有相对路径都应从 Skill 根目录解析。这样整个文件夹移动到别处以后仍然能用。

### 3.8 能不能创建其他目录？

开放规范允许 Skill 包含额外文件和目录，但兼容性最好的做法仍然是优先使用约定结构。

只有当内容确实无法清楚归入 `scripts/`、`references/`、`assets/` 时，才考虑增加新目录；还要确认目标 Agent 是否支持。不要为了“看起来完整”提前创建空目录。

---

## 4. 问题三：Frontmatter、必填字段和可选字段分别是什么？

### 4.1 什么是 Frontmatter？

Frontmatter 是 Markdown 文件顶部用 YAML 表达的结构化元数据。

它不是正文简介，而是给 Agent 或 Skill 加载器读取的机器可解析信息。最重要的用途是：

```text
标识 Skill
→ 描述能力
→ 帮助 Agent 判断是否应该触发
→ 可选地声明许可证、环境要求和工具权限
```

### 4.2 开放规范中的必填字段

#### `name`

作用：Skill 的稳定标识符。

规则：

- 字符串；
- 1–64 个字符；
- 只使用小写字母、数字和连字符；
- 不能以连字符开头或结尾；
- 不能包含连续连字符；
- 必须与父目录名称一致。

#### `description`

作用：说明 Skill 做什么，以及什么时候使用。

规则：

- 非空字符串；
- 最多 1024 个字符；
- 同时写清“能力”和“触发场景”；
- 包含用户任务中可能出现的具体关键词；
- 最好用动作动词开头。

对比：

```yaml
# 太模糊，无法可靠触发
description: Helps with datasets.

# 更好：能力 + 使用场景 + 关键词
description: Publish datasets to Hugging Face Hub. Use when uploading datasets, creating dataset cards, validating dataset metadata, or managing dataset versions.
```

### 4.3 开放规范中的可选字段

| 字段 | 类型 | 作用 | 什么时候需要 |
|---|---|---|---|
| `license` | string | 声明 Skill 的许可证或许可证文件 | 需要分发、共享或限制使用时 |
| `compatibility` | string | 声明产品、系统包、网络或运行环境要求 | Skill 存在明确环境依赖时 |
| `metadata` | mapping | 保存规范之外的自定义字符串键值 | 需要作者、版本等管理信息时 |
| `allowed-tools` | string | 声明预批准工具 | 目标 Agent 支持且需要工具权限控制时 |

完整示例：

```yaml
---
name: dataset-publishing
description: Publish datasets to Hugging Face Hub. Use when uploading datasets, creating dataset cards, or managing dataset versions.
license: Apache-2.0
compatibility: Requires Python 3.8+, huggingface_hub, and network access.
metadata:
  author: ml-team
  version: "1.0.0"
allowed-tools: Bash(hf:*) Python(huggingface_hub:*)
---
```

注意：`allowed-tools` 仍是实验字段，不是所有 Agent 都支持。

### 4.4 必填与可选的判断依据是什么？

必须分三层判断：

1. **开放规范**：决定跨平台 Skill 的基本合法性；
2. **目标 Agent 的实现**：决定这个产品实际识别哪些字段；
3. **当前 Skill 的真实需要**：决定是否值得添加某个可选字段。

不能只因为字段“可以写”就全部写上。判断问题应该是：

```text
没有这个字段，Agent 是否无法发现、触发或正确运行 Skill？
目标 Agent 是否真的读取这个字段？
这个值是否真实、稳定、可维护？
```

### 4.5 一个重要的实现差异

Hugging Face 课程讲的是通用 Agent Skills Specification，因此列出了上述可选字段。不同产品可能采用更严格的子集。

例如，当前 Codex 的 `skill-creator` 约定 Frontmatter 只保留：

```yaml
---
name: my-skill
description: Describe what the skill does and when Codex should use it.
---
```

因此，真实编写时不能机械复制课程示例，应先检查目标 Agent 的官方说明和校验工具。通用规范回答“允许什么”，产品规范回答“这个 Agent 实际接受什么”。

---

## 5. 问题四：什么是 Body Content？

Body Content 是 Frontmatter 结束之后的全部 Markdown 正文。

它回答的不是“是否触发”，而是：

```text
Skill 已经被触发，现在 Agent 应该如何完成任务？
```

开放规范没有强制固定章节，但建议包括：

- 分步骤操作说明；
- 输入与输出示例；
- 决策规则；
- 常见边界情况；
- 错误处理；
- 文件和工具的使用方式；
- 交付前的验证标准。

### 5.1 推荐的正文骨架

```markdown
# Dataset Publishing

## Inputs

Confirm the dataset path, repository name, license, and visibility.

## Workflow

1. Check authentication.
2. Inspect the dataset format and schema.
3. Run `scripts/validate_dataset.py`.
4. Generate the dataset card from the template.
5. Upload the dataset.
6. Verify the repository and metadata.

## Decision Rules

- If the dataset contains personal data, stop and request a privacy review.
- If validation fails, do not upload.

## References

- Read [the schema guide](references/dataset-schema.md) when fields are unclear.
- Read [the API guide](references/api-reference.md) before changing upload behavior.

## Validation

- Confirm the repository is reachable.
- Confirm the dataset card renders.
- Confirm the declared license matches the data source.
```

### 5.2 Body 不是越详细越好

Body 应该“足够指导执行”，而不是“收录这个领域的全部知识”。Agent 触发 Skill 后通常会加载完整 Body，冗长内容会直接占用上下文。

因此：

```text
每次执行都必须知道的内容 → 留在 Body
只有特定条件下才需要的详细知识 → 放 references/
需要重复稳定执行的代码 → 放 scripts/
需要复制或用于最终结果的文件 → 放 assets/
```

---

## 6. 问题五：内容指南怎么理解？什么是技能中的文件参考？

### 6.1 内容指南的核心不是排版，而是降低 Agent 的执行成本

课程建议：

- 使用 `##` 和 `###` 形成清晰层级；
- 流程使用编号步骤；
- 前置条件使用检查清单；
- 命令和代码放进带语言标记的代码块；
- 示例应可复制运行，并且事先测试；
- 描述要具体，避免“处理一下”“正常执行”这类模糊表达；
- 把详细参考资料移出主文件；
- 用相对路径引用包内资源。

这些建议的共同目标是让 Agent 少猜、少搜索、少重复生成，并且能够验证结果。

### 6.2 文件参考是什么意思？

文件参考就是在 `SKILL.md` 中明确告诉 Agent：Skill 文件夹里还有哪些文件，以及在什么情况下读取、运行或使用它们。

它不是简单列出文件名，而是建立“任务条件 → 资源”的导航关系。

````markdown
For field definitions, read
[the dataset schema](references/dataset-schema.md).

Before uploading, run:

```bash
python scripts/validate_dataset.py data/my-dataset.csv
```

Create the final card from
[the dataset card template](assets/dataset-card-template.md).
````

三类引用分别表示：

| 引用 | Agent 的动作 |
|---|---|
| `references/dataset-schema.md` | 读取它，补充知识 |
| `scripts/validate_dataset.py` | 执行它，完成确定性操作 |
| `assets/dataset-card-template.md` | 复制或修改它，生成交付物 |

### 6.3 为什么必须使用相对路径？

推荐：

```markdown
[API guide](references/api-reference.md)
```

不推荐：

```markdown
/Users/alice/projects/my-skill/references/api-reference.md
```

相对路径以 Skill 根目录为基准，使 Skill 在移动、安装、打包或分享后仍然可用。

### 6.4 文件引用的原则

1. 从 `SKILL.md` 直接引用资源；
2. 尽量保持一层深度；
3. 不要让 reference A 再引向 B、B 再引向 C；
4. 写清楚“何时读”和“读完做什么”；
5. 定期检查引用文件是否真实存在；
6. 不要在多个文件中维护同一份真相。

---

## 7. 问题六：脚本是不是只能存在于 scripts/ 目录？

### 7.1 规范层面的答案

开放规范把 `scripts/` 定义为可执行代码的标准目录，同时也允许 Skill 包含额外文件或目录。因此从文件系统角度说，脚本并非“技术上只能”存在于 `scripts/`。

但从兼容性、可发现性和维护性来说：

```text
可复用的辅助脚本应放在 scripts/。
```

这是约定优于配置的体现。看到 `scripts/validate.py`，Agent 和维护者能立即判断它是可执行辅助程序。

### 7.2 哪些代码不一定放入 scripts/？

- 正文中的极短命令示例，可以直接放在代码块中；
- `assets/` 中的项目模板可能自带项目源代码，它们属于输出脚手架；
- reference 中可以有解释 API 用法的代码片段，但它们首先是文档示例；
- 用户项目自身的业务代码仍应留在用户项目中，不必全部搬进 Skill。

判断关键不在扩展名，而在用途：

```text
供 Agent 反复直接执行的辅助程序 → scripts/
用于解释概念的示例代码 → Body 或 references/
作为生成项目起点的样板代码 → assets/
用户真正维护的产品代码 → 用户项目目录
```

### 7.3 脚本设计原则

- 一个脚本解决一个清晰问题；
- 参数体现真正会变化的核心输入；
- 不把每个内部实现细节都暴露成命令行参数；
- 默认行为安全且合理；
- 错误消息说明原因和下一步；
- 必要时支持 `--help`；
- 输出应便于 Agent 判断成功或失败；
- 涉及副作用时提供预览、确认或幂等机制；
- 所有脚本都要经过实际运行测试。

---

## 8. 问题七：“脚本不需要过多参数”怎么理解？

课程原意可以拆成三层。

### 8.1 脚本首先是能力样板，不一定是面向所有人的永久 CLI 产品

Skill 里的脚本主要服务于 Agent。它需要把关键、容易出错的操作固化下来，让 Agent 可以直接运行，也可以在必要时读取并适配。

因此，初版脚本只要清楚表达核心功能即可，不必一开始设计几十个参数，试图覆盖所有未来情形。

### 8.2 参数越多，Agent 的决策负担越大

假设一个模型卡生成脚本暴露以下参数：

```text
--name
--description
--metrics
--license
--framework
--language
--tags
--citation
--limitations
--datasets
--widget
--pipeline-tag
--base-model
--library-name
```

Agent 不仅要理解所有参数，还要判断哪些必填、哪些冲突、哪些有默认值。大量参数会把“生成模型卡”变成“研究这个脚本的复杂接口”。

初版可以先抓核心变量：

```bash
python scripts/generate_card.py \
  --model-info model-info.json \
  --output README.md
```

把相关输入集中在结构化文件中，脚本负责稳定生成输出。遇到新要求时，Agent 可以修改输入文件、调整脚本，或根据核心逻辑生成一个任务专用版本。

### 8.3 “代理程序会重新生成脚本”不等于每次都应该重写

这句话不是说脚本可以随便写，也不是说 Agent 每次都必须重写脚本。

更准确的理解是：

```text
不要为了预测所有未来变化而过度设计通用接口；
先固化稳定核心，任务出现特殊需要时，再让 Agent 做局部适配。
```

优先顺序应当是：

1. 现有脚本和参数已经满足任务：直接运行；
2. 只是输入值变化：传入不同核心参数或配置文件；
3. 环境或任务有小差异：由 Agent 小范围修改；
4. 需求已经长期稳定且反复出现：再正式扩展脚本接口并补充测试。

### 8.4 “少参数”不是“把变量写死”

不好的极端：

```python
dataset_path = "/Users/alice/data/train.csv"
repo_id = "alice/my-dataset"
token = "hf_xxx"
```

合理做法：保留真正影响行为的核心输入，把稳定细节放入内部实现或配置。

```bash
python scripts/publish_dataset.py data/train.csv alice/my-dataset
```

是否增加参数，可以用三个问题判断：

1. 这个值是否会在不同任务中频繁变化？
2. 用户或 Agent 是否需要明确控制它？
3. 暴露它是否比使用安全默认值更清楚？

如果三个问题大多是否定的，就不要急着增加参数。

---

## 9. 规范、课程建议和产品实现必须分开看

| 问题 | 开放规范 | Hugging Face 课程建议 | 实际项目判断 |
|---|---|---|---|
| 最少需要什么？ | 根目录和 `SKILL.md` | 使用标准目录组织资源 | 先做最小可用版本 |
| 必填字段 | `name`、`description` | 描述以动词开头，写清使用时机 | 以目标 Agent 校验规则为准 |
| 可选字段 | `license`、`compatibility`、`metadata`、`allowed-tools` | 按示例合理补充 | 不要添加目标 Agent 不支持的字段 |
| 主文件长度 | 建议低于 500 行 | 课程页面写 400–800 行最大值 | 优先保持精简，接近 500 行就拆分 |
| 脚本长度 | 未规定统一硬上限 | 单个脚本建议低于 500 行 | 以职责单一、可测试为准 |
| Skill 总大小 | 未规定统一硬上限 | 建议低于 2 MB | 大资料尽量外置或按需获取 |
| 其他目录 | 允许 | 重点介绍三个标准目录 | 先考虑兼容性和必要性 |

> [!important] 如何处理“400–800 行”和“低于 500 行”的差异？
> 这两个数字都是编写建议，不是 YAML 格式的硬性语法限制。开放规范当前明确建议主 `SKILL.md` 低于 500 行，因此实践中应优先追求更短、更聚焦；课程中的 400–800 行可理解为“不要无限膨胀”的宽松上限，而不是写满 400 行的目标。

---

## 10. 一份真实 Skill 应该怎样从零编写？

### 第一步：先用真实请求定义触发边界

列出：

- 三个应该触发的用户请求；
- 三个不应该触发的用户请求；
- 任务需要什么输入；
- 最终必须交付什么结果。

### 第二步：提炼稳定工作流

把任务拆成：

```text
确认输入
→ 检查前置条件
→ 执行核心步骤
→ 处理异常
→ 验证结果
```

### 第三步：规划可复用资源

逐项判断：

```text
反复生成的确定性代码？ → scripts/
任务偶尔需要查询的知识？ → references/
交付时直接使用的模板或素材？ → assets/
每次执行都必须遵守的步骤？ → SKILL.md Body
```

### 第四步：先写 `name` 和 `description`

确保 description 同时覆盖：

- Skill 能做什么；
- 什么时候使用；
- 用户可能说出的关键词。

### 第五步：编写最短可执行 Body

优先写：

1. 输入确认；
2. 工作流程；
3. 关键决策；
4. 资源导航；
5. 错误处理；
6. 验收清单。

### 第六步：实现并测试脚本

不要只检查代码“看起来没问题”。必须用正常输入、错误输入和边界输入实际运行。

### 第七步：验证 Skill

通用规范可以使用：

```bash
skills-ref validate ./my-skill
```

目标 Agent 如果提供自己的验证器，还应再运行产品专用验证。

### 第八步：用真实任务迭代

观察：

- Skill 是否在正确场景触发；
- 是否误触发；
- Agent 是否能找到需要的文件；
- 步骤是否存在歧义；
- 脚本是否真的减少重复劳动；
- 最终结果是否通过验收。

---

## 11. 推荐模板

### 11.1 最小模板

```markdown
---
name: skill-name
description: Perform a specific task. Use when the user asks for specific trigger scenarios.
---

# Skill Title

## Workflow

1. Confirm required inputs.
2. Perform the task.
3. Validate the result.
```

### 11.2 带资源的实用模板

```markdown
---
name: skill-name
description: Perform a specific task. Use when the user mentions relevant files, tools, or outcomes.
---

# Skill Title

## Inputs

Confirm the required inputs before starting.

## Workflow

1. Inspect the input.
2. Read the relevant reference when required.
3. Run the helper script.
4. Review the generated output.
5. Validate the final result.

## Decision Rules

- If condition A applies, use approach A.
- If required information is missing, request it before taking an irreversible action.

## Resources

- Read [the API guide](references/api-reference.md) before using the API.
- Run `scripts/validate.py` before delivery.
- Use [the output template](assets/template.md) for the final artifact.

## Validation

- Confirm the output file exists.
- Confirm required fields are present.
- Confirm no errors were hidden or ignored.
```

---

## 12. 常见误区

### 误区一：把 description 写成一句空泛口号

`A useful writing skill` 无法形成可靠触发。description 必须包含能力、使用时机和任务关键词。

### 误区二：把“什么时候使用”只写在 Body

Agent 决定是否触发时通常还没有读取 Body，所以触发条件必须写进 description。

### 误区三：把所有知识都塞进 SKILL.md

这会破坏渐进式披露。详细知识应按主题放入 `references/`。

### 误区四：为了目录完整而创建空文件夹

可选目录只在确实有资源时创建。空目录不会提高 Skill 质量。

### 误区五：把 references 和 assets 混在一起

前者用于让 Agent 理解，后者用于生成最终产出。

### 误区六：脚本参数越多越专业

复杂参数会增加理解成本和组合错误。先暴露核心变量，再根据反复出现的真实需求扩展。

### 误区七：认为有脚本就不需要说明

`SKILL.md` 仍要说明何时运行、输入是什么、成功标准是什么、失败以后怎么办。

### 误区八：课程示例可以原样用于所有 Agent

开放规范、课程建议和产品实现可能不同。创建 Skill 前必须检查目标 Agent 的规则。

---

## 13. 最终检查清单

### 目录与命名

- [ ] Skill 目录名只使用小写字母、数字和连字符
- [ ] 目录名没有首尾连字符和连续连字符
- [ ] 根目录存在 `SKILL.md`
- [ ] `name` 与目录名完全一致
- [ ] 只创建真实需要的资源目录

### Frontmatter

- [ ] YAML 起止分隔线正确
- [ ] 包含合法的 `name`
- [ ] 包含具体的 `description`
- [ ] description 同时说明“做什么”和“什么时候使用”
- [ ] 可选字段符合目标 Agent 的支持范围

### Body

- [ ] 工作流可以直接执行
- [ ] 关键决策条件清楚
- [ ] 输入、输出和验收标准明确
- [ ] 不必要的背景材料已经移入 references
- [ ] 命令和代码示例可以复制运行

### 资源

- [ ] references 文件主题单一、按需读取
- [ ] scripts 职责清楚、错误信息有用
- [ ] scripts 已经真实运行测试
- [ ] assets 是实际用于输出的模板或素材
- [ ] 所有相对路径真实存在
- [ ] 没有写死密钥和个人绝对路径

### 验证

- [ ] 运行通用或产品专用校验器
- [ ] 测试应该触发的请求
- [ ] 测试不应该触发的请求
- [ ] 用至少一个真实任务检查最终交付质量

---

## 14. 本章结论

`SKILL.md` 的重点不是记住若干目录名，而是理解它背后的上下文工程：

```text
用 name + description 做低成本发现，
用 Body 提供触发后的核心工作流，
用 references 延迟加载详细知识，
用 scripts 固化重复且需要确定性的动作，
用 assets 提供最终产出所需素材。
```

高质量 Skill 的判断标准也不是“写得多”，而是：

```text
该触发时能触发，
触发后能少走弯路，
需要资料时找得到，
关键步骤执行稳定，
最终结果可以验证。
```
