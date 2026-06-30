---
title: Day 04｜内部推理与 ReAct 方法
date: 2026-06-20
tags:
  - AI-Agent
  - Thought
  - ReAct
  - Chain-of-Thought
  - Tool-Calling
  - Messages
  - Obsidian
status: in-progress
---
9
# Day 04｜内部推理与 ReAct 方法

## 一、今天的学习主题

Day 4 的核心主题是：

```text
思维机制：内部推理与 ReAct 方法
```

这一节主要讲两件事：

```text
1. Thought 是什么：内部推理、规划、分析、决策
2. ReAct 是什么：一种把“推理”和“行动”结合起来的方法
```

注意：

```text
内部推理 = Thought 这一环节本身
ReAct = 让 Thought 和 Action 配合起来的一种方法
```

Day 3 学的是完整循环：

```text
Thought → Action → Observation
```

Day 4 是把第一个环节 `Thought` 单独拿出来深入理解。

---

# 二、今天最重要的一句话

```text
Thought 是模型基于 messages 里的上下文，判断下一步该干什么。
```

Agent 的 Thought 不是凭空出现的。

它主要根据这些信息进行推理：

```text
system message：你是谁、你有哪些工具、你必须遵守什么规则
user message：用户当前要你做什么
assistant message：模型前面已经回答过什么
tool / observation message：工具刚刚返回了什么结果
```

这就和前面三天连接起来了：

```text
Day 1：LLM 能读文本、生成文本
Day 2：messages 保存上下文
Day 3：Agent 有 Thought → Action → Observation 循环
Day 4：深入理解 Thought 是怎么分析、规划、决策的
```

---

# 三、是不是根据 messages 的信息进行推理和规划

是的。

Agent 的 Thought 本质就是：

```text
模型读取当前 messages
→ 理解用户目标
→ 结合 system prompt 中的规则和工具说明
→ 判断下一步该做什么
```

例如 Day 3 的天气 Agent：

```text
用户：今天苏州天气怎么样？
```

模型看到：

```text
system 里说我有 get_weather 工具
user 问的是实时天气
```

于是 Thought 应该是：

```text
这是实时信息，我不能直接瞎答，应该调用 get_weather 工具。
```

这就是根据 `messages` 进行推理和规划。

---

# 四、Thought 不是最终答案

Thought 不是给用户看的最终答案。

Thought 是模型在行动前的分析过程。

用户最终看到的是：

```text
Final Answer
```

Agent 内部用来决定下一步的是：

```text
Thought
```

所以：

```text
Thought 负责想清楚下一步；
Action 负责调用工具；
Observation 负责接收工具结果；
Final Answer 负责回答用户。
```

---

# 五、图片一：常见思维模式怎么理解

图片一列的是 Agent 在 Thought 阶段常见的思维类型。

这些不是让你死记英文，而是让你理解：

```text
Thought 不是一句“我想一下”。
Thought 里面包含规划、分析、决策、反思、优先级排序等能力。
```

| 思维类型 | 中文 | 怎么理解 | 工程里的作用 |
|---|---|---|---|
| Planning | 规划 | 把大任务拆成几步 | 防止一上来乱干 |
| Analysis | 分析 | 根据已有信息判断原因 | 排查错误、分析问题 |
| Decision Making | 决策 | 在多个方案里选一个 | 推荐方案、选择工具 |
| Problem Solving | 问题解决 | 找出解决路径 | Debug、优化代码 |
| Memory Integration | 记忆整合 | 利用前文上下文 | 接上 Day 2 的 messages |
| Self-Reflection | 自我反思 | 发现上一步不行，换策略 | 工具失败后重试 |
| Goal Setting | 目标设定 | 明确完成标准 | 知道什么时候停 |
| Prioritization | 优先级排序 | 判断先做什么后做什么 | 复杂任务排顺序 |

---

## 用银行 RPA 场景理解这些思维模式

用户说：

```text
帮我检查这个客户有没有风险。
```

Agent 的 Thought 可能包含：

```text
Planning：我要分三步：查工商、查司法、查舆情。
Analysis：如果司法记录很多，风险可能偏高。
Decision Making：先查工商，因为这是基础信息。
Memory Integration：用户之前说这个客户是企业客户，不是个人客户。
Self-Reflection：如果工商接口失败，我应该换备用查询方式。
Goal Setting：最终要输出风险等级和人工复核建议。
Prioritization：先查强结构化数据，再查舆情。
```

这就是 Thought 在真实业务里的样子。

---

# 六、什么是 ReAct 方法

ReAct 来自两个词：

```text
Reasoning + Acting
推理 + 行动
```

它的核心思想是：

```text
不要让模型直接给最终答案。
让模型先推理，再行动，再根据结果继续推理。
```

最简单的人话：

```text
ReAct = 让模型边想边做。
```

不是：

```text
用户问 → 模型直接答
```

而是：

```text
用户问
→ Thought：我需要查什么？
→ Action：调用工具
→ Observation：看到工具结果
→ Thought：现在知道了什么？
→ Action 或 Final Answer
```

这正好就是 Day 3 的循环。

---

# 七、为什么要有 ReAct

早期很多 LLM 用法都是直接问答。

比如：

```text
问：一个杂耍演员有 16 个球，一半是高尔夫球，一半高尔夫球是蓝色，蓝色高尔夫球几个？
答：8
```

这个答案是错的。

正确过程是：

```text
总共有 16 个球
一半是高尔夫球，所以高尔夫球是 8 个
一半高尔夫球是蓝色，所以蓝色高尔夫球是 4 个
```

正确答案是：

```text
4
```

直接回答容易错，因为模型跳过了中间步骤。

后来大家发现，如果提示模型：

```text
Let's think step by step.
让我们一步一步思考。
```

模型更容易把问题拆开，错误率会下降。

但是，只让模型“逐步思考”还不够。

因为很多真实任务不是只靠脑子想就能完成，还需要：

```text
查资料
算数
读文件
调用 API
查询数据库
操作业务系统
```

于是就有了 ReAct：

```text
Reasoning：先想清楚
Acting：再调用工具行动
Observation：看工具结果
Reasoning：继续更新判断
```

---

# 八、图片二：Few-shot、CoT、Zero-shot-CoT 怎么理解

图片二讲的是：

```text
直接回答 vs 逐步思考
```

里面有几种情况：

| 名称 | 怎么理解 |
|---|---|
| Few-shot | 给几个例子，让模型模仿回答 |
| Few-shot-CoT | 给几个带推理过程的例子，让模型模仿逐步推理 |
| Zero-shot | 不给例子，直接让模型答 |
| Zero-shot-CoT | 不给例子，但加一句 Let's think step by step |

关键点是：

```text
即使你不给模型示例，只要加一句“让我们一步一步思考”，模型也更容易生成中间推理步骤。
```

这张图想说明：

```text
模型直接输出最终答案时容易犯错；
引导它分步骤推理，通常更稳。
```

---

# 九、CoT 和 ReAct 的区别

图片二更接近 CoT，也就是：

```text
Chain-of-Thought
思维链
```

CoT 的重点是：

```text
让模型一步一步推理。
```

ReAct 比 CoT 更进一步：

```text
让模型一边推理，一边行动。
```

关系是：

```text
CoT = Reasoning
ReAct = Reasoning + Acting
```

所以：

```text
CoT 更像“脑子里一步一步算”；
ReAct 更像“想一步，做一步，看结果，再想下一步”。
```

---

# 十、图片三：推理模型和 thought 标签怎么理解

图片三提到：

```text
DeepSeek R1
OpenAI o1
<thought> 和 </thought>
```

它想表达的是：

```text
近期很多推理模型会被训练成“先思考，再回答”。
```

一些训练数据或模型格式里，会用特殊标记区分：

```text
思考部分
最终回答部分
```

例如：

```text
<thought>
这里是模型的推理过程
</thought>

Final Answer:
这里是给用户看的最终答案
```

但工程上要注意：

```text
我们不一定需要、也不一定应该把完整内部思考都展示给用户。
```

实际产品里更常见的是让模型输出：

```text
简短计划
关键依据
下一步动作
最终结论
```

而不是把所有隐藏推理都暴露出来。

这对银行、金融、企业系统尤其重要，因为我们真正需要的是：

```text
可控
可审计
可复核
可追踪
```

而不是一大段不可控的内心独白。

---

# 十一、ReAct 和前三天的关系

## Day 1：LLM

```text
模型能理解文字，也能生成文字。
```

但它本身只是语言模型。

---

## Day 2：messages

```text
system / user / assistant / tool 都放进 messages。
模型每次根据 messages 生成下一步。
```

这是 Agent 的上下文基础。

---

## Day 3：Thought-Action-Observation

```text
模型先 Thought
再 Action 调工具
工具返回 Observation
模型再生成 Final Answer
```

这是 Agent 的执行循环。

---

## Day 4：ReAct

```text
让模型的 Thought 和 Action 交替进行。
不是一口气瞎答，而是边推理、边行动、边观察、边修正。
```

所以 ReAct 就是把前三天组合起来：

```text
LLM + messages + tools + loop = ReAct Agent
```

更工程化一点：

```text
messages 负责上下文
Thought 负责判断下一步
Action 负责调用工具
Observation 负责反馈现实结果
ReAct 负责把推理和行动串成一个可迭代流程
```

---

# 十二、ReAct 的工程意义

## 1. 防止模型瞎答

没有 ReAct：

```text
用户：今天苏州天气怎么样？
模型：今天苏州晴，28度。
```

这个答案可能是编的。

有 ReAct：

```text
Thought：这是实时天气，需要查工具。
Action：get_weather("苏州")
Observation：晴，28°C
Final Answer：苏州今天晴，28°C。
```

这样可靠性更高。

---

## 2. 让复杂任务可拆解

例如：

```text
生成企业风险报告
```

不能一步完成。

ReAct 会拆成：

```text
Thought：先查企业基本信息
Action：query_company_info

Observation：拿到企业信息

Thought：下一步查司法风险
Action：query_judicial_risk

Observation：拿到司法记录

Thought：继续查经营异常
Action：query_abnormal_operation

Observation：拿到异常记录

Final Answer：生成风险报告
```

这就是复杂任务工程化。

---

## 3. 让 Agent 可以纠错

比如工具失败：

```text
Observation：接口超时
```

Agent 可以继续：

```text
Thought：主接口失败，我应该尝试备用接口。
Action：query_backup_api
```

这就是自我反思和重试。

普通问答模型很难稳定做到这种流程控制。

---

## 4. 让过程可审计

对企业系统来说，不能只看最终答案。

还要知道：

```text
它为什么调用这个工具？
它传了什么参数？
工具返回了什么？
它基于什么结果做了判断？
```

ReAct 天然能留下过程日志：

```text
Thought
Action
Observation
Final Answer
```

这对银行、金融、风控、RPA 场景尤其重要。

---

## 5. 让模型和业务系统连接起来

以前做 RPA，流程通常是人写死的：

```text
第一步点这里
第二步查那里
第三步下载文件
```

ReAct Agent 是：

```text
模型根据当前任务和工具结果，动态决定下一步。
```

这就是从“自动化脚本”走向“智能体”的关键。

---

# 十三、银行 RPA 场景示例

用户问：

```text
帮我查一下某企业有没有风险，并生成简要报告。
```

Agent 可以这样工作：

```text
Thought：
这是企业风险分析任务，不能直接回答。需要先查企业基本信息。

Action：
query_company_info(company_name)

Observation：
企业成立 8 年，注册资本 1000 万，经营状态正常。

Thought：
基本信息正常，下一步需要查司法风险。

Action：
query_judicial_risk(company_name)

Observation：
存在 2 条被执行记录。

Thought：
司法记录可能影响风险等级，还需要查经营异常。

Action：
query_abnormal_operation(company_name)

Observation：
无经营异常。

Thought：
已有基本信息、司法风险、经营异常结果，可以生成最终报告。

Final Answer：
该企业经营状态正常，无经营异常，但存在 2 条被执行记录，建议标记为中风险并人工复核。
```

这就是 ReAct 在真实业务中的形态。

---

# 十四、今天需要掌握的关键区别

| 概念 | 作用 |
|---|---|
| LLM | 负责理解和生成文本 |
| messages | 保存上下文 |
| Thought | 判断下一步该做什么 |
| Action | 调用工具 |
| Observation | 工具返回结果 |
| CoT | 让模型一步一步推理 |
| ReAct | 让模型一边推理一边行动 |
| Final Answer | 给用户看的最终回答 |

---

# 十五、Day 4 学习截止点

今天学到这里截止：

```text
ReAct 方法
```

不要继续往下学：

```text
行动，使智能体能够与环境交互
观察，整合反馈以反思和适应
简单智能体库
使用 Smolagents 创建我们的第一个智能体
```

这些是后面几天的内容。

---

# 十六、Day 4 代码建议

Day 4 不需要写复杂代码。

今天重点是理解 Thought 和 ReAct。

建议只写两个小练习：

```text
examples/04-thoughts/
├── thought_examples.py
└── react_prompt_demo.py
```

## thought_examples.py

用来打印几种思维类型：

```text
Planning
Analysis
Decision Making
Self-Reflection
Prioritization
```

## react_prompt_demo.py

用来对比：

```text
不加“逐步思考”的回答
vs
加“逐步思考”的回答
```

目标不是炫技，而是理解：

```text
提示模型逐步思考，通常能让复杂问题更稳。
```

---

# 十七、Day 4 验收问题

今天结束前，必须能回答下面问题：

1. Thought 是最终答案吗？
2. Thought 的作用是什么？
3. Thought 是基于什么信息产生的？
4. messages 和 Thought 有什么关系？
5. Planning 是什么？
6. Analysis 是什么？
7. Decision Making 是什么？
8. Self-Reflection 是什么？
9. CoT 是什么？
10. ReAct 是什么？
11. CoT 和 ReAct 有什么区别？
12. 为什么要让模型先思考再行动？
13. ReAct 为什么适合 Agent？
14. ReAct 在工程上有什么意义？
15. 用银行 RPA 举一个 ReAct 的例子。

---

# 十八、今日结论

Day 4 的核心不是学新框架，而是理解 Agent 的“脑子”。

可以这样记：

```text
Thought 是 Agent 的脑子；
Action 是 Agent 的手；
Observation 是外界反馈；
ReAct 是让脑子和手配合起来干活的方法。
```

ReAct 解决的问题是：

```text
模型直接回答容易错；
复杂任务一步做不完；
实时信息需要工具；
工具失败需要调整；
企业场景需要过程可审计。
```

一句话总结：

```text
ReAct = 想一步，做一步，看结果，再想下一步。
```

