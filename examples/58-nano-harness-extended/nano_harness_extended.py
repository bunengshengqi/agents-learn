# ============================================================
# nano_harness_extended.py  (Day58 配套：扩展 Nano Harness，逐行中文注释版)
# 在基础 harness 上新增两个工具：web_fetch（抓网页）、hf_search（搜 Hugging Face Hub）
# 教学用，非生产。运行：
#   export HF_TOKEN="hf_..."
#   export NANO_MODEL="zai-org/GLM-5.1"
#   python nano_harness_extended.py
# （不设 HF_TOKEN 也能跑，只是 hf_search 会返回错误提示；web_fetch 不依赖 token）
# ============================================================

import io                              # io：用 StringIO 捕获代码的标准输出
import json                            # json：解析 HF API 返回的 JSON
import os                              # os：读取环境变量（模型名、token、接口地址）
import re                              # re：用正则从模型回复里抠出 ```python 代码块
import subprocess                      # subprocess：执行白名单内的 shell 命令
import urllib.error                    # urllib.error：捕获网络错误
import urllib.request                  # urllib.request：发 HTTP 请求（抓网页/搜 HF）
from contextlib import redirect_stderr, redirect_stdout  # 重定向：把 print 改道到 buffer
from pathlib import Path              # Path：安全拼接/解析路径
from openai import OpenAI             # OpenAI SDK：调用兼容 /v1 的模型接口

# -------------------- 配置区 --------------------

TASK = "Search for bert models on Hugging Face and summarize top 3."  # 任务：搜 bert 模型并总结前 3 个
MODEL = os.getenv("NANO_MODEL", "zai-org/GLM-5.1")      # 模型：优先读 NANO_MODEL，缺省 GLM-5.1
BASE_URL = os.getenv("OPENAI_BASE_URL", "https://router.huggingface.co/v1")  # 接口：HF 的 OpenAI 兼容路由
API_KEY = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY", "")  # 密钥：优先 HF_TOKEN，否则 OpenAI key
WORKSPACE = str(Path.cwd())            # 工作目录：文件操作限制在此
MAX_STEPS = 50                         # 步数上限：最多 50 圈
TIMEOUT_S = 30                         # 超时：网络请求/命令最多 30 秒
MAX_CHARS = 8000                       # 输出上限：文本最多 8000 字符
ALLOW_WRITE = False                    # 写开关：默认禁止写文件
ALLOW_COMMANDS = ["ls", "cat", "pwd", "echo", "head", "tail", "wc", "rg"]  # 命令白名单
TEMPERATURE = 0.2                      # 温度：低，输出更确定

# -------------------- 系统提示词：把新工具也告诉模型 --------------------

SYSTEM_PROMPT = f"""You are a code-first agent.
Reply with executable Python only.

Tools:
  - list_dir(path='.') → list files
  - read_file(path, max_chars=4000) → read file
  - write_file(path, content) → write file (only if ALLOW_WRITE=True)
  - exec_cmd(args) → run allowed command
  - web_fetch(url, max_bytes=10000) → fetch webpage
  - hf_search(query, limit=5) → search HF Hub

Allowed commands: {ALLOW_COMMANDS}
Writes enabled: {ALLOW_WRITE}

When done, call final_answer(result).
Output only Python code, no prose."""

# -------------------- 小工具：clip 截断 --------------------

def clip(x, n=MAX_CHARS):              # 把任意对象转字符串后截断到 n 字符
    s = str(x)                         # 转字符串（工具返回可能是列表/字典）
    return s[:n] + f"\n...[truncated]" if len(s) > n else s  # 超长就截断并标注

# -------------------- 主函数：所有工具与循环都定义在里面 --------------------

def main():                            # 主函数，工具嵌套定义以便共享状态
    ws = Path(WORKSPACE).resolve()     # 工作空间绝对路径
    done = False                       # 局部：任务是否完成
    final_result = None                # 局部：最终答案

    def safe_path(path):               # 路径限制：防止目录穿越
        p = (ws / path).resolve()      # 拼到工作目录并解析
        try:
            p.relative_to(ws)          # 判断是否在 ws 内
        except ValueError:
            raise ValueError(f"Path escapes workspace: {path}")  # 越界拒绝
        return p

    def list_dir(path="."):            # 工具1：列目录
        p = safe_path(path)
        return sorted(x.name + ("/" if x.is_dir() else "") for x in p.iterdir())

    def read_file(path, max_chars=4000):  # 工具2：读文件（带大小上限）
        p = safe_path(path)
        return clip(p.read_text(errors="replace"), min(max_chars, MAX_CHARS))

    def write_file(path, content):     # 工具3：写文件（受 ALLOW_WRITE 控制）
        if not ALLOW_WRITE:
            raise PermissionError("write_file disabled")
        p = safe_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(str(content), encoding="utf-8")
        return f"Wrote {len(str(content))} bytes"

    def exec_cmd(args):                # 工具4：跑白名单内命令
        if args[0] not in ALLOW_COMMANDS:
            raise PermissionError(f"Command {args[0]} not allowed")
        result = subprocess.run(args, capture_output=True, timeout=TIMEOUT_S, text=True)
        output_parts = []
        if result.stdout:
            output_parts.append(f"stdout:\n{result.stdout}")
        if result.stderr:
            output_parts.append(f"stderr:\n{result.stderr}")
        output = "\n\n".join(output_parts) or f"(exit code {result.returncode} with no output)"
        return clip(output, MAX_CHARS)

    # ===== 扩展工具 1：web_fetch（抓网页） =====
    def web_fetch(url, max_bytes=10000):  # 抓取指定网址的内容，带字节上限
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT_S) as r:  # 带超时地发请求
                content = r.read(max_bytes)                # 最多读 max_bytes 字节
                return content.decode("utf-8", errors="replace")  # 解码成文本，乱码替换
        except Exception as e:
            return f"Error: {type(e).__name__}: {str(e)}"  # 出错返回字符串，让模型能反应

    # ===== 扩展工具 2：hf_search（搜 Hugging Face Hub） =====
    def hf_search(query, resource_type="models", limit=5):  # 搜 HF Hub，默认搜模型
        if not API_KEY:
            return "Error: HF_TOKEN not set"               # 没 token 直接报错提示
        try:
            url = f"https://huggingface.co/api/{resource_type}"  # 资源类型：models/datasets 等
            req = urllib.request.Request(
                f"{url}?search={query}&limit={limit}",       # 拼查询参数
                headers={"Authorization": f"Bearer {API_KEY}"}  # 带鉴权头
            )
            with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:  # 带超时请求
                data = json.loads(r.read())                 # 解析返回的 JSON
                return [                                    # 整理成简洁结果列表
                    {
                        "id": item.get("id"),
                        "downloads": item.get("downloads", 0),
                        "description": item.get("description", "")[:100]
                    }
                    for item in data[:limit]                # 只取前 limit 个
                ]
        except Exception as e:
            return f"Error: {str(e)}"                       # 出错返回字符串

    def final_answer(value):            # 结束信号：模型完成时调用
        nonlocal done, final_result     # 修改外层 main 的局部变量
        done = True
        final_result = value
        return value

    # ===== 初始化客户端 =====
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)  # 指向 HF router（OpenAI 兼容）

    messages = [                        # 消息历史 = 短期记忆
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": TASK}
    ]

    # ===== 主循环：和 Day56 一样，只是工具更多了 =====
    for step in range(MAX_STEPS):       # 最多 50 圈
        print(f"\n[Step {step + 1}]")

        response = client.responses.create(  # 调模型（Responses API）
            model=MODEL, temperature=TEMPERATURE, input=messages
        )
        content = response.output_text       # 模型回复（一段 Python）
        print(f"Model:\n{content[:300]}...")  # 预览前 300 字

        messages.append({"role": "assistant", "content": content})  # 存模型代码

        try:
            # 用正则抠出 ```python ... ``` 代码块
            code_match = re.search(r"```python\n(.*?)\n```", content, re.DOTALL)
            if not code_match:
                raise ValueError("No Python code block found")  # 没找到代码块就报错

            stdout_buffer = io.StringIO()    # 接标准输出
            stderr_buffer = io.StringIO()    # 接标准错误
            exec_globals = {                 # 受限全局环境：新增了 web_fetch / hf_search / json
                "__builtins__": {},          # 清空内置函数（沙箱核心）
                "list_dir": list_dir,
                "read_file": read_file,
                "write_file": write_file,
                "exec_cmd": exec_cmd,
                "web_fetch": web_fetch,      # 新工具注入
                "hf_search": hf_search,      # 新工具注入
                "final_answer": final_answer,
                "json": json                 # 顺手放出 json，方便解析
            }
            with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
                exec(code_match.group(1), exec_globals)  # 在受限环境执行抠出的代码

            stdout_text = stdout_buffer.getvalue().strip()
            stderr_text = stderr_buffer.getvalue().strip()

            if done:                         # 调了 final_answer()
                result = f"Final answer: {clip(final_result)}"
            else:                            # 否则收集观察
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
            result = f"Error: {type(e).__name__}: {str(e)}"  # 其他异常变观察

        if done:
            print(f"✓ Task complete: {final_result}")
            break
        messages.append({"role": "user", "content": result})  # 观察喂回历史

    if not done:
        print(f"✗ Max steps reached")       # 转满 50 圈仍没完成

# -------------------- 练习：你可以再加的 3 个工具（按需启用） --------------------
# 下面只是参考实现，未接入上面的 harness。想用就把函数挪进 main() 并加进 exec_globals。
#
# def git_log(limit=10):
#     """最近 git 提交。需先把 'git' 加进 ALLOW_COMMANDS。"""
#     return exec_cmd(["git", "log", "--oneline", f"-{limit}"])
#
# def json_parse(json_string):
#     """安全解析 JSON。"""
#     try:
#         return json.loads(json_string)
#     except json.JSONDecodeError as e:
#         return f"Error: {str(e)}"
#
# def compute_stats(numbers):
#     """计算 min/max/mean/count。"""
#     nums = list(map(float, numbers))
#     return {"min": min(nums), "max": max(nums),
#             "mean": sum(nums) / len(nums), "count": len(nums)}

if __name__ == "__main__":              # 直接运行本文件时
    main()                              # 启动扩展版 Agent
