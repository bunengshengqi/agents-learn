# 第28天 LlamaIndex 风格端到端 Alfred 示例。  # 说明本文件用途
from __future__ import annotations  # 启用延迟类型注解

from common_alfred_tools import run_alfred  # 导入公共端到端执行函数

class LlamaIndexLikeContext:  # 定义一个轻量版 Context 以便离线学习
    def __init__(self) -> None:  # 初始化上下文
        self.memory: list[dict[str, str]] = []  # 保存会话消息

class LlamaIndexLikeAgentWorkflow:  # 定义一个轻量版 AgentWorkflow
    def __init__(self, tools: list[str]) -> None:  # 初始化工作流
        self.tools = tools  # 保存工具名称列表

    def run(self, query: str, ctx: LlamaIndexLikeContext | None = None) -> str:  # 定义 LlamaIndex 风格 run 方法
        memory = ctx.memory if ctx is not None else None  # 从 Context 中取出记忆
        return run_alfred(query, memory)  # 调用公共 Alfred 流程并返回答案

def build_llama_index_alfred() -> LlamaIndexLikeAgentWorkflow:  # 定义构建 LlamaIndex 风格 Alfred 的函数
    tools = ["guest_info_tool", "search_tool", "weather_info_tool", "hub_stats_tool"]  # 准备工具列表
    return LlamaIndexLikeAgentWorkflow(tools=tools)  # 返回配置好的工作流

def main() -> None:  # 定义脚本入口函数
    alfred = build_llama_index_alfred()  # 创建 LlamaIndex 风格 Alfred
    ctx = LlamaIndexLikeContext()  # 创建上下文以模拟 LlamaIndex 记忆
    queries = [  # 准备端到端测试问题
        "Tell me about Lady Ada Lovelace.",  # 测试宾客资料检索
        "What's the weather like in Paris tonight? Will it be suitable for our fireworks display?",  # 测试天气决策
        "One of our guests is from Google. What can you tell me about their most popular model?",  # 测试 Hub 统计
        "I need to speak with Dr. Nikola Tesla about recent advancements in wireless energy.",  # 测试多工具组合
    ]  # 结束测试问题列表
    for query in queries:  # 遍历所有测试问题
        print("=" * 80)  # 打印分隔线
        print(alfred.run(query, ctx=ctx))  # 运行工作流并打印结果

if __name__ == "__main__":  # 判断是否直接执行脚本
    main()  # 调用脚本入口
