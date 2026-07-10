"""用标准库演示一个真正执行工具的 Thought -> Act -> Observe 循环。"""

from __future__ import annotations

import ast
import json
import operator
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ToolSpec:
    """描述调度器可以执行的一个工具。"""

    function: Callable[..., dict[str, Any]]
    required_arguments: tuple[str, ...]


@dataclass(frozen=True)
class ModelDecision:
    """表示模型的一次输出：调用工具，或者直接给出最终答案。"""

    thought_summary: str
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None
    final_answer: str | None = None


def get_weather(city: str) -> dict[str, Any]:
    """返回离线固定天气；函数本身会被调度器真实调用。"""

    weather_by_city = {
        "杭州": {"city": "杭州", "temperature_c": 24, "condition": "小雨"},
        "北京": {"city": "北京", "temperature_c": 31, "condition": "晴"},
    }
    return weather_by_city.get(
        city,
        {"city": city, "error": "教学数据中没有这个城市"},
    )


ALLOWED_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _evaluate_expression(node: ast.AST) -> float:
    """只计算数字与四则运算，避免直接使用不安全的 eval。"""

    if isinstance(node, ast.Expression):
        return _evaluate_expression(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_BINARY_OPERATORS:
        left = _evaluate_expression(node.left)
        right = _evaluate_expression(node.right)
        return ALLOWED_BINARY_OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate_expression(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    raise ValueError("表达式只能包含数字、括号和 + - * / 运算")


def calculator(expression: str) -> dict[str, Any]:
    """安全计算简单算术表达式。"""

    syntax_tree = ast.parse(expression, mode="eval")
    result = _evaluate_expression(syntax_tree)
    normalized_result: int | float = int(result) if result.is_integer() else result
    return {"expression": expression, "result": normalized_result}


TOOLS: dict[str, ToolSpec] = {
    "get_weather": ToolSpec(get_weather, ("city",)),
    "calculator": ToolSpec(calculator, ("expression",)),
}


class TeachingFunctionCallingModel:
    """用确定性规则模拟“训练后模型”的决策输出。"""

    def decide(self, messages: list[dict[str, Any]]) -> ModelDecision:
        observations = {
            message["name"]: message["content"]
            for message in messages
            if message["role"] == "tool"
        }

        if "get_weather" not in observations:
            return ModelDecision(
                thought_summary="问题依赖当前天气，先查询杭州天气。",
                tool_name="get_weather",
                arguments={"city": "杭州"},
            )

        if "calculator" not in observations:
            return ModelDecision(
                thought_summary="已经获得天气，还需要计算 5 公里乘以每公里 6 分钟。",
                tool_name="calculator",
                arguments={"expression": "5 * 6"},
            )

        weather = observations["get_weather"]
        calculation = observations["calculator"]
        return ModelDecision(
            thought_summary="所需的天气和时间都已获得，可以根据观察结果回答。",
            final_answer=(
                f"{weather['city']}当前{weather['temperature_c']}℃、{weather['condition']}。"
                f"按每公里 6 分钟估算，5 公里约需{calculation['result']}分钟；雨天注意路滑。"
            ),
        )


def execute_tool(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """校验工具名称和必填参数，再执行真实 Python 函数。"""

    if tool_name not in TOOLS:
        return {"error": f"工具不存在：{tool_name}"}

    tool = TOOLS[tool_name]
    missing = [name for name in tool.required_arguments if name not in arguments]
    if missing:
        return {"error": f"缺少参数：{', '.join(missing)}"}

    try:
        return tool.function(**arguments)
    except Exception as exc:  # noqa: BLE001 - 调度器边界必须将工具异常变成观察结果。
        return {"error": f"工具执行失败：{exc}"}


def run_agent(user_query: str, max_steps: int = 5) -> str:
    """运行 Agent，直到模型给出最终答案或达到最大步数。"""

    model = TeachingFunctionCallingModel()
    messages: list[dict[str, Any]] = [{"role": "user", "content": user_query}]

    print(f"User: {user_query}\n")
    for step in range(1, max_steps + 1):
        decision = model.decide(messages)
        print(f"Step {step} Thought: {decision.thought_summary}")

        if decision.final_answer is not None:
            print(f"Final: {decision.final_answer}")
            return decision.final_answer

        if decision.tool_name is None or decision.arguments is None:
            raise RuntimeError("模型既没有给最终答案，也没有给出完整工具调用")

        action = {"name": decision.tool_name, "arguments": decision.arguments}
        print(f"Step {step} Act: {json.dumps(action, ensure_ascii=False)}")

        observation = execute_tool(decision.tool_name, decision.arguments)
        print(f"Step {step} Observe: {json.dumps(observation, ensure_ascii=False)}\n")
        messages.append(
            {
                "role": "assistant",
                "tool_call": action,
            }
        )
        messages.append(
            {
                "role": "tool",
                "name": decision.tool_name,
                "content": observation,
            }
        )

    raise RuntimeError(f"Agent 在 {max_steps} 步内没有完成任务")


if __name__ == "__main__":
    run_agent("先确认杭州天气，再按每公里 6 分钟估算跑 5 公里需要多久。")

