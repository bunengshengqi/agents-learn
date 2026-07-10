"""使用 Transformers、SFTTrainer 与 PEFT LoRA 进行真实函数调用微调。"""

from __future__ import annotations

import argparse
import inspect
import json
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DATASET = SCRIPT_DIR / "data" / "function_calling_sft.jsonl"
DEFAULT_OUTPUT_DIR = SCRIPT_DIR / "outputs" / "function-calling-lora"
DEFAULT_MODEL_ID = "HuggingFaceTB/SmolLM2-135M-Instruct"

SPECIAL_TOKENS = [
    "<|available_tools|>",
    "<|end_available_tools|>",
    "<|user|>",
    "<|thought|>",
    "<|tool_call|>",
    "<|observation|>",
    "<|final|>",
    "<|end|>",
]


def parse_args() -> argparse.Namespace:
    """解析训练参数；默认只预览，显式传入 --run 才下载并训练。"""

    parser = argparse.ArgumentParser(
        description="真实 SFTTrainer + LoRA 函数调用微调示例",
    )
    parser.add_argument("--run", action="store_true", help="真正开始下载模型和训练")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--learning-rate", type=float, default=2e-4)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4)
    parser.add_argument("--max-length", type=int, default=1024)
    parser.add_argument("--lora-rank", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def validate_dataset(path: Path) -> int:
    """在加载训练框架前，先校验 JSONL 的 prompt-completion 结构。"""

    if not path.exists():
        raise FileNotFoundError(
            f"找不到数据集：{path}\n"
            "请先运行 03_sft_dataset_builder.py。"
        )

    record_count = 0
    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            record = json.loads(line)
            missing = {"prompt", "completion"} - record.keys()
            if missing:
                raise ValueError(f"第 {line_number} 行缺少字段：{sorted(missing)}")
            record_count += 1

    if record_count < 2:
        raise ValueError("数据集至少需要两条记录，才能划分训练集和验证集")
    return record_count


def print_preview(args: argparse.Namespace, record_count: int) -> None:
    """输出将要执行的真实训练配置。"""

    print("训练配置预览：")
    print(f"- 基础模型：{args.model_id}")
    print(f"- 数据集：{args.dataset}")
    print(f"- 记录数：{record_count}")
    print(f"- 输出目录：{args.output_dir}")
    print(f"- epochs：{args.epochs}")
    print(f"- learning rate：{args.learning_rate}")
    print(f"- LoRA rank / alpha：{args.lora_rank} / {args.lora_alpha}")
    print("- 损失：只计算 completion，不训练模型复述用户 prompt")
    print("- 特殊 token：只训练新增 token 的 embedding，并训练 LoRA adapter")


def build_lora_config(
    lora_config_class: type[Any],
    task_type: Any,
    args: argparse.Namespace,
    new_token_ids: list[int],
) -> Any:
    """配置 LoRA，并兼容较旧 PEFT 对新增 token 训练方式的差异。"""

    kwargs: dict[str, Any] = {
        "r": args.lora_rank,
        "lora_alpha": args.lora_alpha,
        "lora_dropout": 0.05,
        "target_modules": "all-linear",
        "bias": "none",
        "task_type": task_type,
    }
    parameters = inspect.signature(lora_config_class).parameters

    if new_token_ids and "trainable_token_indices" in parameters:
        kwargs["trainable_token_indices"] = new_token_ids
        if "ensure_weight_tying" in parameters:
            kwargs["ensure_weight_tying"] = True
    elif new_token_ids:
        kwargs["modules_to_save"] = ["embed_tokens", "lm_head"]
        print(
            "警告：当前 PEFT 不支持 trainable_token_indices，"
            "将完整保存输入 embedding 与 lm_head。"
        )

    return lora_config_class(**kwargs)


def generate_sample(
    model: Any,
    tokenizer: Any,
    prompt: str,
    torch_module: Any,
    max_new_tokens: int = 160,
) -> str:
    """训练完成后，使用当前 adapter 进行一次真实自回归生成。"""

    model.eval()
    device = next(model.parameters()).device
    encoded = tokenizer(prompt, return_tensors="pt")
    encoded = {name: tensor.to(device) for name, tensor in encoded.items()}

    with torch_module.inference_mode():
        generated = model.generate(
            **encoded,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    prompt_length = encoded["input_ids"].shape[1]
    new_tokens = generated[0, prompt_length:]
    return tokenizer.decode(new_tokens, skip_special_tokens=False)


def run_training(args: argparse.Namespace) -> None:
    """加载真实依赖、模型、数据集并训练 LoRA adapter。"""

    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, TaskType
        from transformers import AutoModelForCausalLM, AutoTokenizer, set_seed
        from trl import SFTConfig, SFTTrainer
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "缺少训练依赖。请运行：\n"
            "python3 -m pip install -r "
            "examples/30-function-calling-finetuning/requirements-training.txt\n"
            f"原始错误：{exc}"
        ) from exc

    set_seed(args.seed)
    print(f"正在加载 tokenizer：{args.model_id}")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    vocabulary_before = set(tokenizer.get_vocab())
    tokenizer.add_special_tokens({"additional_special_tokens": SPECIAL_TOKENS})
    newly_added_tokens = [token for token in SPECIAL_TOKENS if token not in vocabulary_before]
    new_token_ids = tokenizer.convert_tokens_to_ids(newly_added_tokens)

    print(f"正在加载基础模型：{args.model_id}")
    model = AutoModelForCausalLM.from_pretrained(args.model_id)
    if newly_added_tokens:
        model.resize_token_embeddings(len(tokenizer))
    model.config.use_cache = False

    dataset = load_dataset("json", data_files=str(args.dataset), split="train")
    split_dataset = dataset.train_test_split(test_size=0.2, seed=args.seed)

    lora_config = build_lora_config(
        LoraConfig,
        TaskType.CAUSAL_LM,
        args,
        new_token_ids,
    )
    training_config = SFTConfig(
        output_dir=str(args.output_dir),
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        logging_steps=1,
        save_strategy="epoch",
        report_to="none",
        max_length=args.max_length,
        completion_only_loss=True,
        packing=False,
        seed=args.seed,
    )
    trainer = SFTTrainer(
        model=model,
        args=training_config,
        train_dataset=split_dataset["train"],
        eval_dataset=split_dataset["test"],
        processing_class=tokenizer,
        peft_config=lora_config,
    )

    print("开始真实 LoRA 训练。")
    trainer.train()
    metrics = trainer.evaluate()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(args.output_dir))
    tokenizer.save_pretrained(str(args.output_dir))

    sample_prompt = split_dataset["test"][0]["prompt"]
    sample_output = generate_sample(trainer.model, tokenizer, sample_prompt, torch)

    print("\n验证集指标：")
    for name, value in sorted(metrics.items()):
        print(f"- {name}: {value}")
    print(f"\nLoRA adapter 已保存到：{args.output_dir}")
    print("\n训练后真实生成样例：")
    print(sample_output)
    print("\n注意：教学数据很小，输出不代表生产质量。")


def main() -> None:
    """先预览配置；只有 --run 时才真正下载模型并训练。"""

    args = parse_args()
    record_count = validate_dataset(args.dataset)
    print_preview(args, record_count)

    if not args.run:
        print("\n当前是安全预览模式，没有下载模型，也没有开始训练。")
        print("确认配置后添加 --run 才会真正执行。")
        return

    run_training(args)


if __name__ == "__main__":
    main()

