"""用可解释规则检查函数调用格式、工具选择、参数和结果忠实度。"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


TOOL_SCHEMAS = {
    "get_weather": {"required": {"city": str}},
    "calculator": {"required": {"expression": str}},
    "publish_article": {"required": {"platform": str, "title": str}},
}

TOOL_CALL_PATTERN = re.compile(r"<\|tool_call\|>(.*?)<\|end\|>", re.DOTALL)
FINAL_PATTERN = re.compile(r"<\|final\|>(.*?)<\|end\|>", re.DOTALL)


@dataclass(frozen=True)
class EvaluationCase:
    """描述一个输出及其期望行为。"""

    name: str
    model_output: str
    expected_valid: bool
    expected_tool: str | None = None
    expected_arguments: dict[str, Any] | None = None
    required_final_fragments: tuple[str, ...] = ()


def parse_tool_call(model_output: str) -> tuple[dict[str, Any] | None, list[str]]:
    """解析特殊 token 中的 JSON 工具调用。"""

    match = TOOL_CALL_PATTERN.search(model_output)
    if match is None:
        return None, ["没有找到 <|tool_call|>...<|end|>"]

    try:
        call = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        return None, [f"工具调用不是合法 JSON：{exc.msg}"]

    if not isinstance(call, dict):
        return None, ["工具调用必须是 JSON object"]
    return call, []


def validate_tool_call(call: dict[str, Any]) -> list[str]:
    """根据工具白名单和最小 schema 校验工具调用。"""

    errors: list[str] = []
    tool_name = call.get("name")
    arguments = call.get("arguments")

    if tool_name not in TOOL_SCHEMAS:
        return [f"未知工具：{tool_name}"]
    if not isinstance(arguments, dict):
        return ["arguments 必须是 JSON object"]

    for argument_name, argument_type in TOOL_SCHEMAS[tool_name]["required"].items():
        if argument_name not in arguments:
            errors.append(f"缺少必填参数：{argument_name}")
        elif not isinstance(arguments[argument_name], argument_type):
            errors.append(f"参数 {argument_name} 类型错误")
    return errors


def evaluate_case(case: EvaluationCase) -> list[str]:
    """执行单个函数调用或最终答案评测。"""

    errors: list[str] = []

    if case.expected_tool is not None:
        call, parse_errors = parse_tool_call(case.model_output)
        errors.extend(parse_errors)
        if call is not None:
            errors.extend(validate_tool_call(call))
            if call.get("name") != case.expected_tool:
                errors.append(
                    f"工具选择错误：期望 {case.expected_tool}，实际 {call.get('name')}"
                )
            if case.expected_arguments is not None and call.get("arguments") != case.expected_arguments:
                errors.append(
                    f"参数值错误：期望 {case.expected_arguments}，实际 {call.get('arguments')}"
                )

        if "<|observation|>" in case.model_output:
            errors.append("模型发出工具调用后又自行生成 observation")

    if case.required_final_fragments:
        match = FINAL_PATTERN.search(case.model_output)
        if match is None:
            errors.append("没有找到 <|final|>...<|end|>")
        else:
            final_answer = match.group(1)
            for fragment in case.required_final_fragments:
                if fragment not in final_answer:
                    errors.append(f"最终答案未体现观察结果：{fragment}")

    return errors


def build_cases() -> list[EvaluationCase]:
    """包含正确输出，也包含评测器应该识别出的错误。"""

    return [
        EvaluationCase(
            name="合法天气调用",
            model_output=(
                "<|thought|>需要查询天气。<|end|>\n"
                '<|tool_call|>{"name":"get_weather","arguments":{"city":"杭州"}}<|end|>'
            ),
            expected_valid=True,
            expected_tool="get_weather",
            expected_arguments={"city": "杭州"},
        ),
        EvaluationCase(
            name="参数实体错误",
            model_output=(
                '<|tool_call|>{"name":"get_weather","arguments":{"city":"上海"}}<|end|>'
            ),
            expected_valid=False,
            expected_tool="get_weather",
            expected_arguments={"city": "杭州"},
        ),
        EvaluationCase(
            name="模型伪造观察结果",
            model_output=(
                '<|tool_call|>{"name":"calculator","arguments":{"expression":"28 * 17"}}<|end|>\n'
                '<|observation|>{"result":999}<|end|>'
            ),
            expected_valid=False,
            expected_tool="calculator",
            expected_arguments={"expression": "28 * 17"},
        ),
        EvaluationCase(
            name="最终答案忠于观察",
            model_output="<|final|>杭州当前 24℃，有小雨，请注意路滑。<|end|>",
            expected_valid=True,
            required_final_fragments=("24℃", "小雨"),
        ),
        EvaluationCase(
            name="最终答案忽略观察",
            model_output="<|final|>杭州今天晴朗，适合户外活动。<|end|>",
            expected_valid=False,
            required_final_fragments=("24℃", "小雨"),
        ),
    ]


def main() -> None:
    """运行评测，并验证评测器能区分成功与失败样本。"""

    harness_failures = 0
    for case in build_cases():
        errors = evaluate_case(case)
        actual_valid = not errors
        harness_ok = actual_valid == case.expected_valid
        harness_failures += int(not harness_ok)

        result = "通过" if actual_valid else "失败"
        expectation = "有效" if case.expected_valid else "应被拦截"
        print(f"[{result}] {case.name}（期望：{expectation}）")
        for error in errors:
            print(f"  - {error}")

    if harness_failures:
        raise SystemExit(f"评测器自身有 {harness_failures} 个结果不符合预期")
    print("\n评测器自检通过：正确样本被接受，错误样本被成功拦截。")


if __name__ == "__main__":
    main()

