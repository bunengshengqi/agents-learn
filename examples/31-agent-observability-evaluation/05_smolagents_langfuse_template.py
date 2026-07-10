"""接近教材的 smolagents + OpenTelemetry + Langfuse 模板。"""

from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_dotenv(path: Path) -> None:
    """加载简单的 KEY=VALUE 形式 .env 文件。"""

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def configure_langfuse_otel() -> None:
    """根据 Langfuse 密钥配置 OpenTelemetry OTLP 出口。"""

    public_key = os.environ["LANGFUSE_PUBLIC_KEY"]
    secret_key = os.environ["LANGFUSE_SECRET_KEY"]
    host = os.environ.get("LANGFUSE_HOST", "https://cloud.langfuse.com").rstrip("/")
    auth = base64.b64encode(f"{public_key}:{secret_key}".encode("utf-8")).decode("utf-8")
    os.environ["LANGFUSE_HOST"] = host
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{host}/api/public/otel"
    os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {auth}"


def main() -> None:
    """配置遥测并运行一个最小 smolagents 示例。"""

    parser = argparse.ArgumentParser()
    parser.add_argument("--run", action="store_true", help="真正运行 smolagents 并发送 trace")
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")
    required = ["LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "HF_TOKEN"]
    missing = [name for name in required if not os.environ.get(name)]

    if not args.run:
        print("预览模式：该脚本会配置 Langfuse OTLP，并运行一个 smolagents CodeAgent。")
        print("真正运行：python3 examples/31-agent-observability-evaluation/05_smolagents_langfuse_template.py --run")
        return

    if missing:
        raise SystemExit(f"缺少环境变量：{', '.join(missing)}")

    try:
        from openinference.instrumentation.smolagents import SmolagentsInstrumentor
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from smolagents import CodeAgent, InferenceClientModel
    except ImportError as exc:
        raise SystemExit(
            "缺少依赖，请先运行：python3 -m pip install -r "
            "examples/31-agent-observability-evaluation/requirements.txt"
        ) from exc

    configure_langfuse_otel()

    trace_provider = TracerProvider()
    trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
    trace.set_tracer_provider(trace_provider)
    SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)

    tracer = trace.get_tracer(__name__)
    model = InferenceClientModel()
    agent = CodeAgent(tools=[], model=model)

    with tracer.start_as_current_span("day31-smolagents-test") as span:
        span.set_attribute("langfuse.tags", ["day31", "observability", "smolagents"])
        span.set_attribute("langfuse.session.id", "agents-learn-day31")
        output = agent.run("1+1=")

    print("Agent output:")
    print(output)
    print("Trace 已发送到 Langfuse，请打开你的 Langfuse 项目查看。")


if __name__ == "__main__":
    main()
