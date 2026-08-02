# ============================================================
# nano_harness_annotated.py
# Nano Harness 逐行注释版（教学用，非生产环境）
# 基于 context-course Unit6 agent-loop 课件重建，并为每一行加中文注释
# 说明：课件原文只给了片段，safe_path / clip / extract_python / 客户端
#       等辅助函数按课件描述的语义补全，使整份代码可直接运行。
# ============================================================

import os                              # 导入 os：用来读取环境变量（模型名、token、接口地址）
import io                              # 导入 io：用 StringIO 把代码的标准输出接到内存里
import subprocess                      # 导入 subprocess：在受限环境里执行 shell 命令
from pathlib import Path              # 导入 Path：更安全地拼接和解析文件路径
from openai import OpenAI             # 导入 OpenAI SDK：调用兼容 /v1 的模型接口
from contextlib import redirect_stdout, redirect_stderr  # 导入重定向器：把代码里的 print 改道到 buffer

# -------------------- 1. 配置区：给 Agent 立家规 --------------------

TASK = "Inspect the workspace and provide a summary."   # 任务：Agent 要完成的目标，你可以改成自己的任务
MODEL = os.getenv("NANO_MODEL", "zai-org/GLM-5.1")      # 模型：优先读环境变量 NANO_MODEL，缺省用 GLM-5.1
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://router.huggingface.co/v1")  # 接口地址：HF 的 OpenAI 兼容路由
API_KEY = os.getenv("HF_TOKEN", "")                     # 密钥：从环境变量 HF_TOKEN 读取
WORKSPACE = str(Path.cwd())                             # 工作目录：当前进程所在目录，文件操作只能限制在此
MAX_STEPS = 50                                          # 步数上限：循环最多转 50 圈，保证一定停下来
TEMPERATURE = 0.2                                       # 温度：0.2 偏确定，模型输出更稳定、更少胡说
TIMEOUT_S = 30                                          # 超时：单条 shell 命令最多跑 30 秒，超时即放弃
MAX_CHARS = 8000                                        # 输出上限：工具输出最多 8000 字符，防塞爆上下文窗口
ALLOW_WRITE = False                                     # 写开关：默认禁止写文件，防止 Agent 误改你的东西
ALLOW_COMMANDS = ["ls", "cat", "pwd", "echo", "head", "tail", "wc", "rg"]  # 命令白名单：shell 只能跑这 8 个

# -------------------- 2. 系统提示词：教模型怎么说话 --------------------

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
"""   # 系统提示词：f-string 把 WORKSPACE/ALLOW_COMMANDS/MAX_CHARS 填成真实值；命令模型只输出 Python、列出工具、给出结束信号

# -------------------- 3. 工具函数：每个都在边界上做安检 --------------------

def list_dir(path="."):               # 列出目录内容，参数默认当前目录
    p = safe_path(path)                 # 先把路径校验在工作目录内（防越界）
    if not p.is_dir():                  # 如果解析后不是目录
        raise NotADirectoryError(str(p))  # 抛错，让模型知道路径不对
    return sorted([x.name + ("/" if x.is_dir() else "") for x in p.iterdir()])  # 列出内容，目录名后加 / 便于区分

def read_file(path, max_chars=4000):  # 读文件，默认最多 4000 字符
    p = safe_path(path)                 # 校验路径是否在工作目录内
    content = p.read_text(encoding="utf-8", errors="replace")  # 读文本，遇到乱码用替换符而非报错
    return clip(content, min(max_chars, MAX_CHARS))  # 截断到两者中较小的值（双重保险）

def write_file(path, content):        # 写文件
    if not ALLOW_WRITE:                 # 如果写开关没开
        raise PermissionError("write_file disabled")  # 直接拒绝，不写
    p = safe_path(path)                 # 校验路径
    p.parent.mkdir(parents=True, exist_ok=True)  # 必要时创建父目录
    p.write_text(str(content), encoding="utf-8")  # 把内容写成 UTF-8 文本
    return f"Wrote {len(str(content))} bytes"  # 返回写入的字节数，作为观察结果

def exec_cmd(args):                    # 执行 shell 命令，args 是命令及参数列表
    if args[0] not in ALLOW_COMMANDS:   # 如果命令不在白名单里
        raise PermissionError(f"Command {args[0]} not allowed")  # 直接拒绝
    result = subprocess.run(args, capture_output=True, timeout=TIMEOUT_S, text=True)  # 在超时内执行，捕获输出
    output_parts = []                   # 用来收集输出片段
    if result.stdout:                   # 如果有标准输出
        output_parts.append(f"stdout:\n{result.stdout}")  # 加标签后放入
    if result.stderr:                   # 如果有标准错误
        output_parts.append(f"stderr:\n{result.stderr}")  # 加标签后放入
    output = "\n\n".join(output_parts) or f"(exit code {result.returncode} with no output)"  # 合并；都没输出就给退出码
    return clip(output, MAX_CHARS)      # 截断后返回，防止上下文溢出

DONE = False                            # 全局标志：任务是否已经完成
FINAL_RESULT = None                     # 全局变量：存放最终答案

def final_answer(value):               # 模型完成任务时调用，value 是最终答案
    global DONE, FINAL_RESULT            # 声明要修改上面两个全局变量
    DONE = True                          # 把完成标志置为 True
    FINAL_RESULT = value                 # 存下最终答案
    return value                         # 返回原值，方便在代码里链式使用

# -------------------- 4. 辅助函数：被工具复用的小工具 --------------------

def clip(text, n):                     # 截断文本，n 为最大长度
    text = "" if text is None else str(text)   # 确保是字符串，None 当作空串
    return text if len(text) <= n else text[:n] + "…"  # 超长就截断并加省略号

def safe_path(path):                   # 校验路径是否落在工作目录内，防目录穿越
    root = Path(WORKSPACE).resolve()           # 工作空间的绝对路径
    full = (root / path).resolve()             # 拼上相对路径并解析成绝对路径（处理 ../）
    if not str(full).startswith(str(root)):    # 解析后仍然不在根目录内
        raise PermissionError(f"Path escapes workspace: {path}")  # 越界，拒绝
    return full                                # 返回安全的绝对路径

def extract_python(content):           # 从模型回复里抠出纯 Python 代码
    text = content.strip()                     # 去掉首尾空白
    if "```" in text:                          # 模型可能用 ``` 代码块包裹
        start = text.index("```")              # 找第一个 ```
        end = text.rindex("```")               # 找最后一个 ```
        code = text[start + 3 : end]           # 取中间部分（跳过 ``` 和语言标记占的 3 字符）
        if code.lstrip().startswith("python"): # 如果开头是 python 标记
            code = code.lstrip()[len("python"):]  # 去掉这个标记
        text = code.strip()                    # 再去一遍首尾空白
    return text                                # 返回纯 Python 代码

# -------------------- 5. 客户端：连接模型 --------------------

client = OpenAI(base_url=BASE_URL, api_key=API_KEY)  # 创建 OpenAI 客户端，指向 HF router（同样兼容 /v1）

# -------------------- 6. 主循环：Agent 的心脏 --------------------

def main():                            # 主函数：跑整个 Agent
    global DONE, FINAL_RESULT            # 使用前面定义的全局状态
    DONE = False                         # 每次启动时重置完成标志
    FINAL_RESULT = None                  # 重置最终答案
    messages = [                        # 消息历史：就是 Agent 的短期记忆
        {"role": "system", "content": SYSTEM_PROMPT},  # 第 0 条：系统提示词（讲规矩）
        {"role": "user", "content": TASK}              # 第 1 条：用户任务（要干啥）
    ]

    for step in range(MAX_STEPS):       # 最多 MAX_STEPS 圈，转满就停（保险丝）
        print(f"\n[Step {step + 1}]")   # 打印当前是第几步，方便观察

        # (1) 调用大模型
        response = client.responses.create(  # 调用 Responses API（HF router 兼容）
            model=MODEL,               # 指定用哪个模型
            temperature=TEMPERATURE,   # 低温度，输出更确定
            input=messages             # 把完整历史一起发过去，模型才能"记得"之前的事
        )
        content = response.output_text  # 取出模型回复的文本（一段 Python 代码）
        print(f"Model output:\n{content[:500]}...")  # 只打印前 500 字预览，避免刷屏

        messages.append({"role": "assistant", "content": content})  # (2) 把模型这段代码当作 assistant 消息存进历史

        # (3) 解析并执行 Python 代码
        code = extract_python(content)  # 从回复里抠出纯 Python
        try:
            stdout_buffer = io.StringIO()  # 准备接住代码的标准输出
            stderr_buffer = io.StringIO()  # 准备接住代码的标准错误
            exec_globals = {              # 受限的全局环境：这是沙箱的核心防线
                "__builtins__": {},       # 清空内置函数，模型代码几乎不能直接调用任何危险内置
                "list_dir": list_dir,     # 只暴露这 5 个函数给被执行代码
                "read_file": read_file,
                "write_file": write_file,
                "exec_cmd": exec_cmd,
                "final_answer": final_answer
            }
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):  # 把 print 改道到 buffer
                exec(code, exec_globals)  # 在受限环境里执行模型生成的代码

            stdout_text = stdout_buffer.getvalue().strip()  # 取出标准输出文本
            stderr_text = stderr_buffer.getvalue().strip()  # 取出标准错误文本

            if DONE:                     # 如果代码里调用了 final_answer()
                result = f"Final answer: {clip(FINAL_RESULT)}"  # 拼出最终答案
            else:                        # 否则还没完成任务
                observations = []        # 用来收集这一轮的观察
                if stdout_text:          # 有标准输出
                    observations.append(f"stdout:\n{clip(stdout_text)}")  # 加标签后放入
                if stderr_text:          # 有标准错误
                    observations.append(f"stderr:\n{clip(stderr_text)}")  # 加标签后放入
                result = "\n\n".join(observations) or "Executed successfully (no output)"  # 合并，或给默认提示
        except FileNotFoundError:        # 模型读了不存在的文件
            result = "Error: FileNotFoundError: File not found"  # 把错误变成文字
        except PermissionError as e:     # 权限问题（写被拒 / 命令被拦 / 路径越界）
            result = f"Error: PermissionError: {str(e)}"  # 把错误变成文字
        except subprocess.TimeoutExpired:  # 命令执行超时
            result = "Error: TimeoutError: Command took too long"  # 把错误变成文字
        except Exception as e:           # 其它任何未预料到的异常
            result = f"Error: {type(e).__name__}: {str(e)}"  # 把错误类型+信息变成文字

        # (4) 判断是否结束
        if DONE:                         # 如果已经调用 final_answer()
            print(f"✓ Task complete: {FINAL_RESULT}")  # 打印成功信息
            break                        # 跳出循环，Agent 收工

        # (5) 把观察结果喂回历史
        messages.append({"role": "user", "content": result})  # 把结果或错误作为 user 消息加回历史，进入下一轮

    if not DONE:                         # 转满 MAX_STEPS 圈仍没完成
        print(f"✗ Max steps ({MAX_STEPS}) reached without final_answer()")  # 提示未完成任务

# -------------------- 7. 入口 --------------------

if __name__ == "__main__":             # 只有当本文件被直接运行时
    main()                              # 才启动 Agent（被 import 时不自动跑）
