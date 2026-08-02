# Day55 — Unit 6: Nano Harness 引言：从零认识 Agent 黑箱

> 课程地址：https://huggingface.co/learn/context-course/unit6/introduction  
> 课件源码：https://github.com/huggingface/context-course/blob/main/units/en/unit6/introduction.mdx  
> 上一节：Day54 - Hooks 实战：搭建 Agent 活动看板

---

## 0. 这一单元在干嘛？一句话说清

前五单元，你用了 Claude Code、Codex、OpenCode、Pi、smolagents、LangGraph、LlamaIndex 这些框架。它们很方便，但有个问题：**它们把 Agent 最核心的心脏——"那个循环"——藏起来了。**

Unit 6 要做一件反直觉但极有价值的事：**抛开大框架，用约 220 行 Python 自己写一个最小 Agent——Nano Harness。** 不是为了替代生产框架，而是为了让你亲眼看见 Agent 到底是怎么一步一步思考的、工具怎么被调用的、结果怎么回到上下文的、哪里容易出错、安全边界在哪。

> 💡 **大佬视角**：用了这么久 Agent，终于到了"拆发动机"的环节。你不需要重复造轮子，但你需要知道轮子为什么能转。

> ⚠️ **重要提醒**：Nano Harness 是**学习工具，不是生产工具**。不要在真实工作里用它。

---

## 1. 为什么要从零开始？

学习任何复杂系统，最有效的方式之一都是：**把它拆到最小，再拼回去。**

大框架把以下这些东西打包得很漂亮：

- 系统提示词（system prompt）
- 多轮对话的消息历史
- 工具调用与解析
- 错误重试
- 安全沙箱
- 上下文窗口管理

这些设计选择在大框架里是"默认的"、不可见的。但 Nano Harness 把它们全部摊在一个文件里，让你能一行一行读：

```text
为什么这里要重试？
模型输出怎么解析成代码？
出错了是继续还是停止？
文件访问为什么被限制在工作目录？
命令为什么只允许 ls/cat/pwd 这些？
```

当你读完这个最小实现，再回头看 Claude Code / Codex / LangGraph 的设计，很多东西会豁然开朗。

---

## 2. Nano Harness 是什么？

一个约 **220 行 Python** 写的最小 Agent 框架。它只做 7 件事：

```text
1. 接受任务      —— "Inspect the workspace and provide a summary"
2. 调用 LLM     —— 用 OpenAI-compatible API（默认走 Hugging Face Inference Providers）
3. 生成 Python 代码 —— 模型不返回 JSON，而是返回可执行的 Python 代码
4. 安全执行      —— 在受限环境里运行这段代码
5. 观察结果      —— 收集 stdout / stderr / 异常 / 最终答案
6. 更新上下文    —— 把观察结果喂回给模型
7. 重复         —— 直到任务完成或达到步数上限（默认 50 步）
```

> 💡 注意它和之前学的大多数 Agent 不一样：之前模型可能返回 JSON 工具调用（ToolCallingAgent），或者返回自然语言里的 `<tool>` 标记。Nano Harness 里**模型直接返回 Python 代码**，Agent 把它当成 Python 脚本执行。

---

## 3. Nano Harness 的四大关键设计

### 3.1 Code-First Agent：模型直接写 Python

模型给出的不是 "我要调用 list_dir"，而是直接一段 Python：

```python
files = list_dir(".")
models = read_file("models.txt")
final_answer("Files:\n" + "\n".join(files) + "\n\nmodels.txt:\n" + models)
```

Agent 的工作就是：**拿到这段字符串 → 解析 → 在受限环境里执行。**

这和 smolagents 的 CodeAgent 思路很像，但 Nano Harness 把解析器、执行器、错误处理全写在一个文件里，没有隐藏。

### 3.2 受限工具（Constrained Tools）

只有 4 个工具可用：

| 工具 | 作用 | 安全限制 |
|------|------|---------|
| `list_dir(path)` | 列出目录内容 | 路径限制在工作空间内 |
| `read_file(path, max_chars)` | 读取文件 | 路径限制 + 大小上限 |
| `write_file(path, content)` | 创建/修改文件 | 路径限制 + **默认禁用** |
| `exec_cmd(args)` | 运行 shell 命令 | 只允许白名单命令：`ls`, `cat`, `pwd`, `echo`, `head`, `tail`, `wc`, `rg` |

> 💡 看到没有？`write_file` 默认关闭，`exec_cmd` 不是你想跑啥就跑啥。这些限制都是为了防止学习时一个不留神把电脑搞坏。

### 3.3 沙箱执行（Sandboxed Execution）

- 所有文件操作被限制在工作空间目录内；
- 命令只能跑白名单里的；
- 输出有大小限制，防止大输出塞爆上下文；
- 执行有超时，防止死循环挂起。

这就是前面课程里反复提到的 **sandboxing**（沙箱化）的一个最小实现。

### 3.4 模型：走 Hugging Face Inference Providers

Nano Harness 默认用 **zai-org/GLM-5.1** 模型，通过 Hugging Face Inference Providers 调用。它的接口是 **OpenAI-compatible** 的，也就是 `/v1/chat/completions` 那种风格。

环境变量：

```bash
export NANO_MODEL="zai-org/GLM-5.1"
export HF_TOKEN="hf_..."
```

---

## 4. Agentic Loop：Nano Harness 的心脏

整个 Agent 的核心就是一个循环：

```text
1. 把「任务 + 历史消息」发给 LLM
2. 把模型输出解析成 Python 代码
3. 在受限环境里执行这段代码
4. 收集 stdout、stderr、异常
5. 把观察结果追加到消息历史
6. 回到第 1 步（最多 50 步）
7. 结束条件：调用 final_answer()，或达到步数上限
```

这个循环就是前面课程里反复说的 **Thought → Action → Observation** 的最小完整实现：

- **Thought**：模型看到上下文后，在代码里体现的推理；
- **Action**：那段 Python 代码实际做的事；
- **Observation**：代码执行后的输出，再喂回去。

> 💡 你现在应该能感觉到：之前所有框架里那个"自动循环"，本质上都是这个 7 步流程的包装和扩展。Nano Harness 把它赤裸裸的摆在你面前。

---

## 5. 这一单元你会学到什么？

按课程安排，Unit 6 会带你：

1. **逐行读懂 Nano Harness 的 Agent 循环代码** —— 系统提示词、解析、执行、错误处理；
2. **理解工具设计和沙箱机制** —— 为什么只允许这 4 个工具、沙箱边界怎么画；
3. **扩展 Nano Harness** —— 加入 `web_fetch` 和 Hugging Face Hub 搜索这两个新工具；
4. **用 zai-org/GLM-5.1 跑通它** —— 通过 Hugging Face Inference Providers。

也就是说，这一单元不是教你"怎么用框架"，而是教你"框架里面长什么样"。

---

## 6. 学前准备

- 基础 Python；
- 对 HTTP API 有概念；
- 对沙箱/安全边界有概念；
- 一个 Hugging Face token，且有 Inference Providers 的访问权限。

---

## 7. 大佬总结（Key Takeaways）

1. **Nano Harness 是教学用的"裸机"Agent**，约 220 行 Python，不是生产框架。
2. **它让设计选择变得可读**：系统提示词、循环、工具、沙箱、错误处理全在一个文件里。
3. **模型直接输出 Python 代码**（Code-First），Agent 解析并沙箱执行。
4. **工具是受限的**：4 个基础工具，文件访问限在工作目录，shell 命令限白名单。
5. **核心还是 Thought-Action-Observation 循环**，只是这次没有框架帮你包起来。

> 💡 **一句话带走**：前面你学会了"开飞机"，这一单元把飞机拆开，让你看见发动机、操纵杆、油箱、起落架是怎么连在一起的。读完后，你再开任何 Agent 框架都会更有底气。

---

## 8. 下一节预告

> **Agentic Loop 深度拆解**：我们将逐行走进 Nano Harness 的代码，看看系统提示词怎么写、模型输出怎么被解析成代码、执行出错时怎么处理、以及 50 步上限是怎么控制的。
