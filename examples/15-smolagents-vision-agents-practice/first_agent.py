"""
Day15: first_agent.py

这是第 15 天的主练习：使用 DeepSeek API 练习“视觉智能体”的工作流。

注意：
- 这个脚本会调用你的真实模型 API。
- 这里不把图片直接传给 DeepSeek。
- Agent 必须先调用视觉工具，把图片或截图变成文字 observation。
- DeepSeek 再根据 observation 做推理。

运行：

python first_agent.py
"""

from __future__ import annotations

from smolagents import CodeAgent

from model_config import build_model
from tools import get_visual_tools


def build_vision_text_agent() -> CodeAgent:
    """
    创建一个 DeepSeek 版视觉智能体。

    这个 Agent 的视觉能力来自工具，而不是来自模型本身：
    - describe_guest_image：模拟图片描述工具。
    - read_text_from_screenshot：模拟 OCR 工具。
    - inspect_screenshot_layout：模拟截图布局分析工具。
    """
    return CodeAgent(
        tools=get_visual_tools(),
        model=build_model(),
        max_steps=8,
        additional_authorized_imports=[],
    )


def run_guest_identity_demo(agent: CodeAgent) -> None:
    """
    练习 1：来宾身份判断。

    这个任务对应课程里“给 Agent 图片，让 Agent 判断角色身份”的场景。
    DeepSeek 不能直接看图，所以必须调用 describe_guest_image。
    """
    task = """
你正在协助 Alfred 检查超级英雄主题派对来宾身份。

来宾声称自己扮演的是 Wonder Woman。
图片名称是：guest_claim_wonder_woman。

请严格按下面流程完成：
1. 先调用 describe_guest_image 获取图片视觉描述，不要凭空猜。
2. 根据工具返回的视觉证据判断来宾更像 Wonder Woman 还是 The Joker。
3. 用中文回答，并说明：
   - 你调用了哪个工具；
   - 工具返回了哪些关键视觉证据；
   - 最终判断是什么；
   - 为什么这个流程适合 DeepSeek 文本模型。
"""

    print("=" * 80)
    print("练习 1：来宾身份判断")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def run_screenshot_debug_demo(agent: CodeAgent) -> None:
    """
    练习 2：网页截图排错。

    这个任务对应课程里“浏览器智能体动态观察截图”的场景。
    DeepSeek 不能直接看截图，所以必须调用 OCR 和布局分析工具。
    """
    task = """
你正在协助 Alfred 排查一个网页报名表单的问题。

截图名称是：party_signup_error。

请严格按下面流程完成：
1. 调用 read_text_from_screenshot 读取截图文字。
2. 调用 inspect_screenshot_layout 获取页面布局描述。
3. 综合两个工具的 observation，判断用户为什么提交失败。
4. 用中文回答，并说明：
   - OCR 发现了什么；
   - 布局分析发现了什么；
   - 该如何修复；
   - 这和课程里的 browser screenshot / observations_images 有什么关系。
"""

    print("\n" + "=" * 80)
    print("练习 2：网页截图排错")
    print("=" * 80)

    answer = agent.run(task)

    print("\nFinal Answer:")
    print(answer)


def main() -> None:
    """创建 Agent，并依次运行两个 Day15 视觉练习。"""
    agent = build_vision_text_agent()

    run_guest_identity_demo(agent)
    run_screenshot_debug_demo(agent)


if __name__ == "__main__":
    main()

