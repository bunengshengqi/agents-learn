"""
Day15: vlm_api_shape_demo.py

这个脚本不调用 API，只打印“原生 VLM 写法”和“DeepSeek 改造写法”的区别。

课程原版的关键点是：
- 如果底层模型是真正的 VLM，可以在 agent.run(..., images=images) 中传入图片。
- 如果底层模型是 DeepSeek 文本模型，就应该先通过工具把图片转成文本 observation。

运行：

python vlm_api_shape_demo.py
"""

from __future__ import annotations


def show_original_vlm_shape() -> None:
    """展示课程中 VLM 模型的典型写法。"""
    print("=" * 80)
    print("原生 VLM 写法：适合 GPT-4o 这类支持图片输入的模型")
    print("=" * 80)
    print(
        """
images = [image_1, image_2]

answer = agent.run(
    "请描述这些图片，并判断来宾扮演的是谁。",
    images=images,
)
""".strip()
    )


def show_deepseek_friendly_shape() -> None:
    """展示 DeepSeek 文本模型更适合的改造写法。"""
    print("\n" + "=" * 80)
    print("DeepSeek 改造写法：视觉工具先转文本，DeepSeek 再推理")
    print("=" * 80)
    print(
        """
image_description = describe_guest_image("guest_claim_wonder_woman")

answer = agent.run(
    f'''
    下面是视觉工具返回的图片描述：
    {image_description}

    请根据描述判断来宾扮演的是谁，并说明理由。
    '''
)
""".strip()
    )


def main() -> None:
    """打印两种代码形态的区别。"""
    show_original_vlm_shape()
    show_deepseek_friendly_shape()


if __name__ == "__main__":
    main()

