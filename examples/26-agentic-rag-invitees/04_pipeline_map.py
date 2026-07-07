"""Day26 示例 4：输出 Agentic RAG 宾客工具流程图。"""  # 说明这个脚本输出流程图。 


def main() -> None:  # 定义主函数。 
    flow_lines = [  # 创建 Mermaid 流程图的每一行文本。 
        "flowchart TD",  # 定义 Mermaid 图方向为自上而下。 
        "    A[Hugging Face Dataset] --> B[Load invitee rows]",  # 表示从数据集加载原始宾客行。 
        "    B --> C[Convert each row to Document]",  # 表示把每行数据转换成 Document。 
        "    C --> D[Build Retriever]",  # 表示基于 Document 构建检索器。 
        "    D --> E[Wrap Retriever as Tool]",  # 表示把检索器包装成工具。 
        "    E --> F[Give Tool to Alfred Agent]",  # 表示把工具交给 Alfred 智能体。 
        "    F --> G[User asks about invitee]",  # 表示用户提出宾客相关问题。 
        "    G --> H{Should Alfred use guest tool?}",  # 表示 Alfred 判断是否需要宾客工具。 
        "    H -->|Yes| I[Call guest_info_retriever]",  # 表示需要检索时调用宾客工具。 
        "    H -->|No| J[Answer without retrieval]",  # 表示不需要检索时直接回答。 
        "    I --> K[Return matching guest records]",  # 表示工具返回匹配的宾客记录。 
        "    K --> L[Alfred writes final answer]",  # 表示 Alfred 基于记录组织最终答案。 
        "    J --> L",  # 表示直接回答路径也汇入最终答案。 
    ]  # 结束 Mermaid 文本行列表。 
    print("\n".join(flow_lines))  # 按换行拼接并打印 Mermaid 文本。 


if __name__ == "__main__":  # 判断脚本是否直接运行。 
    main()  # 执行主函数。 
