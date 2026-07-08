# 第28天端到端 Agentic RAG 流程图脚本。  # 说明本文件用途

def main() -> None:  # 定义脚本入口函数
    flow_lines = [  # 准备 Mermaid 流程图文本
        "flowchart TD",  # 定义流程图方向
        "    A[User task] --> B[Alfred understands intent]",  # 用户问题进入 Agent
        "    B --> C{Select tools}",  # Agent 选择工具
        "    C -->|guest question| D[guest_info_tool]",  # 宾客问题进入宾客工具
        "    C -->|weather question| E[weather_info_tool]",  # 天气问题进入天气工具
        "    C -->|model question| F[hub_stats_tool]",  # 模型问题进入 Hub 工具
        "    C -->|recent info| G[web_search_tool]",  # 实时信息进入搜索工具
        "    D --> H[Collect observations]",  # 宾客结果进入观察集合
        "    E --> H",  # 天气结果进入观察集合
        "    F --> H",  # Hub 结果进入观察集合
        "    G --> H",  # 搜索结果进入观察集合
        "    H --> I[Compose final answer]",  # 观察结果进入最终回答
        "    I --> J[Update memory]",  # 最终回答写入记忆
        "    J --> K[Return response]",  # 返回用户响应
    ]  # 结束流程图文本列表
    print("\n".join(flow_lines))  # 打印 Mermaid 流程图

if __name__ == "__main__":  # 判断是否直接执行脚本
    main()  # 调用脚本入口
