"""Day25 示例 3：输出 Agentic RAG 流程图。

运行后，把输出复制到 Obsidian 的 Mermaid 代码块即可查看图。
"""


def main() -> None:
    print(
        """flowchart TD
    A[用户问题] --> B[Agent 分析问题]
    B --> C{需要什么信息?}
    C -->|宾客资料| D[guest_profile_tool]
    C -->|菜单信息| E[menu_tool]
    C -->|活动时间| F[schedule_tool]
    C -->|天气/烟花| G[weather_tool]
    C -->|最新话题| H[news_tool]
    D --> I[收集证据]
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J{信息是否足够?}
    J -->|不够| B
    J -->|足够| K[LLM 综合答案]
    K --> L[返回结果]"""
    )


if __name__ == "__main__":
    main()
