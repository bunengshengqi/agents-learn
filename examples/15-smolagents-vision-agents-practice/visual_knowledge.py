"""
Day15: visual_knowledge.py

这个文件模拟“视觉工具已经看完图片以后得到的结果”。

为什么要这样设计？
- 课程原版使用 GPT-4o 这类 VLM，可以直接看图片。
- 你当前使用 DeepSeek API，不默认具备直接图片输入能力。
- 所以我们先把图片/截图转成文字 observation，再让 DeepSeek 推理。

后续如果你接入真实 OCR、真实截图工具或真实 VLM，只需要替换这里的数据来源。
"""

from __future__ import annotations


GUEST_IMAGE_DESCRIPTIONS: dict[str, str] = {
    "guest_claim_wonder_woman": (
        "图像描述：来宾脸部有白色底妆，嘴唇被画成夸张红色笑容，头发偏绿色，"
        "外套偏紫色，整体更接近 The Joker 的经典造型。没有看到 Wonder Woman "
        "常见的金色头冠、红金胸甲、蓝色裙装或银色护腕。"
    ),
    "guest_real_wonder_woman": (
        "图像描述：来宾佩戴金色头冠，穿红金色胸甲和蓝色裙装，手腕有银色护腕，"
        "整体符合 Wonder Woman 的经典视觉特征。"
    ),
    "guest_unclear_mask": (
        "图像描述：来宾佩戴黑色面具和深色披风，背景光线较暗，只能确认是超级英雄主题装扮，"
        "无法稳定判断具体角色，需要更多图片或人工确认。"
    ),
}


SCREENSHOT_OCR_RESULTS: dict[str, str] = {
    "party_signup_error": (
        "OCR 结果：页面标题为 Superhero Party Signup。表单中 Email 输入框下方出现红色提示："
        "Please enter a valid email address。Submit 按钮处于可点击状态。"
    ),
    "browser_cookie_popup": (
        "OCR 结果：页面中央有弹窗，标题为 We use cookies。按钮包括 Accept all、Reject all、"
        "Customize。弹窗遮挡了下方正文内容。"
    ),
    "agent_course_vision_page": (
        "OCR 结果：页面标题包含 Vision Agents。正文提到 provide images at launch、"
        "dynamic image retrieval、step callbacks、browser screenshots。"
    ),
}


SCREENSHOT_LAYOUT_DESCRIPTIONS: dict[str, str] = {
    "party_signup_error": (
        "布局描述：页面主体是一个报名表单，Email 输入框位于中间区域，错误提示紧贴输入框下方，"
        "Submit 按钮在表单底部。当前最可能的失败原因是邮箱格式不合法。"
    ),
    "browser_cookie_popup": (
        "布局描述：弹窗位于页面中心，遮罩覆盖正文。Accept all 按钮最醒目，Reject all 位于旁边，"
        "在继续阅读网页前应该先处理弹窗。"
    ),
    "agent_course_vision_page": (
        "布局描述：这是一个文档页面，左侧是课程导航，中间是正文，右侧是当前章节目录。"
        "适合使用页面文本提取或 Ctrl+F 查找关键词。"
    ),
}


def list_known_visual_inputs() -> str:
    """返回当前练习项目里可用的模拟图片和截图名称。"""
    guest_names = ", ".join(sorted(GUEST_IMAGE_DESCRIPTIONS))
    screenshot_names = ", ".join(sorted(SCREENSHOT_OCR_RESULTS))

    return (
        "可用来宾图片名称：\n"
        f"{guest_names}\n\n"
        "可用截图名称：\n"
        f"{screenshot_names}"
    )

