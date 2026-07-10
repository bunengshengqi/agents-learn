# Day31：AI 智能体可观测性与评估

本目录对应：

```text
notes/Day31-AI智能体可观测性与评估.md
```

## 学习顺序

1. `01_trace_one_run.py`：用本地 JSON trace 看懂 trace/span。
2. `02_online_metrics_dashboard.py`：模拟线上成本、延迟、错误和用户反馈。
3. `03_offline_evaluation.py`：用固定测试集做离线评估。
4. `04_llm_as_judge_openai_compatible.py`：调用真实 OpenAI-compatible API 做自动评分。
5. `05_smolagents_langfuse_template.py`：接入教材里的 smolagents + OpenTelemetry + Langfuse。

## 零依赖脚本

前三个脚本只使用 Python 标准库：

```bash
python3 examples/31-agent-observability-evaluation/01_trace_one_run.py
python3 examples/31-agent-observability-evaluation/02_online_metrics_dashboard.py
python3 examples/31-agent-observability-evaluation/03_offline_evaluation.py
```

输出会写入：

```text
examples/31-agent-observability-evaluation/outputs/
```

`outputs/` 已加入本目录 `.gitignore`，不会提交到 GitHub。

## 真实 LLM-as-a-Judge

如果项目根目录 `.env` 里已经有：

```text
OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
```

可以运行：

```bash
python3 examples/31-agent-observability-evaluation/04_llm_as_judge_openai_compatible.py --run
```

不加 `--run` 时只会预览待评估样本，不会调用接口。

## smolagents + Langfuse

安装依赖：

```bash
python3 -m pip install -r examples/31-agent-observability-evaluation/requirements.txt
```

需要配置：

```text
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
HF_TOKEN=hf_...
```

然后运行：

```bash
python3 examples/31-agent-observability-evaluation/05_smolagents_langfuse_template.py --run
```

说明：

- `LANGFUSE_HOST` 可以换成 `https://us.cloud.langfuse.com` 或自部署地址；
- `HF_TOKEN` 用于 Hugging Face 推理调用；
- 该脚本不会打印任何密钥；
- 如果依赖或环境变量缺失，脚本会给出提示。

## 文件说明

| 文件 | 说明 |
|---|---|
| `agent_core.py` | 本地 Agent、TraceRecorder、评分函数 |
| `01_trace_one_run.py` | 单次运行 trace/span 演示 |
| `02_online_metrics_dashboard.py` | 在线监控指标模拟 |
| `03_offline_evaluation.py` | 离线评估数据集运行 |
| `04_llm_as_judge_openai_compatible.py` | 真实 OpenAI-compatible Judge |
| `05_smolagents_langfuse_template.py` | smolagents + OpenTelemetry + Langfuse 模板 |
| `data/offline_eval_cases.jsonl` | 固定评估集 |
| `requirements.txt` | 可选的 telemetry 依赖 |
