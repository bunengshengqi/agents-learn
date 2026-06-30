"""
第17天：把 QueryEngine 包装成 Agent 工具

运行：
python query_engine_as_tool.py
"""

from query_local_notes import get_query_engine


class AlfredRAGTool:
    name = "alfred_rag_tool"
    description = "查询 Alfred 的晚宴知识库，返回基于资料的答案。"

    def __init__(self):
        self.query_engine = get_query_engine()

    def forward(self, query: str) -> str:
        response = self.query_engine.query(query)
        return str(response)


def main() -> None:
    tool = AlfredRAGTool()

    question = "请根据知识库，安排一个不含辣椒和花生的周五晚宴菜单。"
    answer = tool.forward(question)

    print("====== 工具名称 ======")
    print(tool.name)

    print("\n====== 工具描述 ======")
    print(tool.description)

    print("\n====== 工具输入 ======")
    print(question)

    print("\n====== 工具输出 ======")
    print(answer)


if __name__ == "__main__":
    main()
