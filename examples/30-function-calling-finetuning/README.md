# Day30：函数调用模型微调与 LoRA

本目录对应：

```text
notes/Day30-函数调用模型微调与LoRA.md
```

## 学习顺序

前五个教学步骤分别回答：

1. Agent 的 Thought → Act → Observe 循环如何真正执行？
2. 特殊 token 如何把用户、行动、观察和最终答案分开？
3. SFT 训练数据到底长什么样？
4. LoRA 为什么能减少可训练参数？
5. 如何使用真实 `Transformers + TRL SFTTrainer + PEFT LoRA` 开始训练？
6. 训练后如何验收函数调用结果？

## 零依赖脚本

以下脚本只使用 Python 标准库：

```bash
python3 examples/30-function-calling-finetuning/01_function_calling_loop.py
python3 examples/30-function-calling-finetuning/02_special_tokens_formatter.py
python3 examples/30-function-calling-finetuning/03_sft_dataset_builder.py
python3 examples/30-function-calling-finetuning/04_lora_parameter_demo.py
python3 examples/30-function-calling-finetuning/06_function_calling_evaluator.py
```

`01` 中的工具是真正被 Python 调用的；为了离线稳定学习，天气返回使用固定数据。这里的重点是分清模型决策、调度器和工具执行。

## 真实 LoRA 训练

先创建单独环境，并安装训练依赖：

```bash
python3 -m venv .venv-day30
source .venv-day30/bin/activate
python3 -m pip install -r examples/30-function-calling-finetuning/requirements-training.txt
```

先查看配置，不下载模型：

```bash
python3 examples/30-function-calling-finetuning/05_real_sfttrainer_lora.py
```

确认后真正开始训练：

```bash
python3 examples/30-function-calling-finetuning/05_real_sfttrainer_lora.py --run
```

默认基础模型：

```text
HuggingFaceTB/SmolLM2-135M-Instruct
```

可以换成其他 Causal LM：

```bash
python3 examples/30-function-calling-finetuning/05_real_sfttrainer_lora.py \
  --run \
  --model-id Qwen/Qwen2.5-0.5B-Instruct \
  --epochs 3
```

说明：

- 首次运行会从 Hugging Face 下载基础模型；
- 这是本地开源权重训练，不读取项目 `.env` 中的 OpenAI-compatible API 配置；
- 真正训练需要 `torch`，速度取决于 CPU、Apple Silicon、CUDA GPU 和模型大小；
- 示例数据用于理解流程，不足以训练生产模型；
- 输出目录只保存 LoRA adapter，不会提交进 Git；
- macOS 内存较小时先使用默认 135M 模型验证流程。

## 文件说明

| 文件 | 说明 |
|---|---|
| `01_function_calling_loop.py` | 完整可执行工具循环 |
| `02_special_tokens_formatter.py` | 特殊 token 格式化与顺序校验 |
| `03_sft_dataset_builder.py` | 生成 prompt-completion JSONL 数据，训练脚本再按 8:2 划分 |
| `04_lora_parameter_demo.py` | LoRA 参数量计算器 |
| `05_real_sfttrainer_lora.py` | 真实 SFTTrainer + LoRA 训练入口 |
| `06_function_calling_evaluator.py` | 函数调用静态评测示例 |
| `data/function_calling_sft.jsonl` | 小型教学数据集 |
| `requirements-training.txt` | 真实训练依赖 |
