# 第28天 LangGraph 风格端到端 Alfred 示例。  # 说明本文件用途
from __future__ import annotations  # 启用延迟类型注解

from common_alfred_tools import collect_observations, compose_final_answer  # 导入工具执行和回答生成函数

class LangGraphLikeAlfred:  # 定义一个轻量版 LangGraph 应用
    def __init__(self) -> None:  # 初始化图应用
        self.messages: list[dict[str, str]] = []  # 保存消息状态

    def assistant_node(self, query: str) -> dict[str, object]:  # 定义 assistant 节点
        observations = collect_observations(query)  # assistant 决定并收集工具结果
        return {"query": query, "observations": observations}  # 返回中间状态

    def final_node(self, state: dict[str, object]) -> str:  # 定义最终回答节点
        query = str(state["query"])  # 从状态中取出原始问题
        observations = list(state["observations"])  # 从状态中取出工具观察结果
        return compose_final_answer(query, observations)  # 生成最终回答

    def invoke(self, state: dict[str, str]) -> dict[str, list[dict[str, str]]]:  # 定义 LangGraph 风格 invoke 方法
        query = state["messages"]  # 读取输入消息
        assistant_state = self.assistant_node(query)  # 执行 assistant 节点
        answer = self.final_node(assistant_state)  # 执行最终回答节点
        self.messages.append({"role": "user", "content": query})  # 保存用户消息
        self.messages.append({"role": "assistant", "content": answer})  # 保存助手消息
        return {"messages": self.messages}  # 返回图状态

def build_langgraph_alfred() -> LangGraphLikeAlfred:  # 定义构建 LangGraph 风格 Alfred 的函数
    return LangGraphLikeAlfred()  # 返回图应用实例

def main() -> None:  # 定义脚本入口函数
    alfred = build_langgraph_alfred()  # 创建 LangGraph 风格 Alfred
    queries = [  # 准备端到端测试问题
        "Tell me about Lady Ada Lovelace.",  # 测试宾客资料检索
        "What's the weather like in Paris tonight? Will it be suitable for our fireworks display?",  # 测试天气决策
        "One of our guests is from Qwen. What can you tell me about their most popular model?",  # 测试 Hub 统计
        "I need to speak with Dr. Nikola Tesla about recent advancements in wireless energy.",  # 测试多工具组合
    ]  # 结束测试问题列表
    for query in queries:  # 遍历所有测试问题
        print("=" * 80)  # 打印分隔线
        result = alfred.invoke({"messages": query})  # 调用图应用
        print(result["messages"][-1]["content"])  # 打印最新助手回答

if __name__ == "__main__":  # 判断是否直接执行脚本
    main()  # 调用脚本入口
