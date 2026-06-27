"""
Day15: tools.py

这个文件把“视觉能力”封装成 smolagents 工具。

关键思想：
- DeepSeek 不直接看图片。
- 工具负责把图片、截图、网页视觉状态转成文字。
- Agent 读取这些文字 observation 后，再做推理和回答。
"""

from __future__ import annotations

import base64
import mimetypes
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from smolagents import tool

from visual_knowledge import (
    GUEST_IMAGE_DESCRIPTIONS,
    SCREENSHOT_LAYOUT_DESCRIPTIONS,
    SCREENSHOT_OCR_RESULTS,
    list_known_visual_inputs,
)


BASE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = BASE_DIR / "images"
GUEST_IMAGE_DIR = IMAGE_DIR / "guests"
SCREENSHOT_IMAGE_DIR = IMAGE_DIR / "screenshots"
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")


def _is_url(value: str) -> bool:
    """判断输入是否是可直接传给 VLM 的网络图片 URL 或 data URL。"""
    return value.startswith(("http://", "https://", "data:image/"))


def _find_image_file(image_name: str, preferred_dir: Path) -> Path | None:
    """
    根据图片名称查找真实图片文件。

    支持三种输入：
    - 绝对路径：/path/to/image.png
    - 相对路径：images/screenshots/page.png
    - 练习名称：party_signup_error -> images/screenshots/party_signup_error.png
    """
    raw_path = Path(image_name).expanduser()
    candidates: list[Path] = []

    if raw_path.is_absolute():
        candidates.append(raw_path)
    else:
        candidates.extend(
            [
                Path.cwd() / raw_path,
                BASE_DIR / raw_path,
                preferred_dir / raw_path.name,
                IMAGE_DIR / raw_path.name,
            ]
        )

    if raw_path.suffix:
        for candidate in candidates:
            if candidate.is_file():
                return candidate
        return None

    search_dirs = [preferred_dir, IMAGE_DIR, GUEST_IMAGE_DIR, SCREENSHOT_IMAGE_DIR]
    for directory in search_dirs:
        for suffix in IMAGE_SUFFIXES:
            candidate = directory / f"{image_name}{suffix}"
            if candidate.is_file():
                return candidate

    return None


def _image_file_to_data_url(image_path: Path) -> str:
    """把本地图片文件编码成 OpenAI-compatible vision API 可接收的 data URL。"""
    mime_type = mimetypes.guess_type(image_path.name)[0] or "image/png"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _resolve_image_input(image_name: str, preferred_dir: Path) -> tuple[str, str]:
    """
    返回 (来源说明, image_url)。

    image_url 可以是网络 URL、data URL，或由本地图片文件转换出来的 data URL。
    """
    if _is_url(image_name):
        return image_name, image_name

    image_path = _find_image_file(image_name, preferred_dir)
    if image_path is None:
        raise FileNotFoundError(
            "找不到真实图片文件。请把图片放到 "
            f"{preferred_dir}，例如 {preferred_dir / (image_name + '.png')}；"
            "也可以直接传入图片绝对路径或 https 图片 URL。"
        )

    return str(image_path), _image_file_to_data_url(image_path)


def _call_vision_model(image_name: str, preferred_dir: Path, prompt: str) -> str:
    """
    调用 996tokens 上的 gpt-4o 视觉模型，把图片转成文字 observation。

    环境变量：
    - VISION_API_KEY：996tokens 的 API Key。
    - VISION_BASE_URL：996tokens 的 OpenAI-compatible 地址，默认 https://api.996tokens.com/v1。
    - VISION_MODEL：视觉模型名称，默认 gpt-4o。
    """
    load_dotenv()

    source, image_url = _resolve_image_input(image_name, preferred_dir)

    api_key = os.getenv("VISION_API_KEY")
    if not api_key:
        raise RuntimeError("缺少 VISION_API_KEY。请在 .env 中配置 996tokens 的图片识别 API Key。")

    base_url = os.getenv("VISION_BASE_URL", "https://api.996tokens.com/v1")
    model = os.getenv("VISION_MODEL", "gpt-4o")

    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        max_tokens=800,
        messages=[
            {
                "role": "system",
                "content": (
                    "你是一个严格的视觉识别工具。只根据图片本身输出观察结果，"
                    "不要编造看不到的信息。用中文回答，结论要清楚。"
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ],
    )

    content = response.choices[0].message.content
    if not content:
        return f"视觉模型没有返回有效内容。图片来源：{source}"

    return f"图片来源：{source}\n视觉模型：{model}\n{content}"


def _list_image_files(directory: Path) -> str:
    """列出目录里的真实图片文件。"""
    if not directory.exists():
        return "暂无"

    files = sorted(path.name for path in directory.iterdir() if path.suffix.lower() in IMAGE_SUFFIXES)
    return ", ".join(files) if files else "暂无"


@tool
def list_visual_inputs() -> str:
    """
    列出当前练习项目中可用的真实图片、真实截图和课程模拟名称。
    """
    real_inputs = (
        "真实图片目录：\n"
        f"- 来宾图片：{GUEST_IMAGE_DIR}\n"
        f"- 截图图片：{SCREENSHOT_IMAGE_DIR}\n\n"
        "当前找到的真实来宾图片：\n"
        f"{_list_image_files(GUEST_IMAGE_DIR)}\n\n"
        "当前找到的真实截图图片：\n"
        f"{_list_image_files(SCREENSHOT_IMAGE_DIR)}"
    )

    return real_inputs + "\n\n" + list_known_visual_inputs()


@tool
def describe_guest_image(image_name: str) -> str:
    """
    使用 996tokens / gpt-4o 返回真实来宾图片的视觉描述。

    Args:
        image_name: 图片名称、图片路径或 https 图片 URL，比如 guest_claim_wonder_woman。
    """
    prompt = (
        "请详细描述这张派对来宾图片中的可见视觉特征，包括服装、颜色、妆容、道具、"
        "标志性元素。最后判断它更像 Wonder Woman、The Joker，还是无法确定。"
    )

    try:
        return _call_vision_model(image_name, GUEST_IMAGE_DIR, prompt)
    except FileNotFoundError:
        mock_result = GUEST_IMAGE_DESCRIPTIONS.get(image_name)
        if mock_result:
            return "没有找到真实图片文件，下面返回的是课程练习里的模拟图片描述。\n" + mock_result
        return (
            "没有找到真实图片文件，也没有找到对应的模拟图片描述。"
            "请先调用 list_visual_inputs 查看可用名称，或传入真实图片路径。"
        )
    except Exception as error:
        return f"视觉模型识别失败：{error}"


@tool
def read_text_from_screenshot(screenshot_name: str) -> str:
    """
    使用 996tokens / gpt-4o 读取真实截图中的文字。

    Args:
        screenshot_name: 截图名称、图片路径或 https 图片 URL，比如 party_signup_error。
    """
    prompt = (
        "请像 OCR 工具一样读取这张截图里的所有可见文字。"
        "按从上到下、从左到右的顺序输出；如果有错误提示、按钮文字或输入框标签，请特别标出。"
    )

    try:
        return _call_vision_model(screenshot_name, SCREENSHOT_IMAGE_DIR, prompt)
    except FileNotFoundError:
        mock_result = SCREENSHOT_OCR_RESULTS.get(screenshot_name)
        if mock_result:
            return "没有找到真实截图文件，下面返回的是课程练习里的模拟 OCR 结果。\n" + mock_result
        return (
            "没有找到真实截图文件，也没有找到对应的模拟 OCR 结果。"
            "请先调用 list_visual_inputs 查看可用名称，或传入真实截图路径。"
        )
    except Exception as error:
        return f"截图文字识别失败：{error}"


@tool
def inspect_screenshot_layout(screenshot_name: str) -> str:
    """
    使用 996tokens / gpt-4o 返回真实截图的页面布局描述。

    Args:
        screenshot_name: 截图名称、图片路径或 https 图片 URL，比如 party_signup_error。
    """
    prompt = (
        "请分析这张网页或应用截图的布局。说明页面主要区域、表单字段、错误提示、按钮位置、"
        "弹窗或遮挡元素，以及最可能影响用户操作的问题。"
    )

    try:
        return _call_vision_model(screenshot_name, SCREENSHOT_IMAGE_DIR, prompt)
    except FileNotFoundError:
        mock_result = SCREENSHOT_LAYOUT_DESCRIPTIONS.get(screenshot_name)
        if mock_result:
            return "没有找到真实截图文件，下面返回的是课程练习里的模拟布局描述。\n" + mock_result
        return (
            "没有找到真实截图文件，也没有找到对应的模拟布局描述。"
            "请先调用 list_visual_inputs 查看可用名称，或传入真实截图路径。"
        )
    except Exception as error:
        return f"截图布局识别失败：{error}"


@tool
def explain_deepseek_vision_strategy(task_type: str) -> str:
    """
    说明在 DeepSeek 文本模型下应该如何处理视觉任务。

    Args:
        task_type: 任务类型，比如 identity_check、screenshot_debug、webpage_reading、complex_visual_reasoning。
    """
    strategies = {
        "identity_check": (
            "身份核验类任务：先用 describe_guest_image 调用 996tokens / gpt-4o "
            "获得真实图像描述，再让 DeepSeek 根据服装、妆容、标志性物品进行判断。"
        ),
        "screenshot_debug": (
            "截图排错类任务：先用 read_text_from_screenshot 读取文字，再用 "
            "inspect_screenshot_layout 判断错误提示和按钮位置。"
        ),
        "webpage_reading": (
            "网页阅读类任务：优先提取 DOM 文本或网页正文；只有文本不足时再截图并做 OCR 或 VLM 描述。"
        ),
        "complex_visual_reasoning": (
            "复杂视觉推理任务：把图片交给支持图片输入的 VLM，再把 VLM 结果交给 DeepSeek 综合推理。"
        ),
    }

    return strategies.get(
        task_type,
        (
            "未知任务类型。可以输入 identity_check、screenshot_debug、webpage_reading "
            "或 complex_visual_reasoning。"
        ),
    )


def get_visual_tools() -> list:
    """返回 Day15 视觉智能体练习需要的全部工具。"""
    return [
        list_visual_inputs,
        describe_guest_image,
        read_text_from_screenshot,
        inspect_screenshot_layout,
        explain_deepseek_vision_strategy,
    ]
