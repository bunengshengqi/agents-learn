# 第28天真实 API 版 Alfred：使用 OpenAI-compatible 接口调用你配置的大模型。  # 说明本文件用途
from __future__ import annotations  # 启用延迟类型注解

import json  # 导入 JSON 解析和序列化工具
import os  # 导入环境变量工具
import urllib.error  # 导入网络错误类型
import urllib.parse  # 导入 URL 编码工具
import urllib.request  # 导入标准库 HTTP 请求工具
from pathlib import Path  # 导入路径工具

from common_alfred_tools import guest_info_tool  # 导入本课程的本地宾客检索工具

ROOT_DIR = Path(__file__).resolve().parents[2]  # 计算项目根目录
ENV_FILE = ROOT_DIR / ".env"  # 定位项目根目录的 .env 文件
SYSTEM_PROMPT = (  # 定义系统提示词
    "你是 Alfred，一个 Gala 晚会智能体。你必须根据任务选择工具，拿到 Observation 后再回答。 "  # 说明身份和工具原则
    "你可以使用工具：guest_info, weather_info, hub_stats, web_search。 "  # 告诉模型可用工具
    "如果需要工具，只输出 JSON：{\"thought\":\"...\",\"action\":{\"name\":\"工具名\",\"input\":\"参数\"}}。 "  # 规定工具调用 JSON
    "如果已经可以最终回答，只输出 JSON：{\"thought\":\"...\",\"final\":\"最终中文回答\"}。 "  # 规定最终回答 JSON
    "不要编造工具结果，不要使用 Markdown 代码块。"  # 禁止伪造观察结果
)  # 结束系统提示词

def load_env_file(path: Path) -> None:  # 定义读取 .env 文件的函数
    if not path.exists():  # 判断 .env 是否存在
        return  # 不存在就直接返回
    for raw_line in path.read_text(encoding="utf-8").splitlines():  # 遍历 .env 每一行
        line = raw_line.strip()  # 去掉首尾空白
        if not line or line.startswith("#") or "=" not in line:  # 跳过空行、注释和无效行
            continue  # 继续下一行
        key, value = line.split("=", 1)  # 按第一个等号切分键值
        key = key.strip()  # 清理变量名
        value = value.strip().strip('"').strip("'")  # 清理变量值和引号
        os.environ.setdefault(key, value)  # 只在环境变量未设置时写入

def require_env(name: str) -> str:  # 定义必填环境变量读取函数
    value = os.getenv(name)  # 从系统环境读取变量
    if not value:  # 判断变量是否为空
        raise RuntimeError(f"缺少环境变量 {name}，请先在项目根目录 .env 中配置。")  # 抛出友好错误
    return value  # 返回环境变量值

def build_chat_url(base_url: str) -> str:  # 定义构造 chat completions 地址的函数
    base = base_url.rstrip("/")  # 去掉末尾斜杠
    if base.endswith("/chat/completions"):  # 判断用户是否已经填写完整接口路径
        return base  # 直接返回完整接口路径
    return base + "/chat/completions"  # 拼接 OpenAI-compatible 聊天接口路径

def post_json(url: str, api_key: str, payload: dict) -> dict:  # 定义发送 JSON 请求的函数
    body = json.dumps(payload).encode("utf-8")  # 把请求体编码成 UTF-8 字节
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}  # 构造鉴权和内容类型头
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")  # 构造 HTTP POST 请求
    try:  # 开始捕获网络异常
        with urllib.request.urlopen(request, timeout=90) as response:  # 发送请求并设置超时
            return json.loads(response.read().decode("utf-8"))  # 解析并返回 JSON 响应
    except urllib.error.HTTPError as exc:  # 捕获 HTTP 错误
        error_text = exc.read().decode("utf-8", errors="replace")  # 读取错误响应文本
        raise RuntimeError(f"模型接口 HTTP {exc.code}: {error_text}") from exc  # 抛出带上下文的错误
    except urllib.error.URLError as exc:  # 捕获网络连接错误
        raise RuntimeError(f"模型接口连接失败: {exc}") from exc  # 抛出连接失败错误

def call_llm(messages: list[dict[str, str]]) -> str:  # 定义调用真实大模型的函数
    load_env_file(ENV_FILE)  # 加载项目根目录 .env
    api_key = require_env("OPENAI_API_KEY")  # 读取 API Key
    base_url = require_env("OPENAI_BASE_URL")  # 读取 Base URL
    model = require_env("OPENAI_MODEL")  # 读取模型名称
    url = build_chat_url(base_url)  # 构造完整请求地址
    payload = {"model": model, "messages": messages, "temperature": 0.1}  # 构造聊天补全请求体
    data = post_json(url, api_key, payload)  # 发起真实 API 请求
    return data["choices"][0]["message"]["content"] or ""  # 返回模型输出文本

def extract_json(text: str) -> dict | None:  # 定义从模型输出中提取 JSON 的函数
    start = text.find("{")  # 查找第一个左花括号
    end = text.rfind("}")  # 查找最后一个右花括号
    if start == -1 or end == -1 or end <= start:  # 判断是否没有完整 JSON
        return None  # 返回空表示解析失败
    try:  # 开始捕获 JSON 解析异常
        return json.loads(text[start : end + 1])  # 解析并返回 JSON 对象
    except json.JSONDecodeError:  # 捕获 JSON 格式错误
        return None  # 返回空表示解析失败

def real_weather_info(location: str) -> str:  # 定义真实天气工具
    safe_location = urllib.parse.quote(location)  # 对地点做 URL 编码
    url = f"https://wttr.in/{safe_location}?format=j1"  # 使用无需 key 的 wttr.in 天气接口
    try:  # 开始捕获天气请求异常
        with urllib.request.urlopen(url, timeout=20) as response:  # 请求天气接口
            data = json.loads(response.read().decode("utf-8"))  # 解析天气 JSON
        current = data["current_condition"][0]  # 读取当前天气
        condition = current["weatherDesc"][0]["value"]  # 读取天气描述
        temp_c = current["temp_C"]  # 读取摄氏温度
        wind = current["windspeedKmph"]  # 读取风速
        return f"{location} 当前天气：{condition}，温度 {temp_c}°C，风速 {wind} km/h。"  # 返回天气摘要
    except Exception as exc:  # 捕获所有天气工具异常
        return f"天气工具调用失败：{exc}"  # 返回工具失败信息

def real_hub_stats(author: str) -> str:  # 定义真实 Hugging Face Hub 统计工具
    safe_author = urllib.parse.quote(author)  # 对作者名做 URL 编码
    url = f"https://huggingface.co/api/models?author={safe_author}&sort=downloads&direction=-1&limit=1"  # 构造 Hub 模型查询地址
    try:  # 开始捕获 Hub 请求异常
        with urllib.request.urlopen(url, timeout=30) as response:  # 请求 Hugging Face Hub API
            data = json.loads(response.read().decode("utf-8"))  # 解析 Hub JSON
        if not data:  # 判断是否没有模型结果
            return f"没有找到 {author} 的 Hugging Face Hub 模型统计。"  # 返回空结果说明
        model = data[0]  # 取下载量最高的第一个模型
        model_id = model.get("modelId", "unknown-model")  # 读取模型 ID
        downloads = model.get("downloads", 0)  # 读取下载量
        return f"{author} 下载量最高的模型是 {model_id}，下载量约 {downloads:,}。"  # 返回 Hub 统计摘要
    except Exception as exc:  # 捕获所有 Hub 工具异常
        return f"Hub 统计工具调用失败：{exc}"  # 返回工具失败信息

def real_web_search(query: str) -> str:  # 定义真实网络搜索工具
    safe_query = urllib.parse.quote(query)  # 对搜索词做 URL 编码
    url = f"https://api.duckduckgo.com/?q={safe_query}&format=json&no_html=1&skip_disambig=1"  # 构造 DuckDuckGo Instant Answer 地址
    try:  # 开始捕获搜索请求异常
        with urllib.request.urlopen(url, timeout=30) as response:  # 请求 DuckDuckGo 接口
            data = json.loads(response.read().decode("utf-8"))  # 解析搜索 JSON
        abstract = data.get("AbstractText") or data.get("Heading")  # 优先读取摘要文本
        if abstract:  # 判断是否有摘要
            return f"搜索结果摘要：{abstract}"  # 返回摘要结果
        topics = data.get("RelatedTopics", [])  # 读取相关主题列表
        first_topic = topics[0].get("Text") if topics and isinstance(topics[0], dict) else ""  # 尝试读取第一条主题
        return f"搜索结果：{first_topic or '没有获得明确摘要，建议更换关键词或接入正式搜索 API。'}"  # 返回搜索结果
    except Exception as exc:  # 捕获所有搜索工具异常
        return f"网络搜索工具调用失败：{exc}"  # 返回工具失败信息

TOOLS = {  # 注册真实工具表
    "guest_info": guest_info_tool,  # 注册本地宾客检索工具
    "weather_info": real_weather_info,  # 注册真实天气工具
    "hub_stats": real_hub_stats,  # 注册真实 Hub 统计工具
    "web_search": real_web_search,  # 注册真实网络搜索工具
}  # 结束工具表

def run_tool(action: dict) -> str:  # 定义工具执行函数
    name = str(action.get("name", ""))  # 读取工具名称
    tool_input = str(action.get("input", ""))  # 读取工具输入
    tool = TOOLS.get(name)  # 根据名称查找工具函数
    if tool is None:  # 判断工具是否不存在
        return f"未知工具：{name}。可用工具：{', '.join(TOOLS)}。"  # 返回未知工具错误
    return tool(tool_input)  # 执行工具并返回 Observation

def run_real_alfred(query: str, max_steps: int = 5) -> str:  # 定义真实端到端 Agent 主循环
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": query}]  # 初始化消息列表
    for step in range(max_steps):  # 最多执行指定步数
        model_text = call_llm(messages)  # 调用真实大模型
        parsed = extract_json(model_text)  # 解析模型 JSON 输出
        if parsed is None:  # 判断模型是否没有返回合法 JSON
            return f"模型没有返回合法 JSON，原始输出：\n{model_text}"  # 返回原始输出方便排错
        if "final" in parsed:  # 判断模型是否给出最终答案
            return str(parsed["final"])  # 返回最终答案
        action = parsed.get("action")  # 读取工具调用动作
        if not isinstance(action, dict):  # 判断 action 是否格式错误
            return f"模型 Action 格式错误：{parsed}"  # 返回格式错误
        observation = run_tool(action)  # 执行工具得到 Observation
        messages.append({"role": "assistant", "content": json.dumps(parsed, ensure_ascii=False)})  # 保存模型动作
        messages.append({"role": "user", "content": f"Observation from {action.get('name')}: {observation}"})  # 把观察结果交回模型
    return "达到最大工具调用步数，Agent 停止运行。请缩小问题范围或提高 max_steps。"  # 返回步数耗尽提示

def main() -> None:  # 定义脚本入口函数
    query = "I need to speak with Dr. Nikola Tesla about recent advancements in wireless energy. Can you help me prepare?"  # 准备默认真实测试问题
    print(run_real_alfred(query))  # 调用真实 Alfred 并打印结果

if __name__ == "__main__":  # 判断是否直接执行脚本
    main()  # 调用脚本入口
