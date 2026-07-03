"""Day22 示例 2：State 设计原则。

State 不是靠上帝视角一次性设计完的。
更实用的方法是：
1. 先画出流程。
2. 列出每个节点要读什么、写什么。
3. 只把跨节点需要的数据放进 State。
"""

from pprint import pprint
from typing import Literal

from typing_extensions import TypedDict


class BadState(TypedDict):
    """教学示例里常见，但真实项目里太含糊。"""

    graph_state: str


class EmailClassification(TypedDict):
    intent: Literal["question", "bug", "billing", "other"]
    urgency: Literal["low", "medium", "high"]
    topic: str
    summary: str


class GoodEmailState(TypedDict, total=False):
    """更贴近真实业务的 State。

    total=False 表示有些字段不是一开始就存在，而是由后续节点逐步写入。
    """

    email_id: str
    sender_email: str
    email_content: str

    classification: EmailClassification
    search_results: list[str]
    ticket_id: str
    draft_response: str
    approved: bool
    final_status: str
    errors: list[str]


WORKFLOW_IO = [
    {
        "node": "read_email",
        "reads": ["email_id"],
        "writes": ["email_content", "sender_email"],
    },
    {
        "node": "classify_email",
        "reads": ["email_content", "sender_email"],
        "writes": ["classification"],
    },
    {
        "node": "search_docs",
        "reads": ["classification"],
        "writes": ["search_results"],
    },
    {
        "node": "draft_reply",
        "reads": ["email_content", "classification", "search_results"],
        "writes": ["draft_response"],
    },
    {
        "node": "human_review",
        "reads": ["draft_response", "classification"],
        "writes": ["approved"],
    },
    {
        "node": "send_reply",
        "reads": ["draft_response", "approved"],
        "writes": ["final_status"],
    },
]


def collect_state_fields() -> list[str]:
    fields: set[str] = set()
    for step in WORKFLOW_IO:
        fields.update(step["reads"])
        fields.update(step["writes"])
    return sorted(fields)


if __name__ == "__main__":
    print("不推荐的 State：")
    pprint(BadState.__annotations__)
    print()

    print("从工作流推导字段：")
    pprint(WORKFLOW_IO)
    print()

    print("这个工作流至少需要这些 State 字段：")
    pprint(collect_state_fields())
    print()

    print("更推荐的业务 State：")
    pprint(GoodEmailState.__annotations__)
