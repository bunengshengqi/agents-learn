# Day57 — Unit 6: 工具与沙箱详解（Tools & Sandboxing）

> 课程地址：https://huggingface.co/learn/context-course/unit6/tools-and-sandboxing  
> 课件源码：https://github.com/huggingface/context-course/blob/main/units/en/unit6/tools-and-sandboxing.mdx  
> 上一节：Day56 - Nano Harness 的 Agentic Loop 深度拆解

---

## 0. 这节课在干嘛？一句话说清

Day56 你看懂了「循环」怎么转。这节课专门讲循环里那 4 个**工具**——也就是 Agent 的「手」——以及它们身上那套**安全围栏（沙箱）**。

> 💡 **大佬视角**：工具是 Agent 跟世界交互的唯一出口。所谓「安全」，不是靠模型自觉，而是靠**在工具的边界上一道道门**。这节课就是把每道门拆给你看。

配套可运行代码已放在 `examples/57-nano-harness-tools/nano_tools.py`（4 个工具 + safe_path + 沙箱 + 好/坏工具设计对照，逐行注释，可直接 `python nano_tools.py` 看效果）。

---

## 1. 四个工具：Agent 的「四只手」

### 1.1 `list_dir(path)` —— 列目录

```python
def list_dir(path="."):
    p = safe_path(path)                 # 路径先过安检（防越界）
    if not p.is_dir():
        raise NotADirectoryError(str(p))
    return sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir())
```

- 返回值只有**文件名**，不是绝对路径；目录名后加 `/` 方便区分。
- 经过 `safe_path()`，所以 `list_dir("../etc")` 会被拦。

```python
list_dir(".")          # ✓ OK
list_dir("src")        # ✓ OK
list_dir("../etc")     # ✗ 被 safe_path() 拦下
```

### 1.2 `read_file(path, max_chars)` —— 读文件

```python
def read_file(path, max_chars=4000):
    p = safe_path(path)
    content = p.read_text(encoding="utf-8", errors="replace")  # 乱码替换，不崩
    return clip(content, min(max_chars, MAX_CHARS))            # 双重上限
```

两个保险：① 路径过 `safe_path`；② 长度取 `min(max_chars, MAX_CHARS)`——**就算模型要 `max_chars=999999`，也最多给 8000**。

```python
read_file("README.md")                  # ✓ 最多 4000 字
read_file("data.txt", max_chars=500)    # ✓ 最多 500 字
read_file("huge.db")                     # ✓ 被截到 8000 字（不会无限）
read_file("/etc/passwd")                 # ✗ 被 safe_path() 拦下
```

### 1.3 `write_file(path, content)` —— 写文件（默认关）

```python
ALLOW_WRITE = False       # 默认关闭！

def write_file(path, content):
    if not ALLOW_WRITE:
        raise PermissionError("write_file disabled")  # 没开就拒绝
    p = safe_path(path)
    p.parent.mkdir(parents=True, exist_ok=True)        # 必要时建父目录
    p.write_text(str(content), encoding="utf-8")
    return f"Wrote {len(str(content))} bytes to {p}"
```

> ⚠️ 关键设计：**写文件默认禁用**。Agent 想改磁盘，必须有人显式把 `ALLOW_WRITE` 设成 `True`。这是「默认安全」原则——宁可不方便，也不让它乱写。

### 1.4 `exec_cmd(args)` —— 跑 shell 命令（仅白名单）

```python
ALLOW_COMMANDS = ["ls", "cat", "pwd", "echo", "head", "tail", "wc", "rg"]

def exec_cmd(args):
    if args[0] not in ALLOW_COMMANDS:                      # 白名单检查
        raise PermissionError(f"Command '{args[0]}' not allowed")
    try:
        result = subprocess.run(args, capture_output=True,
                                timeout=TIMEOUT_S, text=True)  # 30 秒超时
        # ... 收集 stdout/stderr，拼好，clip 截断 ...
        return clip(output, MAX_CHARS)
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"                 # 超时也不崩
```

只有白名单里的 8 个命令能跑（全是**只读、不联网**的：`ls`/`cat`/`pwd`/`echo`/`head`/`tail`/`wc`/`rg`）。任何会改状态或碰网络的（`rm`/`mv`/`curl`/`wget`）一律拒绝。

```python
exec_cmd(["ls", "-la"])              # ✓ OK
exec_cmd(["pwd"])                     # ✓ OK
exec_cmd(["rg", "ERROR"])             # ✓ OK（rg 是 ripgrep，只读搜索）
exec_cmd(["rm", "-rf", "/"])         # ✗ 拦下（rm 不在白名单）
exec_cmd(["curl", "evil.com"])       # ✗ 拦下（curl 不在白名单）
```

---

## 2. 路径限制：`safe_path()` —— 所有碰路径的入口

```python
WORKSPACE = Path.cwd()                # 例如 /home/user/project

def safe_path(user_input):
    requested = (WORKSPACE / user_input).resolve()   # 拼到工作目录并解析成绝对路径
    if not requested.is_relative_to(WORKSPACE):      # 解析后是否还在工作目录内
        raise ValueError(f"Path {user_input} escapes workspace")
    return requested
```

它防的是**路径穿越（directory traversal）**：

```python
safe_path("../../../etc/passwd")
# 解析成 /etc/passwd → 不在 WORKSPACE 内 → 抛 ValueError ✓

safe_path("/etc/passwd")
# 绝对路径，不以 WORKSPACE 开头 → 抛 ValueError ✓

safe_path("data/models.txt")
# 解析成 /home/user/project/data/models.txt → 在内 → 返回 ✓
```

> 💡 `resolve()` 会把 `../` 真正算出来再判断，所以无论模型怎么绕，只要最终落点不在工作目录，就过不了门。

---

## 3. 执行沙箱：受限的全局作用域

模型生成的代码不是随便 `exec` 的，而是跑在一个**被阉割的全局环境**里：

```python
exec_globals = {
    "__builtins__": {},   # 清空内置函数：不能 import、不能 open、不能碰网络
    "list_dir": list_dir,
    "read_file": read_file,
    "write_file": write_file,
    "exec_cmd": exec_cmd,
    "final_answer": final_answer
}

exec(agent_code, exec_globals)   # agent 代码只能看到这 5 个函数
```

agent 代码**做不到**的事：
- `import` 任意模块（没有 `__builtins__`）；
- 绕过工具直接读文件；
- 直接用网络；
- 访问父进程的变量。

> 💡 想要 `len()`、`print()` 之类安全内置？**显式加白名单**，而不是继承 Python 全套默认内置。宁可少给，不可多给。

---

## 4. 错误隔离：出错变成「观察」

```python
try:
    exec(agent_code, exec_globals)
except Exception as e:
    error_msg = f"Error: {type(e).__name__}: {str(e)}"
    messages.append({"role": "user", "content": error_msg})  # 错误回给模型
    # 进入下一轮，模型自我调整
```

一个真实的工作流长这样：

```text
第1步：Agent 想读超大文件 → 被 clip 到 8000 字，它看到了截断结果
第2步：Agent 试 exec_cmd(["rm","data.txt"]) → PermissionError: Command 'rm' not allowed
       → 模型看到错误，换别的做法
第3步：Agent 试 read_file("../../../etc/passwd") → ValueError: Path escapes workspace
       → 模型学到并调整
```

> 💡 又是那句话：**错误即观察（errors become observations）**。沙箱不是把错误吞掉，而是翻译成模型能读懂的文字，让它下一轮换思路。

---

## 5. 商业 Agent vs Nano Harness

Claude Code、Codex 背后处理的是**同样的关切**：路径限制、权限询问、超时、输出上限——它们全自动帮你做了，代价是**规则藏起来了、不透明**。

Nano Harness 反过来：把每一条策略都**显式写在你眼前**，你能读、能改，代价是你得自己实现。

> 💡 大佬点评：生产用商业框架图省事，学习用 Nano Harness 图透明。两者解决的是同一个安全问题，只是「谁写规则」不同。

---

## 6. 自己写工具：好设计 vs 坏设计

### ✅ 好的工具设计（四步齐全）

```python
def good_tool(user_input, max_result_size=1000):
    # 1. 校验并限制输入
    if not isinstance(user_input, str):
        raise TypeError("user_input must be string")
    path = safe_path(user_input)          # 1. 路径限制
    result = path.read_text()             # 2. 执行操作
    return clip(result, min(max_result_size, MAX_CHARS))  # 3+4. 限制输出并返回
```

### ❌ 坏的工具设计（逐条踩坑）

```python
# ✗ 不校验输入/路径：能读任何文件
def bad_tool_1(path):
    return open(path).read()

# ✗ 不限制输出：可能返回几 TB，撑爆上下文
def bad_tool_2(query):
    return database.query(query)

# ✗ 不做错误处理：可能超时/卡死
def bad_tool_3(url):
    return requests.get(url).text

# ✗ 完全信任 agent：能跑 rm -rf /，极端危险
def bad_tool_4(command):
    os.system(command)
```

> ⚠️ 这四个反例在 `nano_tools.py` 里也写了，但**标了「故意写错，仅供对照」，不会被调用**。你写自己的工具时，照着 `good_tool` 的四步来，千万别学反例。

---

## 7. 大佬总结（Key Takeaways）

1. **限制工具能触达的范围**：`safe_path()` 把文件访问锁在工作目录内。
2. **命令白名单**拦截会改状态/碰网络的 subprocess 调用。
3. **输出截断**防止上下文爆炸。
4. **写文件默认关**，需显式打开。
5. **错误变成观察**，Agent 能自我纠错而非崩溃。

> 💡 **一句话带走**：工具是 Agent 的手，沙箱是手上的「防护手套」。Nano Harness 把手套缝在每一只手上——路径、命令、输出、写入，处处设防。你写自己的工具时，照 `good_tool` 的四步抄，安全就到位了。

---

## 8. 下一节预告

> **Hands-On: Extending Nano Harness**：亲自动手给 Nano Harness 加新工具（`web_fetch`、HF Hub 搜索），并接上模型真正跑起来。
