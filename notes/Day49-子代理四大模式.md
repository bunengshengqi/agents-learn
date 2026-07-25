# Day 49：子代理的四大模式（Subagent Patterns）

**课程来源**：Hugging Face Context Course — Unit 4: Subagent Patterns  
**原文链接**：https://huggingface.co/learn/context-course/unit4/patterns  
**GitHub 地址**：https://github.com/huggingface/context-course/blob/main/units/en/unit4/patterns.mdx  
**学习日期**：2026-07-25

---

## 一、课程核心观点

> **多 agent 工作流虽然千变万化，但归根结底就这四种形状：Fan-Out/Fan-In、Pipeline、Supervisor、Swarm。**

把这四种模式搞懂，后面看任何多 agent 系统都能一眼认出它是哪种变形。

---

## 二、四种模式总览

| 模式 | 一句话 | 生活类比 |
|---|---|---|
| **Fan-Out / Fan-In** | 把任务分给多个人同时做，最后收回来汇总 | 外卖平台同时派 5 个骑手取不同商家的餐，最后一起送到你手上 |
| **Pipeline** | 工序一件接一件，后一件依赖前一件 | 工厂流水线：切菜 → 炒菜 → 装盘 → 上菜 |
| **Supervisor** | 老板带几个专家，各自负责不同领域 | 医院院长带内科、外科、影像科专家会诊 |
| **Swarm** | 多人从不同角度审查同一件东西 | 论文答辩：三个导师轮流提意见，最后你综合修改 |

---

## 三、Pattern 1：Fan-Out / Fan-In（分发-聚合）

### 官方定义

> Spawn multiple subagents in parallel for independent subtasks, then aggregate results.

为独立的子任务并行派生多个子代理，然后聚合结果。

### 通俗解释

父代理收到一个任务，发现这个任务可以拆成好几块，**这几块之间完全没关系**，于是同时派几个小弟去干，等所有人都干完了，把结果拼在一起。

### 经典例子

**场景**：评测 5 个模型在同一个基准上的表现。

```text
父代理: "去评测这5个模型"
        │
        ├──► 子代理1 → Model A 分数
        ├──► 子代理2 → Model B 分数
        ├──► 子代理3 → Model C 分数
        ├──► 子代理4 → Model D 分数
        └──► 子代理5 → Model E 分数
        │
        ▼
父代理聚合: "最终排名: C > A > E > B > D"
```

### 伪代码

```python
models = ["A", "B", "C", "D", "E"]
results = []

for model in models:
    subagent = spawn_subagent(task=f"evaluate {model}")
    results.append(subagent)

scores = wait_all(results)
report = aggregate(scores)
```

### 优点

- **Fully parallel**：完全并行
- **Max speed**：速度最快
- **Easy to scale**：容易扩展

### 缺点

> Total time = slowest subagent

总时间取决于最慢的那个子代理，存在"长尾延迟"问题。

### 记忆口诀

**Fan-Out / Fan-In = 各干各的，最后汇总。**

---

## 四、Pattern 2：Pipeline（流水线）

### 官方定义

> Chain subagents where output of one becomes input to the next.

把子代理链起来，前一个的输出作为后一个的输入。

### 通俗解释

任务必须分步骤做，**后面一步必须等前面一步完成**。就像工厂流水线，不能先包装再生产。

### 经典例子

**场景**：数据处理流程

```text
Raw Data → Extract（提取） → Clean（清洗） → Analyze（分析） → Report（报告）
```

### 伪代码

```python
raw_data = load_data()

extracted = spawn_subagent("extract fields", raw_data).wait()
cleaned = spawn_subagent("clean data", extracted).wait()
analysis = spawn_subagent("analyze trends", cleaned).wait()
report = spawn_subagent("generate report", analysis).wait()
```

### 优点

- **Clear stages**：阶段清晰
- **Easy to track progress**：容易追踪进度
- **Failures are local**：失败局部化

### 缺点

> No parallelism—each stage waits for previous.

没有并行，每个阶段都要等前一个阶段完成。

### 记忆口诀

**Pipeline = 排队做，后一步等前一步。**

---

## 五、Pattern 3：Supervisor（监督者 / 层级式）

### 官方定义

> Parent agent directs multiple specialized subagents, each with different tools and expertise.

父代理指挥多个专业子代理，每个子代理有不同的工具和专长。

### 通俗解释

父代理是老板，手下有几个不同领域的专家。老板不亲自干活，而是根据任务需要，调用对应的专家，最后把专家的结论整合成最终答案。

### 经典例子

**场景**：准备一份产品发布报告，需要销售数据、工程进度、市场反馈。

```text
父代理（Supervisor）: "给我写一份产品发布报告"
        │
        ├──► Sales 子代理
        │     工具: CRM 系统
        │     任务: 查销售额、转化率、客户反馈
        │
        ├──► Engineering 子代理
        │     工具: GitHub API
        │     任务: 整理新功能、bug 修复、发布内容
        │
        └──► Marketing 子代理
              工具: 分析平台
              任务: 查广告效果、社媒热度、竞品动态
        │
        ▼
父代理整合 → "产品发布报告"
```

### 与 Fan-Out/Fan-In 的区别

| | Fan-Out/Fan-In | Supervisor |
|---|---|---|
| 子代理角色 | 同样的工作，分给不同的人 | 不同的人做不同的事 |
| 工具 | 通常用同样工具 | 通常用不同工具 |
| 类比 | 5 个骑手取外卖 | 院长带不同科室专家会诊 |

### 优点

- **Specialized agents**：专业化代理
- **Clean separation of tools**：工具分离清晰
- **Parallel execution**：可并行执行

### 缺点

> More complex coordination.

协调更复杂。

### 记忆口诀

**Supervisor = 老板带专家，各管一摊。**

---

## 六、Pattern 4：Swarm（蜂群 / 协作式）

### 官方定义

> Multiple subagents work on the same problem, comparing approaches and converging on best solution.

多个子代理处理同一个问题，比较不同方法，收敛到最佳解决方案。

### 通俗解释

不是把任务拆成几块各做各的，而是**让多个人从不同角度同时看同一件东西**，然后互相补充、修正，得到更好的结果。

### 经典例子

**场景**：设计一个新 API。

```text
初始设计稿
    │
    ├──► Architect 子代理
    │     角度: 架构是否合理、可扩展性
    │
    ├──► Security 子代理
    │     角度: 有没有安全漏洞、权限设计
    │
    └──► Performance 子代理
          角度: 性能瓶颈、响应时间
    │
    ▼
父代理整合三份评审意见 → 改进版设计稿
```

### 与 Supervisor 的区别

| | Supervisor | Swarm |
|---|---|---|
| 关注点 | 不同子代理处理不同子任务 | 不同子代理从同一问题的不同角度审查 |
| 输出 | 各自产出一部分结果 | 各自产出一部分意见 |
| 类比 | 医院专家会诊（每人看不同指标） | 论文答辩（三个导师都审同一篇论文） |

### 优点

- **Multiple perspectives improve quality**：多角度提升质量
- **Catches blind spots**：发现盲点

### 缺点

> Can be slow (requires multiple rounds).

可能比较慢，尤其是需要多轮迭代时。

### 记忆口诀

**Swarm = 多人会诊同一件东西，互相挑毛病。**

---

## 七、四种模式对比

| 模式 | 适用场景 | 并行度 | 协调复杂度 |
|---|---|---|---|
| **Fan-Out/Fan-In** | 互相独立的任务 | 高 | 低 |
| **Pipeline** | 有先后顺序的阶段 | 无 | 中 |
| **Supervisor** | 需要多个专家协作 | 中高 | 中高 |
| **Swarm** | 多人协作改进同一件产物 | 低-中 | 高 |

### 选择指南

- 任务可以拆开、互相不依赖 → **Fan-Out/Fan-In**
- 任务必须一步一步来 → **Pipeline**
- 任务需要不同领域专家各出一部分 → **Supervisor**
- 任务需要多角度审查同一产物 → **Swarm**

---

## 八、什么时候不要用子代理？（避坑指南）

### 1. 强串行依赖的工作

**错误做法**：为每一步都派生子代理，然后一个个等。

**正确做法**：串行工作直接在**一个代理**里完成，或用 Pipeline 但整体控制简单。

> Single agent for sequential work.

### 2. 多个子代理同时编辑同一个文件

**错误做法**：两个子代理同时修改 `main.py`。

**正确做法**：让每个子代理处理不同的文件，最后由父代理合并。

> Fan-out on different files.

### 3. 任务本身很小

**错误做法**：为了格式化一个 JSON，专门派个子代理。

**正确做法**：直接在父代理里完成。

> Overhead: 1-2s, task: 0.1s

### 4. 专业子代理太多

**错误做法**：创建十几个超细分子代理。

**正确做法**：把专家分组，让高级架构师带实施团队。

> Group specialists.

---

## 九、核心 Takeaways

1. **Fan-out/fan-in parallelises independent work.**
   > 分发-聚合用于并行处理独立工作。

2. **Pipeline chains stages.**
   > 流水线用于按阶段串联任务。

3. **Supervisor coordinates specialists.**
   > 监督者模式用于协调多个专家。

4. **Swarm cross-reviews a single artefact.**
   > 蜂群模式用于多角度审查同一件产物。

### 黄金法则

> Reach for subagents when you have many files or several independent tasks.
> Stick with a single agent for small jobs and tightly coupled workflows.

当你有很多文件或几个独立任务时，考虑用子代理。小任务和强耦合的工作流，就用单代理。

---

## 十、代码示例位置

本课配套代码示例位于：

```text
examples/49-subagent-patterns/subagent_patterns.py
```

该示例用 Python 函数模拟了四种子代理模式的基本执行流程，适合初学者理解不同模式的核心差异。

---

## 十一、今日面试题

### Q1：子代理有哪四种常见模式？请简述各自的特点。

**参考答案**：

1. **Fan-Out/Fan-In**：将独立子任务并行分发给多个子代理，最后聚合结果。适合互相独立的任务，并行度高。
2. **Pipeline**：将任务按阶段串联，前一阶段输出作为后一阶段输入。适合有明确先后顺序的工作。
3. **Supervisor**：父代理协调多个专业子代理，每个子代理有不同工具和专长。适合复杂任务需要多领域专家协作。
4. **Swarm**：多个子代理从多角度审查同一件产物，互相补充修正。适合需要高质量决策或设计的场景。

---

### Q2：Fan-Out/Fan-In 和 Supervisor 有什么区别？

**参考答案**：

- **Fan-Out/Fan-In**：子代理做的是同类或独立的工作，工具通常相同，强调并行和汇总。
- **Supervisor**：子代理是不同领域的专家，使用不同工具，父代理负责协调和整合各专业输出。

---

### Q3：Pipeline 模式的主要缺点是什么？什么时候不适合用？

**参考答案**：

主要缺点是**没有并行性**，每个阶段必须等待前一阶段完成，总时间是各阶段时间之和。

不适合：任务步骤之间没有强数据依赖、可以并行执行的场景。这种情况下应该优先考虑 Fan-Out/Fan-In。

---

### Q4：Swarm 模式适合什么场景？使用时需要注意什么？

**参考答案**：

适合需要多角度审查、提升质量的场景，比如 API 设计、架构评审、安全审查等。

需要注意：Swarm 通常比单代理慢，尤其是多轮迭代时；token 消耗和协调成本较高，应该只在重要决策上使用。

---

### Q5：哪些情况下不应该使用子代理？

**参考答案**：

1. 强串行依赖的工作，用单代理或简单 Pipeline 更合适。
2. 多个子代理需要同时编辑同一个文件，容易产生冲突。
3. 任务本身很小，创建子代理的开销大于任务收益。
4. 专业子代理过多，协调成本会变得很高，应该分组管理。

---

## 十二、参考资料

- Hugging Face Context Course — Subagent Patterns: https://huggingface.co/learn/context-course/unit4/patterns
- GitHub 原文：https://github.com/huggingface/context-course/blob/main/units/en/unit4/patterns.mdx
