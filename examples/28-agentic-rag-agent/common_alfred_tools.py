# 第28天公共工具文件：用离线数据模拟 Alfred 的所有工具。  # 说明本文件用途
from __future__ import annotations  # 让类型注解在较新 Python 中保持兼容

GUESTS = {  # 保存模拟的宾客资料库
    "lady ada lovelace": {  # 使用标准化姓名作为检索键
        "name": "Lady Ada Lovelace",  # 保存宾客姓名
        "relation": "a respected mathematician and long-time friend",  # 保存宾客关系
        "background": "Known for early computing ideas and analytical engine notes.",  # 保存宾客背景
        "email": "ada.lovelace@example.com",  # 保存联系邮箱
        "project": "Exploring symbolic reasoning notes for mechanical computation.",  # 保存当前项目
    },  # 结束 Ada 的资料
    "dr nikola tesla": {  # 使用标准化姓名作为检索键
        "name": "Dr. Nikola Tesla",  # 保存宾客姓名
        "relation": "an old university friend",  # 保存宾客关系
        "background": "Inventor interested in wireless energy transmission.",  # 保存宾客背景
        "email": "nikola.tesla@example.com",  # 保存联系邮箱
        "project": "Discussing a new wireless energy transmission system.",  # 保存当前项目
    },  # 结束 Tesla 的资料
}  # 结束宾客资料库

WEATHER = {  # 保存模拟天气数据
    "paris": {"condition": "Clear", "temp_c": 25, "wind": "Low", "outdoor_ok": True},  # 保存巴黎天气
    "london": {"condition": "Rain", "temp_c": 15, "wind": "Medium", "outdoor_ok": False},  # 保存伦敦天气
}  # 结束天气数据

HUB_STATS = {  # 保存模拟 Hub 统计数据
    "qwen": {"model": "Qwen/Qwen2.5-VL-7B-Instruct", "downloads": 3313345},  # 保存 Qwen 热门模型
    "google": {"model": "google/electra-base-discriminator", "downloads": 28546752},  # 保存 Google 热门模型
    "facebook": {"model": "facebook/esmfold_v1", "downloads": 13202321},  # 保存 Facebook 热门模型
}  # 结束 Hub 统计数据

SEARCH_RESULTS = {  # 保存模拟网络搜索结果
    "wireless energy": "Recent wireless energy work focuses on resonant coupling, efficient charging, and long-distance power transfer.",  # 保存无线能源搜索结果
    "ai news": "Recent AI discussions focus on open models, evaluation, multimodal assistants, and safer tool use.",  # 保存 AI 新闻搜索结果
}  # 结束搜索结果

def normalize_text(text: str) -> str:  # 定义文本标准化函数
    return text.lower().replace("'", "").replace(".", "").replace("?", "").replace(",", "").strip()  # 返回小写且去掉简单标点的文本

def guest_info_tool(query: str) -> str:  # 定义宾客资料检索工具
    normalized = normalize_text(query)  # 标准化用户查询
    for key, profile in GUESTS.items():  # 遍历所有宾客资料
        if key in normalized or profile["name"].lower().replace(".", "") in normalized:  # 判断查询是否命中宾客
            return f"{profile['name']} is {profile['relation']}. Background: {profile['background']} Email: {profile['email']} Current project: {profile['project']}"  # 返回宾客资料摘要
    return "No matching guest profile was found in the local guest database."  # 返回未命中提示

def weather_info_tool(location: str) -> str:  # 定义天气查询工具
    normalized = normalize_text(location)  # 标准化地点名称
    data = WEATHER.get(normalized, {"condition": "Clear", "temp_c": 22, "wind": "Low", "outdoor_ok": True})  # 获取天气或使用默认值
    suitability = "suitable" if data["outdoor_ok"] else "not suitable"  # 根据天气判断户外活动适配性
    return f"Weather in {location}: {data['condition']}, {data['temp_c']}C, wind={data['wind']}. Outdoor fireworks are {suitability}."  # 返回天气和建议

def hub_stats_tool(author: str) -> str:  # 定义 Hugging Face Hub 统计工具
    normalized = normalize_text(author)  # 标准化作者或组织名
    data = HUB_STATS.get(normalized)  # 获取模拟模型统计
    if data is None:  # 判断是否没有匹配组织
        return f"No Hub statistics were found for {author}."  # 返回未命中提示
    return f"The most popular model by {author} is {data['model']} with {data['downloads']:,} downloads."  # 返回热门模型信息

def web_search_tool(query: str) -> str:  # 定义网络搜索工具
    normalized = normalize_text(query)  # 标准化搜索问题
    if "wireless" in normalized or "energy" in normalized:  # 判断是否搜索无线能源
        return SEARCH_RESULTS["wireless energy"]  # 返回无线能源模拟结果
    if "ai" in normalized or "news" in normalized:  # 判断是否搜索 AI 新闻
        return SEARCH_RESULTS["ai news"]  # 返回 AI 新闻模拟结果
    return "General web result: no exact mock result, but Alfred would search the live web in production."  # 返回通用搜索结果

def enrich_query_with_memory(query: str, memory: list[dict[str, str]] | None) -> str:  # 定义利用记忆补全查询的函数
    if not memory:  # 判断是否没有历史记忆
        return query  # 没有记忆就返回原始查询
    normalized = normalize_text(query)  # 标准化当前查询
    history_text = " ".join(item["content"] for item in memory)  # 合并历史消息文本
    if "she" in normalized and "Ada Lovelace" in history_text:  # 判断代词是否可由历史解析为 Ada
        return query + " Lady Ada Lovelace"  # 补充 Ada 姓名帮助工具检索
    if "he" in normalized and "Nikola Tesla" in history_text:  # 判断代词是否可由历史解析为 Tesla
        return query + " Dr. Nikola Tesla"  # 补充 Tesla 姓名帮助工具检索
    return query  # 没有可补全信息就返回原始查询

def route_tools(query: str) -> list[str]:  # 定义工具路由函数
    normalized = normalize_text(query)  # 标准化查询
    tokens = set(normalized.split())  # 把查询拆成单词集合以避免 he 命中 weather
    selected: list[str] = []  # 创建工具选择列表
    if any(word in normalized for word in ["ada", "tesla", "background", "project"]) or {"she", "he"} & tokens:  # 判断是否需要宾客工具
        selected.append("guest")  # 选择宾客资料工具
    if any(word in normalized for word in ["weather", "fireworks", "paris", "rain", "wind"]):  # 判断是否需要天气工具
        selected.append("weather")  # 选择天气工具
    if any(word in normalized for word in ["qwen", "google", "facebook", "model", "downloads", "hub"]):  # 判断是否需要 Hub 工具
        selected.append("hub")  # 选择 Hub 统计工具
    if any(word in normalized for word in ["recent", "advancement", "wireless", "energy", "news", "prepare"]):  # 判断是否需要搜索工具
        selected.append("search")  # 选择网络搜索工具
    if not selected:  # 判断是否没有匹配任何工具
        selected.append("search")  # 默认选择搜索工具
    return selected  # 返回选择出的工具列表

def extract_location(query: str) -> str:  # 定义地点提取函数
    normalized = normalize_text(query)  # 标准化查询
    if "london" in normalized:  # 判断是否提到伦敦
        return "London"  # 返回伦敦
    return "Paris"  # 默认返回巴黎

def extract_author(query: str) -> str:  # 定义组织名提取函数
    normalized = normalize_text(query)  # 标准化查询
    if "google" in normalized:  # 判断是否提到 Google
        return "google"  # 返回 Google
    if "facebook" in normalized:  # 判断是否提到 Facebook
        return "facebook"  # 返回 Facebook
    return "qwen"  # 默认返回 Qwen

def collect_observations(query: str) -> list[str]:  # 定义工具执行函数
    selected = route_tools(query)  # 获取需要调用的工具
    observations: list[str] = []  # 创建观察结果列表
    if "guest" in selected:  # 判断是否调用宾客工具
        observations.append(guest_info_tool(query))  # 保存宾客工具结果
    if "weather" in selected:  # 判断是否调用天气工具
        observations.append(weather_info_tool(extract_location(query)))  # 保存天气工具结果
    if "hub" in selected:  # 判断是否调用 Hub 工具
        observations.append(hub_stats_tool(extract_author(query)))  # 保存 Hub 工具结果
    if "search" in selected:  # 判断是否调用搜索工具
        observations.append(web_search_tool(query))  # 保存搜索工具结果
    return observations  # 返回所有工具观察结果

def compose_final_answer(query: str, observations: list[str]) -> str:  # 定义最终回答生成函数
    bullet_text = "\n".join(f"- {item}" for item in observations)  # 把工具结果格式化成项目符号
    return f"Question: {query}\nAlfred used {len(observations)} tool result(s):\n{bullet_text}\nFinal: Alfred combined the tool evidence into a practical gala assistant answer."  # 返回最终回答

def run_alfred(query: str, memory: list[dict[str, str]] | None = None) -> str:  # 定义端到端 Alfred 执行函数
    enriched_query = enrich_query_with_memory(query, memory)  # 使用记忆补全当前查询
    observations = collect_observations(enriched_query)  # 调用工具收集观察结果
    answer = compose_final_answer(query, observations)  # 根据观察结果生成最终回答
    if memory is not None:  # 判断是否需要写入记忆
        memory.append({"role": "user", "content": query})  # 保存用户消息
        memory.append({"role": "assistant", "content": answer})  # 保存助手回答
    return answer  # 返回最终回答
