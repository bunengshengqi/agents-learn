# 第28天 smolagents 风格端到端 Alfred 示例。  # 说明本文件用途
from __future__ import annotations  # 启用延迟类型注解

from common_alfred_tools import run_alfred  # 导入公共端到端执行函数

class SmolagentsLikeCodeAgent:  # 定义一个轻量版 CodeAgent 以便离线学习
    def __init__(self, tools: list[str], planning_interval: int = 3) -> None:  # 初始化 Agent
        self.tools = tools  # 保存工具名称列表
        self.planning_interval = planning_interval  # 保存规划间隔
        self.memory: list[dict[str, str]] = []  # 创建会话记忆

    def run(self, query: str, reset: bool = True) -> str:  # 定义 smolagents 风格 run 方法
        if reset:  # 判断是否重置上下文
            self.memory = []  # 清空会话记忆
        return run_alfred(query, self.memory)  # 调用公共 Alfred 流程并返回答案

def build_smolagents_alfred() -> SmolagentsLikeCodeAgent:  # 定义构建 smolagents 风格 Alfred 的函数
    tools = ["guest_info_tool", "weather_info_tool", "hub_stats_tool", "search_tool"]  # 准备工具列表
    return SmolagentsLikeCodeAgent(tools=tools, planning_interval=3)  # 返回配置好的 Agent

def main() -> None:  # 定义脚本入口函数
    alfred = build_smolagents_alfred()  # 创建 smolagents 风格 Alfred
    queries = [  # 准备端到端测试问题
        "Tell me about Lady Ada Lovelace.",  # 测试宾客资料检索
        "What's the weather like in Paris tonight? Will it be suitable for our fireworks display?",  # 测试天气决策
        "One of our guests is from Qwen. What can you tell me about their most popular model?",  # 测试 Hub 统计
        "I need to speak with Dr. Nikola Tesla about recent advancements in wireless energy.",  # 测试多工具组合
    ]  # 结束测试问题列表
    for query in queries:  # 遍历所有测试问题
        print("=" * 80)  # 打印分隔线
        print(alfred.run(query))  # 运行 Agent 并打印结果

if __name__ == "__main__":  # 判断是否直接执行脚本
    main()  # 调用脚本入口
