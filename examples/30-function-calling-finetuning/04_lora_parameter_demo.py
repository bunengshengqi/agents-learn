"""计算全量线性层微调与 LoRA 的参数量差异。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class ParameterComparison:
    """保存全量权重与 LoRA 适配器的参数统计。"""

    full_parameters: int
    lora_parameters: int

    @property
    def trainable_ratio_percent(self) -> float:
        return self.lora_parameters / self.full_parameters * 100

    @property
    def reduction_percent(self) -> float:
        return 100 - self.trainable_ratio_percent


def compare_parameters(input_size: int, output_size: int, rank: int) -> ParameterComparison:
    """使用 W(d_out, d_in) 与 B(d_out, r)A(r, d_in) 计算参数量。"""

    if min(input_size, output_size, rank) <= 0:
        raise ValueError("input-size、output-size 和 rank 必须是正整数")
    if rank > min(input_size, output_size):
        raise ValueError("rank 不应大于输入或输出维度")

    full_parameters = input_size * output_size
    lora_parameters = rank * input_size + output_size * rank
    return ParameterComparison(full_parameters, lora_parameters)


def parse_args() -> argparse.Namespace:
    """解析矩阵尺寸和 LoRA rank。"""

    parser = argparse.ArgumentParser(description="比较全量微调与 LoRA 的参数量")
    parser.add_argument("--input-size", type=int, default=4096)
    parser.add_argument("--output-size", type=int, default=4096)
    parser.add_argument("--rank", type=int, default=16)
    return parser.parse_args()


def main() -> None:
    """打印参数量与比例。"""

    args = parse_args()
    comparison = compare_parameters(args.input_size, args.output_size, args.rank)

    print(f"原始权重矩阵：{args.output_size} × {args.input_size}")
    print(f"LoRA 矩阵：B({args.output_size} × {args.rank}) × A({args.rank} × {args.input_size})")
    print(f"全量参数：{comparison.full_parameters:,}")
    print(f"LoRA 参数：{comparison.lora_parameters:,}")
    print(f"LoRA / 全量：{comparison.trainable_ratio_percent:.4f}%")
    print(f"减少的可训练参数比例：{comparison.reduction_percent:.4f}%")


if __name__ == "__main__":
    main()

