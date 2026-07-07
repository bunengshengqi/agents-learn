# Day25 示例 2：Agentic RAG 工具路由器
# 这个例子用来演示：Agent 如何根据用户问题，自动选择不同的检索工具

# Alfred 是一个“管家型 Agent”
# 当用户提出问题时，Alfred 不会固定查某一个知识库
# 而是会先判断问题类型，再选择合适的工具去查资料

# 可用工具包括：
# guest_profile_tool：查询宾客资料
# menu_tool：查询菜单信息
# schedule_tool：查询活动日程
# weather_tool：查询天气信息
# news_tool：查询最新新闻或安全话题

# 这就是 Agentic RAG 的核心思想：
# 检索不再是固定步骤，而是 Agent 可以主动选择的动作


from __future__ import annotations  # 启用延迟类型注解，让类型提示在运行时不会立刻求值

import json  # 导入 json 模块，用来读取和解析 JSON 数据文件
from pathlib import Path  # 导入 Path，用更现代、更跨平台的方式处理文件路径


DATA_FILE = Path(__file__).parent / "data" / "gala_knowledge.json"  # 拼接知识库 JSON 文件路径


def load_knowledge() -> dict:  # 定义函数：加载知识库，返回一个字典
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))  # 读取 JSON 文件内容，并解析成 Python 字典


def guest_profile_tool(question: str, knowledge: dict) -> str:  # 定义宾客资料查询工具
    normalized = question.lower()  # 把用户问题转成小写，方便后续做关键词匹配

    matches = [  # 创建一个列表，用来保存匹配到的宾客资料
        guest  # 如果某个 guest 符合条件，就把这个 guest 放进 matches 列表
        for guest in knowledge["guest_profiles"]  # 遍历知识库中的所有宾客资料
        if (  # 开始判断当前宾客是否和用户问题匹配
            guest["name"].split()[0].lower() in normalized  # 判断宾客名字的第一个单词是否出现在问题中，例如 Alice
            or guest["name"].lower() in normalized  # 或者判断宾客完整姓名是否出现在问题中
        )  # 条件判断结束
    ]  # 列表推导式结束

    if not matches:  # 如果没有找到任何匹配的宾客
        return "No matching guest profile found."  # 返回没有找到宾客资料的提示

    lines = []  # 创建一个空列表，用来存放最终要输出的每一行宾客信息

    for guest in matches:  # 遍历所有匹配到的宾客
        lines.append(  # 把当前宾客的信息拼接成一行文本，并加入 lines 列表
            f"{guest['name']}: interests={guest['interests']}; "  # 拼接宾客姓名和兴趣信息
            f"achievement={guest['achievement']}; tips={guest['conversation_tips']}"  # 拼接成就和聊天建议
        )  # 当前宾客信息拼接完成

    return "\n".join(lines)  # 把多行宾客信息用换行符连接成一个字符串并返回


def menu_tool(question: str, knowledge: dict) -> str:  # 定义菜单查询工具
    return "Menu items: " + ", ".join(knowledge["menu"])  # 把菜单列表用逗号连接成字符串并返回


def schedule_tool(question: str, knowledge: dict) -> str:  # 定义活动日程查询工具
    return "Schedule: " + "; ".join(  # 返回日程字符串，并用分号连接多个日程项
        f"{item['time']} {item['event']}"  # 把每个日程项格式化成“时间 + 事件”的形式
        for item in knowledge["schedule"]  # 遍历知识库中的所有活动日程
    )  # join 拼接结束


def weather_tool(question: str) -> str:  # 定义天气查询工具
    return (  # 返回一段模拟的天气信息
        "Weather update: clear sky, low wind, no rain expected. "  # 第一部分：天气晴朗、风小、无雨
        "Fireworks are suitable after 21:30."  # 第二部分：建议 21:30 后适合放烟花
    )  # 天气信息返回结束


def news_tool(question: str) -> str:  # 定义新闻查询工具
    return (  # 返回一段模拟的新闻或安全聊天话题
        "Latest safe conversation topic: a new open-source AI model ranking update. "  # 提供一个安全话题：开源 AI 模型排名更新
        "Avoid political commentary."  # 提醒避免政治评论
    )  # 新闻信息返回结束


def choose_tools(question: str) -> list[str]:  # 定义工具选择函数，根据用户问题决定调用哪些工具
    normalized = question.lower()  # 把用户问题转成小写，方便关键词匹配

    tools: list[str] = []  # 创建一个空列表，用来保存需要调用的工具名称

    if any(name in normalized for name in ["alice", "bob", "clara", "guest"]):  # 如果问题中包含宾客相关关键词
        tools.append("guest_profile_tool")  # 选择宾客资料查询工具

    if any(word in normalized for word in ["menu", "food", "vegetarian", "drink"]):  # 如果问题中包含菜单、食物、素食、饮料等关键词
        tools.append("menu_tool")  # 选择菜单查询工具

    if any(word in normalized for word in ["schedule", "time", "when"]):  # 如果问题中包含日程、时间、什么时候等关键词
        tools.append("schedule_tool")  # 选择活动日程查询工具

    if any(word in normalized for word in ["weather", "fireworks", "rain", "wind"]):  # 如果问题中包含天气、烟花、下雨、风等关键词
        tools.append("weather_tool")  # 选择天气查询工具

    if any(word in normalized for word in ["news", "latest", "topic"]):  # 如果问题中包含新闻、最新、话题等关键词
        tools.append("news_tool")  # 选择新闻查询工具

    if not tools:  # 如果没有匹配到任何工具
        tools.append("guest_profile_tool")  # 默认选择宾客资料查询工具

    return tools  # 返回最终选择的工具列表


def answer_with_agentic_rag(question: str, knowledge: dict) -> str:  # 定义 Agentic RAG 的主回答函数
    selected_tools = choose_tools(question)  # 先根据问题选择需要调用的工具

    observations = []  # 创建一个空列表，用来保存每个工具返回的观察结果

    for tool_name in selected_tools:  # 遍历所有被选中的工具名称
        if tool_name == "guest_profile_tool":  # 如果当前工具是宾客资料工具
            observations.append(guest_profile_tool(question, knowledge))  # 调用宾客资料工具，并保存结果

        elif tool_name == "menu_tool":  # 如果当前工具是菜单工具
            observations.append(menu_tool(question, knowledge))  # 调用菜单工具，并保存结果

        elif tool_name == "schedule_tool":  # 如果当前工具是日程工具
            observations.append(schedule_tool(question, knowledge))  # 调用日程工具，并保存结果

        elif tool_name == "weather_tool":  # 如果当前工具是天气工具
            observations.append(weather_tool(question))  # 调用天气工具，并保存结果

        elif tool_name == "news_tool":  # 如果当前工具是新闻工具
            observations.append(news_tool(question))  # 调用新闻工具，并保存结果

    return (  # 拼接最终回答文本
        f"Question: {question}\n"  # 输出原始问题
        f"Selected tools: {selected_tools}\n"  # 输出 Agent 选择了哪些工具
        "Observations:\n"  # 输出观察结果标题
        + "\n".join(f"- {item}" for item in observations)  # 把所有工具结果拼接成项目符号列表
        + "\nFinal answer: Alfred can answer based on the selected evidence above."  # 输出最终回答说明
    )  # 最终回答拼接结束


if __name__ == "__main__":  # 判断当前文件是否是直接运行，而不是被其他文件导入
    knowledge = load_knowledge()  # 加载 gala_knowledge.json 知识库

    questions = [  # 定义一组测试问题
        "What should I talk about with Alice?",  # 测试问题 1：询问 Alice 的聊天话题
        "When should we launch fireworks if weather matters?",  # 测试问题 2：询问天气和烟花时间
        "What vegetarian food and safe news topic can I mention?",  # 测试问题 3：询问素食和安全新闻话题
    ]  # 测试问题列表结束

    for question in questions:  # 遍历每一个测试问题
        print("=" * 80)  # 打印分隔线，方便区分不同问题的输出
        print(answer_with_agentic_rag(question, knowledge))  # 调用 Agentic RAG 主函数并打印回答