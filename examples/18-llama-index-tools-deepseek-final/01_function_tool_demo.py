"""
第18天代码 01：FunctionTool 示例

FunctionTool:
把普通 Python 函数包装成 Agent 可以调用的工具。

运行：
python 01_function_tool_demo.py
"""

from datetime import datetime
from llama_index.core.tools import FunctionTool


def is_workday(date: str) -> str:
    """
    判断给定日期是否为工作日。
    参数 date 格式必须是 YYYY-MM-DD。
    """
    dt = datetime.strptime(date, "%Y-%m-%d")

    if dt.weekday() < 5:
        return f"{date} 是周一到周五，按普通规则属于工作日。"

    return f"{date} 是周六或周日，按普通规则不属于工作日。"


def calculate_fee(amount: float, rate: float) -> str:
    """
    根据金额和费率计算手续费。
    amount 是交易金额，rate 是费率，例如 0.006 表示千分之六。
    """
    fee = amount * rate
    return f"交易金额 {amount:.2f}，费率 {rate:.4f}，手续费为 {fee:.2f}。"


def main() -> None:
    workday_tool = FunctionTool.from_defaults(
        fn=is_workday,
        name="is_workday_tool",
        description="判断某个日期是否为工作日，输入格式为 YYYY-MM-DD。",
    )

    fee_tool = FunctionTool.from_defaults(
        fn=calculate_fee,
        name="calculate_fee_tool",
        description="根据交易金额和费率计算手续费。",
    )

    print("====== FunctionTool 1：工作日判断 ======")
    print(workday_tool.call("2026-07-01"))

    print("\n====== FunctionTool 2：手续费计算 ======")
    print(fee_tool.call(amount=10000, rate=0.006))


if __name__ == "__main__":
    main()
