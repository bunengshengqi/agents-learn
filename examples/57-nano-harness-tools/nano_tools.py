# ============================================================
# nano_tools.py  (Day57 配套：工具与沙箱详解，逐行中文注释版)
# 教学用，非生产。展示 Nano Harness 的 4 个工具、路径限制 safe_path、
# 执行沙箱（受限全局作用域）、错误隔离，以及「好的工具设计 / 坏的工具设计」对照。
# 运行：python nano_tools.py   （无需 HF_TOKEN，本文件只演示工具与沙箱本身）
# ============================================================

import os                              # 导入 os：仅用于反例演示 os.system（切勿实际使用）
import subprocess                      # 导入 subprocess：在受限环境下执行 shell 命令
from pathlib import Path              # 导入 Path：安全拼接/解析文件路径

# -------------------- 0. 配置：沙箱的安全参数都集中在这里 --------------------

WORKSPACE = Path(__file__).resolve().parent   # 演示用：指向本文件所在目录，保证 demo 可跑；真实 harness 用 Path.cwd()
MAX_CHARS = 8000                      # 输出上限：任何工具返回的文本最多 8000 字符
TIMEOUT_S = 30                        # 超时：单条命令最多跑 30 秒
ALLOW_WRITE = False                   # 写开关：默认禁止写文件，必须显式打开才允许
ALLOW_COMMANDS = ["ls", "cat", "pwd", "echo", "head", "tail", "wc", "rg"]  # 命令白名单：只有这 8 个能跑

# -------------------- 1. 小工具：clip 截断文本 --------------------

def clip(text, n):                    # 把文本截到最多 n 个字符
    text = "" if text is None else str(text)   # 确保是字符串，None 当空串
    return text if len(text) <= n else text[:n] + "…"  # 超长就截断并加省略号

# -------------------- 2. 路径限制 safe_path：所有碰路径的入口都过它 --------------------

def safe_path(user_input):            # 确保用户给的路径落在工作目录内
    requested = (WORKSPACE / user_input).resolve()  # 拼到工作目录并解析成绝对路径（处理 ../）
    if not requested.is_relative_to(WORKSPACE):     # 解析后若不在工作目录内
        raise ValueError(f"Path {user_input} escapes workspace")  # 越界，拒绝
    return requested                  # 返回安全的绝对路径

# -------------------- 3. 四个工具：每个都是 Agent 的「手」，且自带安检 --------------------

def list_dir(path="."):               # 工具1：列出目录内容
    p = safe_path(path)                 # 路径先过安检
    if not p.is_dir():                  # 不是目录就报错
        raise NotADirectoryError(str(p))
    return sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir())  # 目录名加 / 区分

def read_file(path, max_chars=4000):  # 工具2：读文件，带大小上限
    p = safe_path(path)                 # 路径先过安检
    content = p.read_text(encoding="utf-8", errors="replace")  # 读文本，乱码替换而非崩溃
    return clip(content, min(max_chars, MAX_CHARS))  # 双重上限：取两者较小值

def write_file(path, content):        # 工具3：写文件（受 ALLOW_WRITE 开关控制）
    if not ALLOW_WRITE:                 # 写开关没开
        raise PermissionError("write_file disabled")  # 直接拒绝
    p = safe_path(path)                 # 路径先过安检
    p.parent.mkdir(parents=True, exist_ok=True)  # 必要时建父目录
    p.write_text(str(content), encoding="utf-8")  # 写文件
    return f"Wrote {len(str(content))} bytes to {p}"  # 返回写入字节数

def exec_cmd(args):                    # 工具4：执行 shell 命令，仅白名单
    if args[0] not in ALLOW_COMMANDS:   # 命令不在白名单
        raise PermissionError(f"Command '{args[0]}' not allowed")  # 拒绝
    try:
        result = subprocess.run(        # 在超时内执行命令
            args,
            capture_output=True,         # 捕获 stdout/stderr
            timeout=TIMEOUT_S,           # 最多 30 秒
            text=True                    # 以文本模式返回
        )
        output_parts = []                # 收集输出
        if result.stdout:                # 有标准输出
            output_parts.append(f"stdout:\n{result.stdout}")
        if result.stderr:                # 有标准错误
            output_parts.append(f"stderr:\n{result.stderr}")
        output = "\n\n".join(output_parts) or f"(exit code {result.returncode} with no output)"  # 合并或给退出码
        return clip(output, MAX_CHARS)   # 截断后返回
    except subprocess.TimeoutExpired:    # 命令超时
        return "Error: Command timed out"  # 返回超时提示

# -------------------- 4. 结束信号 final_answer --------------------

DONE = False                            # 全局：是否完成
FINAL_RESULT = None                     # 全局：最终答案

def final_answer(value):               # 模型完成时调用
    global DONE, FINAL_RESULT            # 修改全局
    DONE = True                          # 标记完成
    FINAL_RESULT = value                 # 存答案
    return value                         # 返回

# -------------------- 5. 执行沙箱：受限全局作用域 --------------------

exec_globals = {                       # 只暴露这 5 个函数给被执行代码
    # __builtins__ 默认应清空；按课程建议，若需要 str/len/print 这类安全内置，
    # 显式放一个"极小白名单"，而不是继承 Python 全套默认内置。
    "__builtins__": {"str": str, "len": len, "print": print},
    "list_dir": list_dir,               # 只允许用这 4 个工具
    "read_file": read_file,
    "write_file": write_file,
    "exec_cmd": exec_cmd,
    "final_answer": final_answer        # 以及结束信号
}

# （演示用）一段"agent 生成的代码"，丢进受限环境执行
AGENT_CODE = """
files = list_dir(".")
head = read_file("nano_tools.py", max_chars=300)
final_answer("files: " + str(files) + "\\nhead of nano_tools.py: " + head)
"""

def run_in_sandbox(code):              # 在沙箱里执行 agent 代码，并做错误隔离
    try:
        exec(code, exec_globals)        # 在受限环境执行
        return "executed" if not DONE else f"done: {FINAL_RESULT}"  # 返回状态
    except Exception as e:              # 任何异常都被接住
        # 错误变成观察：作为消息回给模型，让它下一轮换思路（错误即观察）
        return f"Error: {type(e).__name__}: {str(e)}"

# -------------------- 6. 好工具设计 vs 坏工具设计（对照） --------------------

def good_tool(user_input, max_result_size=1000):  # ✅ 好的工具：四步齐全
    """
    1. 校验并限制输入
    2. 执行操作
    3. 限制输出大小
    4. 返回安全结果
    """
    if not isinstance(user_input, str):        # 1. 校验输入类型
        raise TypeError("user_input must be string")
    path = safe_path(user_input)               # 1. 路径限制
    result = path.read_text()                  # 2. 执行操作
    return clip(result, min(max_result_size, MAX_CHARS))  # 3+4. 限制输出并返回

# 下面四个是"故意写错"的反例，仅供对照，不会被调用，也切勿在生产使用：

def bad_tool_1(path):                    # ✗ 反例1：不校验输入/路径
    return open(path).read()             # 能读任何文件，包括 /etc/passwd

def bad_tool_2(query):                   # ✗ 反例2：不限制输出
    return database.query(query)         # 可能返回几 TB 数据，撑爆上下文

def bad_tool_3(url):                     # ✗ 反例3：不做错误处理
    return requests.get(url).text        # 可能超时/卡死

def bad_tool_4(command):                 # ✗ 反例4：完全信任 agent
    os.system(command)                   # agent 能跑 rm -rf / ，极其危险

# -------------------- 7. 演示：能跑通看效果 --------------------

if __name__ == "__main__":              # 直接运行本文件时
    print("list_dir('.'):", list_dir(".")[:3], "...")   # 演示列目录（只打印前 3 个）
    try:
        print("read_file('../etc/passwd'):")             # 演示越界被拦
        read_file("../etc/passwd")
    except ValueError as e:
        print("  -> 被 safe_path 拦截:", e)

    print("\nexec_cmd(['rm','-rf','/']):")               # 演示危险命令被拦
    try:
        exec_cmd(["rm", "-rf", "/"])
    except PermissionError as e:
        print("  -> 被白名单拦截:", e)

    print("\n沙箱执行示例 agent 代码:")
    print(" ", run_in_sandbox(AGENT_CODE))              # 演示在沙箱里跑一段代码
