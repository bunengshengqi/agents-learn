# Day58 — Unit 6: Hands-On 扩展 Nano Harness（加两个新工具）

> 课程地址：https://huggingface.co/learn/context-course/unit6/hands-on  
> 课件源码：https://github.com/huggingface/context-course/blob/main/units/en/unit6/hands-on.mdx  
> 上一节：Day57 - 工具与沙箱详解

---

## 0. 这节课在干嘛？一句话说清

Day56 你读了循环，Day57 你拆了工具与沙箱。这节课**亲手扩展开**——给 Nano Harness 加两个新工具：

- `web_fetch(url)` —— 让 Agent 能上网抓网页；
- `hf_search(query)` —— 让 Agent 能搜 Hugging Face Hub 上的模型/数据集。

加完之后，同一个循环、同一套安全模型，**不用改一行控制流**，Agent 就多了「触网」和「搜模型」两种能力。这正是 Day57 说的「好工具设计」的实战落地。

> 💡 **大佬视角**：扩展 Agent 的能力，本质就是**加工具**。只要每个新工具都守 Day57 那四步（校验输入、限制输出、加超时、错误变字符串），你就能安全地给 Agent 接上整个世界。

配套可运行代码已放在 `examples/58-nano-harness-extended/nano_harness_extended.py`（完整扩展版 harness，逐行注释，已通过语法检查；运行时需 `HF_TOKEN` 才能用 `hf_search`，`web_fetch` 不依赖 token）。

---

## 1. 扩展 1：`web_fetch` —— 让 Agent 能上网

```python
import urllib.request
import urllib.error

def web_fetch(url, max_bytes=10000):
    """Fetch web page content with size limit."""
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_S) as response:
            content = response.read(max_bytes + 1)        # ① 字节上限，防大响应
            if len(content) > max_bytes:
                content = content[:max_bytes] + b"\n...[truncated]"
            return content.decode("utf-8", errors="replace")  # 解码，乱码替换
    except urllib.error.URLError as e:
        return f"Error: Failed to fetch {url}: {e}"        # ② 错误变字符串
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"
```

三个安全要点（小白版）：

1. **字节上限 `max_bytes`**：网页可能几百 MB，截断到 10000 字节，防塞爆上下文。
2. **`timeout=TIMEOUT_S`**：请求最多 30 秒，防卡死。
3. **错误返回字符串**：失败不抛异常，而是把错误当结果返回，**让模型自己换 URL 或换做法**。

系统提示词里也要告诉模型有这个新工具：

```python
SYSTEM_PROMPT = """
...
Tools:
  - web_fetch(url, max_bytes=10000) → fetch webpage
...
"""
```

模型使用时就这么写：

```python
content = web_fetch("https://huggingface.co/")           # 抓首页
content = web_fetch("https://huggingface.co/", max_bytes=5000)  # 只要前 5000 字节
```

---

## 2. 扩展 2：`hf_search` —— 让 Agent 能搜 Hugging Face

```python
def hf_search(query, resource_type="models", limit=5):
    """Search Hugging Face Hub (requires HF_TOKEN)."""
    if not API_KEY:                                        # ① 没 token 先报错提示
        return "Error: HF_TOKEN not set. Can't access Hugging Face API."

    try:
        url = f"https://huggingface.co/api/{resource_type}"   # 资源类型：models/datasets/...
        params = f"?search={query}&limit={limit}"             # 查询参数
        req = urllib.request.Request(
            url + params,
            headers={"Authorization": f"Bearer {API_KEY}"}    # ② token 从环境变量来，不写进代码
        )
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as response:
            data = json.loads(response.read())                # 解析 JSON

            results = []
            for item in data[:limit]:                         # ③ 只取前 limit 个
                results.append({
                    "id": item.get("id"),
                    "downloads": item.get("downloads", 0),
                    "description": item.get("description", "")[:200]
                })
            return results
    except Exception as e:
        return f"Error: {type(e).__name__}: {str(e)}"         # ④ 错误变字符串
```

安全/设计要点：

- **API key 留在环境变量**：模型拿不到你的 token，只拿到搜索结果。
- **`limit` 限制返回条数**：防止返回上千条撑爆上下文。
- **错误被捕获并返回**：网络抖一下，Agent 能重试而不是崩。

系统提示词加上：`- hf_search(query, resource_type='models', limit=10) → search HF`。模型这么用：

```python
results = hf_search("bert", resource_type="models", limit=5)
final_answer(results)
```

---

## 3. 完整扩展版 harness：循环一行没改

把两个工具加进 `nano_harness.py` 后，关键变化只有两处：

**① 系统提示词**列出 6 个工具（原来 4 个 + `web_fetch` + `hf_search`）。

**② `exec_globals` 注入新工具**：

```python
exec_globals = {
    "__builtins__": {},
    "list_dir": list_dir,
    "read_file": read_file,
    "write_file": write_file,
    "exec_cmd": exec_cmd,
    "web_fetch": web_fetch,      # ← 新工具
    "hf_search": hf_search,      # ← 新工具
    "final_answer": final_answer,
    "json": json
}
```

> 💡 注意：**主循环完全没动**。这正是「工具化」的威力——Agent 的能力边界 = 工具集合，控制流（循环、解析、沙箱、错误隔离）保持稳定。换模型、加工具，都不用重写循环。

扩展版完整代码见 `examples/58-nano-harness-extended/nano_harness_extended.py`（含逐行注释，用了 Responses API，对 HF router 和直连 OpenAI 都通用）。它保留了和基座完全一致的安全模型：`write_file` 仍默认关闭、`exec()` 仍无默认内置、每轮仍把 stdout/stderr/答案/错误回喂。

---

## 4. 怎么跑起来

```bash
export HF_TOKEN="hf_..."
export NANO_MODEL="zai-org/GLM-5.1"
python nano_harness_extended.py
```

- Inference Providers 会把请求自动路由到后端模型供应商。
- 想换别的 HF 文本生成模型？只改 `NANO_MODEL`，**循环和工具集完全不变**。
- 不设 `HF_TOKEN` 也能跑：`web_fetch` 正常，`hf_search` 会返回「HF_TOKEN not set」的错误提示（模型能读到并应对）。

---

## 5. 练习：自己再加 3 个工具

课程留了作业，照 Day57 的四步来写：

```python
# ① git_log：先看 git 提交（先把 "git" 加进 ALLOW_COMMANDS）
def git_log(limit=10):
    """Get recent git commits."""
    return exec_cmd(["git", "log", "--oneline", f"-{limit}"])

# ② json_parse：安全解析 JSON
def json_parse(json_string):
    """Parse JSON safely."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        return f"Error: {str(e)}"

# ③ compute_stats：算 min/max/mean
def compute_stats(numbers):
    """Compute min, max, mean."""
    nums = list(map(float, numbers))
    return {
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
        "count": len(nums)
    }
```

把函数挪进 `main()`，加进 `exec_globals`，并在系统提示词里列出来，就能用。观察 Agent 的轨迹会怎么随工具变多而变化——这正是「能力边界 = 工具集合」的直观体验。

> 💡 `git_log` 要先把 `"git"` 加进 `ALLOW_COMMANDS`，因为 `exec_cmd` 走白名单。其它两个（`json_parse`/`compute_stats`）是纯计算，不需要命令权限。

---

## 6. 大佬总结（Key Takeaways）

1. **工具把 Agent 连向世界**：每个工具都要有大小上限、超时、清晰的错误字符串，好让 Agent 能自我调整。
2. **加工具几乎零成本改控制流**：改系统提示词 + 注入 `exec_globals`，循环一行不动。
3. **同一套循环跑任意 HF 模型**：换 `NANO_MODEL` 即可，工具集不变。
4. **安全模型全程继承**：写文件默认关、无默认内置、错误即观察，一个都没少。

> 💡 **一句话带走**：扩展 Agent = 加工具。只要每个工具守住「输入校验、输出限制、超时、错误变观察」这四道门，你就能安全地给它接上网页、HF Hub、git、计算器……Agent 的能力边界，就是你愿意给它开多少道门。

---

## 7. 下一节预告

> **Unit 6 Quiz**：检验你对 Nano Harness 和 Agent 内部机制（循环、工具、沙箱）的掌握程度，然后整个课程收官。
