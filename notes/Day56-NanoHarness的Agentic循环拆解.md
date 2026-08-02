# Day56 — Unit 6: Nano Harness 的 Agentic Loop 深度拆解

> 课程地址：https://huggingface.co/learn/context-course/unit6/agent-loop  
> 课件源码：https://github.com/huggingface/context-course/blob/main/units/en/unit6/agent-loop.mdx  
> 上一节：Day55 - Nano Harness 引言：从零认识 Agent

---

## 0. 这节课在干嘛？一句话说清

Day55 你认识了 Nano Harness 长什么样。这节课我们**把代码一行一行拆开读**——配置、系统提示词、4 个工具、主循环、错误处理、步数上限、消息历史。

目标只有一个：**让你彻底看懂那个「循环」到底怎么转。** 读完你会发现，一个能干活的最小 Agent，其实就那么多东西。

> 💡 **大佬视角**：这节课是 Unit 6 的「心脏解剖课」。之前你站在外面看它跑，今天你把手伸进胸腔，摸一摸左心室右心室。

> ⚠️ 官方还提供了一个可交互演示页（课程页里的 iframe）：https://context-course-agent-loop.static.hf.space ，想看动态效果可以打开。

---

## 1. 配置区：先定规矩

代码最上面是一堆常量，相当于给 Agent 立「家规」：

```python
TASK = "Inspect the workspace and provide a summary."
MODEL = os.getenv("NANO_MODEL", "zai-org/GLM-5.1")
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://router.huggingface.co/v1")
API_KEY = os.getenv("HF_TOKEN", "")
WORKSPACE = str(Path.cwd())
MAX_STEPS = 50
TEMPERATURE = 0.2
TIMEOUT_S = 30
MAX_CHARS = 8000
ALLOW_WRITE = False
ALLOW_COMMANDS = ["ls", "cat", "pwd", "echo", "head", "tail", "wc", "rg"]
```

逐个解释（小白版）：

| 常量 | 是什么 | 为什么重要 |
|------|--------|-----------|
| `TASK` | 要做的任务 | 就是这个 Agent 的「工作目标」 |
| `MODEL` | 用哪个模型 | 默认 `zai-org/GLM-5.1`，走 HF 路由 |
| `BASE_URL` | 模型接口地址 | OpenAI 风格 `/v1`，HF router 兼容 |
| `WORKSPACE` | 工作目录 | 文件操作只能在这范围内 |
| `MAX_STEPS` | 最多循环 50 次 | **保证一定停下来**，不会无限转 |
| `TEMPERATURE` | 0.2 | 越低越「确定」、越不胡说 |
| `TIMEOUT_S` | 30 秒 | 一条命令最多跑 30 秒，超时拉倒 |
| `MAX_CHARS` | 8000 | 工具输出最多 8000 字，防塞爆上下文 |
| `ALLOW_WRITE` | False | **默认禁止写文件**，防误改 |
| `ALLOW_COMMANDS` | 8 个白名单命令 | shell 只能跑这些 |

> 💡 `TEMPERATURE=0.2` 是什么？你可以理解为「模型的随机度」。0 表示每次都尽量一样（最稳），1 表示天马行空。Agent 要稳定干活，所以压到 0.2。

---

## 2. 系统提示词：教模型「怎么说话」

系统提示词决定了模型的行为方式：

```python
SYSTEM_PROMPT = f"""You are a code-first agent.
Output only executable Python code, no prose.

Tools available:
- list_dir(path='.'): List directory contents
- read_file(path, max_chars=4000): Read file
- write_file(path, content): Write file (only if ALLOW_WRITE=True)
- exec_cmd(args): Run shell command

When task is complete, call:
  final_answer(result)

Constraints:
- All file paths confined to workspace: {WORKSPACE}
- Allowed commands: {ALLOW_COMMANDS}
- Max output: {MAX_CHARS} chars
- No markdown, no prose—only Python
"""
```

注意它干了三件关键的事：

1. **「只输出 Python，别写废话」** —— 这样代码才好解析执行，不会夹带散文。
2. **把 4 个工具列出来** —— 模型才知道自己能调什么。
3. **告诉模型「完成时调 `final_answer()`」** —— 这就是「结束信号」。

约束条件（`{WORKSPACE}`、`{ALLOW_COMMANDS}`、`{MAX_CHARS}`）是 f-string 填进去的，所以模型收到的就是具体数值，而不是占位符。

> 💡 这就是 Day55 讲的「系统提示词把设计选择变可读」的实例。

---

## 3. 工具定义：每个工具都在边界上做安全检查

4 个工具 + 1 个结束函数。重点看每行的「安全闸门」：

```python
def list_dir(path="."):
    """List directory contents."""
    p = safe_path(path)                 # 确保路径在工作空间内
    if not p.is_dir():
        raise NotADirectoryError(str(p))
    return sorted([x.name + ("/" if x.is_dir() else "") for x in p.iterdir()])

def read_file(path, max_chars=4000):
    """Read file with size limit."""
    p = safe_path(path)
    content = p.read_text(encoding="utf-8", errors="replace")
    return clip(content, min(max_chars, MAX_CHARS))   # 限制输出长度

def write_file(path, content):
    """Write or create file if writes are enabled."""
    if not ALLOW_WRITE:
        raise PermissionError("write_file disabled")  # 默认禁用
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(str(content), encoding="utf-8")
    return f"Wrote {len(str(content))} bytes"

def exec_cmd(args):
    """Execute shell command (whitelisted only)."""
    if args[0] not in ALLOW_COMMANDS:
        raise PermissionError(f"Command {args[0]} not allowed")  # 白名单检查
    result = subprocess.run(args, capture_output=True, timeout=TIMEOUT_S, text=True)
    output_parts = []
    if result.stdout:
        output_parts.append(f"stdout:\n{result.stdout}")
    if result.stderr:
        output_parts.append(f"stderr:\n{result.stderr}")
    output = "\n\n".join(output_parts) or f"(exit code {result.returncode} with no output)"
    return clip(output, MAX_CHARS)

DONE = False
FINAL_RESULT = None

def final_answer(value):
    """Agent calls this when task is complete."""
    global DONE, FINAL_RESULT
    DONE = True
    FINAL_RESULT = value
    return value
```

安全设计要点（小白版）：

- **`safe_path(path)`**：把路径解析后，验证它确实落在 `WORKSPACE` 内。防止模型用 `../` 逃出工作目录去读 `~/.ssh` 之类。
- **`read_file`**：读出来后 `clip()` 截断到 `MAX_CHARS`，防止大文件塞爆上下文。
- **`write_file`**：先查 `ALLOW_WRITE`，默认 False，直接抛 `PermissionError`。
- **`exec_cmd`**：第一步就检查 `args[0]` 是不是在 `ALLOW_COMMANDS` 白名单里，不是直接拒绝。
- **`final_answer(value)`**：把 `DONE` 设为 True，并记下最终答案。循环看到 `DONE` 就停。

> 💡 这就是 Day55 说的「沙箱在工具边界上」——每个工具自己先守好门，不安全就抛错。

---

## 4. 主循环：Agent 的心脏（重点中的重点）

```python
def main():
    global DONE, FINAL_RESULT
    DONE = False
    FINAL_RESULT = None
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": TASK}
    ]

    for step in range(MAX_STEPS):
        print(f"\n[Step {step + 1}]")

        # 1. 调用 LLM
        response = client.responses.create(
            model=MODEL, temperature=TEMPERATURE, input=messages
        )
        content = response.output_text
        print(f"Model output:\n{content[:500]}...")

        # 2. 把模型输出加入历史
        messages.append({"role": "assistant", "content": content})

        # 3. 解析并执行 Python 代码
        code = extract_python(content)
        try:
            stdout_buffer = io.StringIO()
            stderr_buffer = io.StringIO()
            exec_globals = {
                "__builtins__": {},
                "list_dir": list_dir,
                "read_file": read_file,
                "write_file": write_file,
                "exec_cmd": exec_cmd,
                "final_answer": final_answer
            }
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code, exec_globals)

            stdout_text = stdout_buffer.getvalue().strip()
            stderr_text = stderr_buffer.getvalue().strip()

            if DONE:
                result = f"Final answer: {clip(FINAL_RESULT)}"
            else:
                observations = []
                if stdout_text:
                    observations.append(f"stdout:\n{clip(stdout_text)}")
                if stderr_text:
                    observations.append(f"stderr:\n{clip(stderr_text)}")
                result = "\n\n".join(observations) or "Executed successfully (no output)"
        except FileNotFoundError:
            result = "Error: FileNotFoundError: File not found"
        except PermissionError as e:
            result = f"Error: PermissionError: {str(e)}"
        except subprocess.TimeoutExpired:
            result = "Error: TimeoutError: Command took too long"
        except Exception as e:
            result = f"Error: {type(e).__name__}: {str(e)}"

        # 4. 是否调用了 final_answer()？
        if DONE:
            print(f"✓ Task complete: {FINAL_RESULT}")
            break

        # 5. 把观察结果加回历史
        messages.append({"role": "user", "content": result})

    if not DONE:
        print(f"✗ Max steps ({MAX_STEPS}) reached without final_answer()")
```

把这段拆成「一次循环」的 5 个动作（小白版）：

1. **调模型**：把整个 `messages` 历史发给 LLM，拿到模型输出（一段 Python 代码）。
2. **存记录**：把模型这段代码当作 `assistant` 消息加进历史。
3. **执行代码**：
   - `extract_python(content)` 把代码从回复里抠出来；
   - `exec_globals` 是一个**被阉割的全局环境**：`__builtins__: {}`（几乎不能调用任何内置函数，比如不能 `open`、`eval`），只暴露 5 个函数（4 工具 + `final_answer`）；
   - `redirect_stdout/stderr` 把代码打印的东西接住，存进 buffer；
   - 如果代码里调用了 `final_answer()`，`DONE` 变 True。
4. **判断是否结束**：如果 `DONE`，打印最终答案并 `break` 跳出循环。
5. **喂回观察**：否则把 `stdout`/`stderr` 或错误信息，当作 `user` 消息加回历史，进入下一轮。

> ⚠️ **`__builtins__: {}` 是个关键安全招**：Python 的 `exec()` 默认能访问全部内置函数。这里把 `__builtins__` 清空，等于告诉被执行的那段「模型代码」：你只能用我给你的 5 个函数，别的门都锁了。这是沙箱的核心防线之一。

> 💡 注意：用的是 OpenAI 的 **Responses API**（`client.responses.create`），HF router 也暴露同样的 `/v1` 接口，所以一个模型 ID 驱动全程。

---

## 5. 错误恢复：出错不是崩溃，是「换个思路」

看上面 `try/except` 那段。模型生成的代码可能出错，比如：

- 读了一个不存在的文件 → `FileNotFoundError`
- 想写文件但 `ALLOW_WRITE=False` → `PermissionError`
- 命令跑了超过 30 秒 → `subprocess.TimeoutExpired`
- 其它任何异常 → 落到最后的 `except Exception`

关键点：**这些错误没有被吞掉，而是被变成一句文字 `result`**，然后作为 `user` 消息塞回历史。

效果是什么？模型下一轮会「看到」这个错误，然后自己调整：

- 文件找不到？→ 先 `list_dir('.')` 看看目录里到底有啥。
- 写文件被拒？→ 不再尝试 `write_file`。
- 命令被拦？→ 换成白名单里的命令。
- 超时？→ 把大任务拆成小步骤。

> 💡 这就是「**错误即观察（errors become observations）**」——Agent 不会崩，它会从错误里学习，下一轮换个做法。这是 Agent 比普通脚本聪明的地方。

---

## 6. 步数上限：保证一定停下来

```python
for step in range(MAX_STEPS):   # MAX_STEPS = 50
    ...
    if DONE:
        break

if not DONE:
    print("Max steps reached without final_answer()")
```

`for step in range(50)` 意味着**最多转 50 圈**。要么模型主动 `final_answer()` 提前 `break`，要么转满 50 圈后结束（打印一句「没完成」）。

为什么需要这个？因为模型可能陷入死循环、反复重试同一个错误、或者就是不调用 `final_answer()`。没有上限，程序会永远跑下去。

经验值（官方给的）：
- 简单任务（列文件）：1~3 步
- 探索代码库：5~10 步
- 调试不简单的问题：15~30 步

> 💡 步数上限就是 Agent 的「防呆保险丝」。

---

## 7. 消息历史：Agent 的「记忆」

`messages` 列表就是 Agent 的短期记忆。每次循环往里加东西，下次调用模型时它全看得到：

```python
messages = [
    {"role": "system",     "content": "You are a code-first agent..."},
    {"role": "user",       "content": "Inspect workspace and summarize"},
    {"role": "assistant",  "content": "list_dir('.')\nread_file('README.md')"},
    {"role": "user",       "content": "Found: ['README.md', 'src/', 'tests/']\n\nREADME.md contains:\n..."},
    {"role": "assistant",  "content": "read_file('src/main.py')"},
    {"role": "user",       "content": "src/main.py:\n..."},
]
```

模式很清晰：**system → user任务 → assistant代码 → user观察 → assistant代码 → user观察 → ……** 交替进行。

因为每次都发送完整历史，模型可以：
- 引用之前的发现；
- 避免重复已经失败的做法；
- 在之前结果上继续推进。

> ⚠️ **这是简化版记忆。** 官方明确说明：Nano Harness 把记忆当成「扁平的对话历史」，所有轮次一直留在上下文里，直到窗口塞满。生产级 Agent 用的是更复杂的记忆架构：短期草稿、情景记忆、语义记忆、检索增强、压缩旧上下文等（比如 MemoryAgentBench、A-MEM、ACON）。Nano Harness 只展示「最小可用循环」，不是全貌。

---

## 8. 上下文管理：别把窗口撑爆

```python
# 好：一次读一个文件
read_file("test.py", max_chars=2000)         # 2000 字 ✓

# 坏：想一次读整个大代码库
read_file("large_codebase.py", max_chars=50000)  # 被截断到 8000
```

配合 `MAX_CHARS=8000` 和 `MAX_TOKENS=4096`，工具输出会被 clip。模型会逐渐学会「分次、策略性地读」，别一股脑塞太多。

> ⚠️ 官方提醒：生产环境的上下文管理是大话题——压缩旧上下文、结构化笔记、把中间结果写文件（而非留在窗口）、智能选工具等。Nano Harness 只演示最简单的方式：硬性字符限制，指望模型读得聪明点。

---

## 9. 设计决策：为什么这么写？

官方总结的几个关键决策，小白版翻译：

1. **用 Python 而非 JSON/散文**：Python 表达力强、明确，不会歧义。JSON 只能说「调哪个工具」，Python 能写判断、循环、串联多个工具。
2. **`safe_path()` 防路径穿越**：每个路径都校验是否在工作空间内，防止 `../` 逃逸。
3. **命令白名单**：只有明确允许的 shell 命令能跑。
4. **硬上限**：步数上限 + 单步输出上限，同时约束运行时间和上下文增长。
5. **异常变观察**：Agent 能自我纠错，而不是崩溃。

---

## 10. 大佬总结（Key Takeaways）

1. **循环 = 调模型 → 解析代码 → 执行 → 观察 → 重复。** 就这么 5 步，转最多 50 次。
2. **系统提示词定义工具、约束、结束信号。** 模型「只输出 Python」。
3. **沙箱在工具边界**：路径限制、命令白名单、输出截断、写文件默认关。
4. **错误变成观察**：模型看到错误会自我调整，不崩溃。
5. **完整消息历史 = 记忆**：模型每次都能回顾之前所有轮次。

> 💡 **一句话带走**：Nano Harness 把「一个能干活的最小 Agent」压缩成了：一段讲规矩的系统提示词 + 4 个守门的工具 + 一个最多 50 圈的循环 + 把错误当饭吃的记忆。看懂这 200 行，你就看懂了所有 Agent 框架的心脏。

---

## 11. 下一节预告

> **Tools and Sandboxing in Detail**：我们会更进一步，专讲工具是怎么设计的、沙箱边界怎么画、为什么白名单这样选。

---

## 附：逐行注释版完整代码

上面各节是「按模块解析」。如果你想**逐行对照着读真代码**，仓库里放了一份可直接运行的逐行中文注释版：

- `examples/56-nano-harness/nano_harness_annotated.py`

它把课件里分散的片段（配置、系统提示词、4 个工具、`final_answer`、主循环、错误恢复、步数上限）**补全成一份完整可跑的 `nano_harness.py`**，并为**几乎每一行**都加了中文注释：

- 课件原文只给了片段，其中 `safe_path()` / `clip()` / `extract_python()` / 客户端初始化等辅助函数按课件描述的语义补全，使整份代码能直接 `python nano_harness_annotated.py` 运行（需先 `export HF_TOKEN=...` 并设置 `NANO_MODEL`）。
- 重点注释集中在两处：**`exec_globals = {"__builtins__": {}, ...}`**（沙箱核心：清空内置函数、只暴露 5 个工具函数）和 `try/except` 把异常变成观察（错误即观察）。

配合本课件从第 1~10 节的模块讲解一起看，就能做到「先懂每块干嘛，再逐行确认怎么写」。
