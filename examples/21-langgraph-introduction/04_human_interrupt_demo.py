"""Day21 示例 4：interrupt() 人类介入。

这个示例展示：
1. 图执行到人工审核节点时暂停。
2. LangGraph 保存当前状态。
3. 人类给出审批结果后，使用同一个 thread_id 恢复执行。

注意：
运行这个文件需要安装 langgraph。
"""

from typing import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class ReviewState(TypedDict, total=False):
    email: str
    draft_reply: str
    approved: bool
    final_message: str


def draft_reply(state: ReviewState) -> dict:
    return {
        "draft_reply": (
            "您好，您的账单问题我们已经收到。"
            "由于涉及账户安全，需要人工客服进一步确认。"
        )
    }


def human_review(state: ReviewState) -> dict:
    human_decision = interrupt(
        {
            "message": "请审核这封邮件回复是否可以发送。",
            "email": state["email"],
            "draft_reply": state["draft_reply"],
        }
    )

    if human_decision.get("approved"):
        edited_reply = human_decision.get("edited_reply", state["draft_reply"])
        return {
            "approved": True,
            "final_message": f"人工已批准，发送内容：{edited_reply}",
        }

    return {
        "approved": False,
        "final_message": "人工拒绝发送，转交客服继续处理。",
    }


def build_graph():
    builder = StateGraph(ReviewState)

    builder.add_node("draft_reply", draft_reply)
    builder.add_node("human_review", human_review)

    builder.add_edge(START, "draft_reply")
    builder.add_edge("draft_reply", "human_review")
    builder.add_edge("human_review", END)

    checkpointer = InMemorySaver()
    return builder.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    graph = build_graph()
    config = {"configurable": {"thread_id": "day21-human-review-demo"}}

    first_result = graph.invoke(
        {"email": "I was charged twice for my subscription!"},
        config=config,
    )

    print("第一次执行结果：")
    print(first_result)
    print()
    print("上面结果里会包含 __interrupt__，表示图已经暂停等待人工输入。")
    print()

    resumed_result = graph.invoke(
        Command(
            resume={
                "approved": True,
                "edited_reply": "您好，账单问题已收到，我们会在 24 小时内人工核查并回复。",
            }
        ),
        config=config,
    )

    print("恢复执行后的结果：")
    print(resumed_result)
