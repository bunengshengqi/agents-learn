"""
Day 4: Thought Examples

这个脚本不调用大模型，也不调用 API。
它的目的：把 Day 4 页面里的常见思维模式，用代码打印出来。

重点理解：
Thought 不是最终答案，而是模型在行动前的分析、规划、决策过程。
"""


THOUGHT_EXAMPLES = [
    {
        "name": "Planning",
        "chinese": "规划",
        "meaning": "把一个大任务拆成多个小步骤。",
        "example": "我需要把企业风险分析拆成三步：查工商信息、查司法风险、生成报告。",
    },
    {
        "name": "Analysis",
        "chinese": "分析",
        "meaning": "根据已有信息判断原因或风险点。",
        "example": "根据错误日志，问题可能出在数据库连接参数。",
    },
    {
        "name": "Decision Making",
        "chinese": "决策",
        "meaning": "在多个选项中选择下一步。",
        "example": "用户预算有限，所以应该推荐中等成本的方案。",
    },
    {
        "name": "Problem Solving",
        "chinese": "问题解决",
        "meaning": "找到解决问题的路径。",
        "example": "要优化这段代码，我应该先定位性能瓶颈，再决定优化方案。",
    },
    {
        "name": "Memory Integration",
        "chinese": "记忆整合",
        "meaning": "结合前文 messages 里的上下文。",
        "example": "用户之前说自己在银行做 RPA，所以我应该用银行自动化场景举例。",
    },
    {
        "name": "Self-Reflection",
        "chinese": "自我反思",
        "meaning": "发现上一步效果不好，调整策略。",
        "example": "刚才查询主接口失败，我应该尝试备用接口。",
    },
    {
        "name": "Goal Setting",
        "chinese": "目标设定",
        "meaning": "明确任务完成的验收标准。",
        "example": "这次任务完成的标准是输出风险等级、原因和人工复核建议。",
    },
    {
        "name": "Prioritization",
        "chinese": "优先级排序",
        "meaning": "决定先做什么，后做什么。",
        "example": "应该先处理安全漏洞，再开发新功能。",
    },
]


def print_thought_examples() -> None:
    """打印 Thought 常见类型。"""
    print("Day 4: 常见 Thought 思维模式")
    print("=" * 60)

    for index, item in enumerate(THOUGHT_EXAMPLES, start=1):
        print(f"{index}. {item['name']}（{item['chinese']}）")
        print(f"含义：{item['meaning']}")
        print(f"示例：{item['example']}")
        print("-" * 60)


def print_bank_rpa_case() -> None:
    """用银行 RPA 场景串联 Thought 类型。"""
    print("\n银行 RPA 场景：查询企业风险")
    print("=" * 60)

    steps = [
        "Planning：先查工商信息，再查司法风险，最后生成报告。",
        "Analysis：如果存在被执行记录，说明司法风险偏高。",
        "Decision Making：先调用工商查询工具，因为它是基础信息。",
        "Memory Integration：用户之前说这是企业客户，不是个人客户。",
        "Self-Reflection：如果主查询接口失败，就切换备用接口。",
        "Goal Setting：最终输出风险等级、依据和人工复核建议。",
        "Prioritization：先查结构化数据，再查新闻舆情。",
    ]

    for step in steps:
        print(step)


def main() -> None:
    print_thought_examples()
    print_bank_rpa_case()


if __name__ == "__main__":
    main()


