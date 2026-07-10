"""Day31 本地 Agent、trace/span 记录器和评估工具。"""

from __future__ import annotations

import ast
import json
import operator
import time
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterator


OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


@dataclass
class SpanRecord:
    """表示一次 trace 中的一个步骤。"""

    trace_id: str
    span_id: str
    parent_id: str | None
    name: str
    start_ns: int
    end_ns: int | None = None
    status: str = "OK"
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[dict[str, Any]] = field(default_factory=list)

    @property
    def duration_ms(self) -> float:
        """返回 span 耗时毫秒数。"""

        if self.end_ns is None:
            return 0.0
        return round((self.end_ns - self.start_ns) / 1_000_000, 3)

    def to_dict(self) -> dict[str, Any]:
        """转换为适合写入 JSON 的字典。"""

        data = asdict(self)
        data["duration_ms"] = self.duration_ms
        return data


class TraceRecorder:
    """用标准库实现一个轻量 trace/span 记录器。"""

    def __init__(self, trace_name: str) -> None:
        self.trace_name = trace_name
        self.trace_id = uuid.uuid4().hex
        self._stack: list[SpanRecord] = []
        self.spans: list[SpanRecord] = []

    @contextmanager
    def span(self, name: str, **attributes: Any) -> Iterator[SpanRecord]:
        """创建一个带父子关系的 span。"""

        parent_id = self._stack[-1].span_id if self._stack else None
        record = SpanRecord(
            trace_id=self.trace_id,
            span_id=uuid.uuid4().hex[:16],
            parent_id=parent_id,
            name=name,
            start_ns=time.perf_counter_ns(),
            attributes=attributes,
        )
        self._stack.append(record)
        self.spans.append(record)
        try:
            yield record
        except Exception as exc:
            record.status = "ERROR"
            record.events.append({"name": "exception", "message": str(exc)})
            raise
        finally:
            record.end_ns = time.perf_counter_ns()
            self._stack.pop()

    def add_event(self, name: str, **attributes: Any) -> None:
        """向当前 span 添加事件。"""

        if not self._stack:
            return
        self._stack[-1].events.append({"name": name, "attributes": attributes})

    def summary(self) -> dict[str, Any]:
        """生成一次 trace 的聚合摘要。"""

        total_ms = sum(span.duration_ms for span in self.spans if span.parent_id is None)
        llm_input_tokens = sum(int(span.attributes.get("input_tokens", 0)) for span in self.spans)
        llm_output_tokens = sum(int(span.attributes.get("output_tokens", 0)) for span in self.spans)
        cost_usd = sum(float(span.attributes.get("cost_usd", 0.0)) for span in self.spans)
        return {
            "trace_name": self.trace_name,
            "trace_id": self.trace_id,
            "root_duration_ms": round(total_ms, 3),
            "span_count": len(self.spans),
            "error_count": sum(1 for span in self.spans if span.status == "ERROR"),
            "input_tokens": llm_input_tokens,
            "output_tokens": llm_output_tokens,
            "estimated_cost_usd": round(cost_usd, 6),
        }

    def write_json(self, path: Path) -> None:
        """将 trace 写入 JSON 文件。"""

        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "summary": self.summary(),
            "spans": [span.to_dict() for span in self.spans],
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


KNOWLEDGE_BASE: dict[str, str] = {
    "langgraph": "LangGraph 适合多步骤、需要显式控制流程、需要状态持久化的复杂 Agent 工作流。",
    "opentelemetry": "OpenTelemetry 中 trace 表示一次完整请求路径，span 表示 trace 内的一个具体步骤。",
    "lora": "LoRA 冻结基础模型参数，只训练低秩适配器里的少量参数，因此微调成本更低。",
    "gaia": "GAIA 用真实问题评测 Agent 的多步骤推理、工具使用、检索和信息整合能力。",
}


ALLOWED_OPERATORS: dict[type[ast.operator], Any] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def estimate_llm_cost(input_tokens: int, output_tokens: int) -> float:
    """用固定价格估算一次教学 LLM 调用成本。"""

    return input_tokens * 0.0000002 + output_tokens * 0.0000008


def safe_calculate(expression: str) -> str:
    """安全计算只包含数字和四则运算的表达式。"""

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPERATORS:
            return ALLOWED_OPERATORS[type(node.op)](visit(node.left), visit(node.right))
        raise ValueError("只允许数字和 + - * /")

    value = visit(ast.parse(expression, mode="eval"))
    return str(int(value)) if value.is_integer() else str(value)


def keyword_search(query: str) -> dict[str, Any]:
    """在本地知识库里检索最相关的资料。"""

    normalized = query.lower()
    for keyword, answer in KNOWLEDGE_BASE.items():
        if keyword in normalized or keyword in query:
            return {"keyword": keyword, "content": answer}
    if "遥测" in query or "可观测" in query:
        return {"keyword": "opentelemetry", "content": KNOWLEDGE_BASE["opentelemetry"]}
    return {"keyword": "unknown", "content": "本地知识库没有找到足够证据。"}


class TeachingObservableAgent:
    """一个可观测的教学 Agent。"""

    def run(self, user_input: str, recorder: TraceRecorder) -> dict[str, Any]:
        """运行 Agent，并将关键步骤写入 recorder。"""

        with recorder.span("agent.run", user_input=user_input) as root:
            with recorder.span(
                "llm.plan",
                model="teaching-rule-model",
                input_tokens=len(user_input),
                output_tokens=36,
                cost_usd=estimate_llm_cost(len(user_input), 36),
            ) as plan_span:
                plan = self._plan(user_input)
                plan_span.attributes["plan"] = plan

            if plan["tool"] == "calculator":
                with recorder.span("tool.calculator", expression=plan["arguments"]["expression"]) as tool_span:
                    observation = safe_calculate(plan["arguments"]["expression"])
                    tool_span.attributes["result"] = observation
            elif plan["tool"] == "search":
                with recorder.span("tool.search", query=plan["arguments"]["query"]) as tool_span:
                    observation = keyword_search(plan["arguments"]["query"])
                    tool_span.attributes["result_keyword"] = observation["keyword"]
            else:
                observation = {"content": "无需工具，直接回答。"}

            with recorder.span(
                "llm.final_answer",
                model="teaching-rule-model",
                input_tokens=len(str(observation)) + len(user_input),
                output_tokens=72,
                cost_usd=estimate_llm_cost(len(str(observation)) + len(user_input), 72),
            ) as answer_span:
                answer = self._answer(user_input, plan, observation)
                answer_span.attributes["answer_preview"] = answer[:120]

            root.attributes["final_answer"] = answer
            root.attributes["used_tool"] = plan["tool"]
            return {
                "input": user_input,
                "answer": answer,
                "used_tool": plan["tool"],
                "observation": observation,
                "trace_id": recorder.trace_id,
            }

    def _plan(self, user_input: str) -> dict[str, Any]:
        """根据问题决定是否需要工具。"""

        lowered = user_input.lower()
        if "7 * 8" in user_input or "7*8" in user_input:
            return {"tool": "calculator", "arguments": {"expression": "7 * 8"}}
        if any(keyword in lowered for keyword in ("langgraph", "opentelemetry", "lora", "gaia")):
            return {"tool": "search", "arguments": {"query": lowered}}
        if any(keyword in user_input for keyword in ("可观测", "遥测", "评估")):
            return {"tool": "search", "arguments": {"query": user_input}}
        return {"tool": "none", "arguments": {}}

    def _answer(self, user_input: str, plan: dict[str, Any], observation: Any) -> str:
        """根据工具观察结果生成最终答案。"""

        if plan["tool"] == "calculator":
            return f"7 * 8 = {observation}。这是简单算术，不需要搜索。"
        if plan["tool"] == "search":
            if observation["keyword"] == "unknown":
                return "本地知识库没有足够证据，我不能假装已经查到可靠答案。"
            return observation["content"]
        return f"这是一个无需外部工具的简短回答：{user_input}"


def score_answer(answer: str, expected_keywords: list[str], forbidden_keywords: list[str]) -> dict[str, Any]:
    """根据关键词和禁用词给回答打一个可重复的教学分数。"""

    matched = [keyword for keyword in expected_keywords if keyword.lower() in answer.lower()]
    violations = [keyword for keyword in forbidden_keywords if keyword.lower() in answer.lower()]
    keyword_score = len(matched) / max(len(expected_keywords), 1)
    penalty = 0.25 * len(violations)
    score = max(0.0, min(1.0, keyword_score - penalty))
    return {
        "score": round(score, 3),
        "matched_keywords": matched,
        "violations": violations,
        "passed": score >= 0.8 and not violations,
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """读取 JSONL 文件。"""

    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: Any) -> None:
    """写入格式化 JSON 文件。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
