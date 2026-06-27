"""
Day15: vision_flow_demo.py

这是一个不调用模型 API 的流程演示。

运行：

python vision_flow_demo.py

这个脚本只帮助你看懂：
图片/截图 -> 视觉工具 -> 文本 observation -> DeepSeek 推理
"""

from __future__ import annotations

from visual_knowledge import GUEST_IMAGE_DESCRIPTIONS, SCREENSHOT_LAYOUT_DESCRIPTIONS, SCREENSHOT_OCR_RESULTS


def show_guest_identity_flow() -> None:
    """演示来宾身份判断任务中的视觉 observation 流程。"""
    image_name = "guest_claim_wonder_woman"
    observation = GUEST_IMAGE_DESCRIPTIONS[image_name]

    print("=" * 80)
    print("流程 1：来宾身份判断")
    print("=" * 80)
    print(f"用户给出的图片名称：{image_name}")
    print("\n视觉工具返回的 observation：")
    print(observation)
    print("\n接下来 DeepSeek 应该做的事：")
    print("根据 observation 判断：这个人虽然声称是 Wonder Woman，但视觉特征更像 The Joker。")


def show_screenshot_debug_flow() -> None:
    """演示网页截图排错任务中的 OCR 和布局 observation 流程。"""
    screenshot_name = "party_signup_error"
    ocr_observation = SCREENSHOT_OCR_RESULTS[screenshot_name]
    layout_observation = SCREENSHOT_LAYOUT_DESCRIPTIONS[screenshot_name]

    print("\n" + "=" * 80)
    print("流程 2：网页截图排错")
    print("=" * 80)
    print(f"用户给出的截图名称：{screenshot_name}")
    print("\nOCR 工具返回的 observation：")
    print(ocr_observation)
    print("\n布局分析工具返回的 observation：")
    print(layout_observation)
    print("\n接下来 DeepSeek 应该做的事：")
    print("综合文字和布局，判断错误原因是邮箱格式不合法，并建议修改 Email 输入。")


def main() -> None:
    """运行两个不依赖 API 的视觉流程演示。"""
    show_guest_identity_flow()
    show_screenshot_debug_flow()


if __name__ == "__main__":
    main()

