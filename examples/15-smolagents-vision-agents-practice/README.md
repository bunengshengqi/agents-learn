# Day15：smolagents 视觉智能体与浏览器智能体练习

这个目录对应 Hugging Face Agents Course 第 15 天：

[使用 smolagents 构建视觉智能体](https://huggingface.co/learn/agents-course/zh-CN/unit2/smolagents/vision_agents)

## 这份代码解决什么问题

课程原版使用 GPT-4o 这类视觉语言模型，可以直接把图片传给 Agent：

```python
agent.run(task, images=images)
```

你当前使用的是 DeepSeek API。DeepSeek 很适合做推理、工具调用和总结，但你不能默认它像 GPT-4o 一样直接看图片。

所以这份代码采用更适合你的练习方式：

```text
图片 / 截图
-> 视觉工具 / OCR 工具 / 布局分析工具
-> 文本 observation
-> DeepSeek Agent 推理
-> 中文最终答案
```

## 文件说明

| 文件 | 作用 |
|---|---|
| `model_config.py` | 读取 `.env`，创建 DeepSeek / OpenAI-compatible 模型 |
| `visual_knowledge.py` | 模拟图片描述、OCR 结果、截图布局分析结果 |
| `tools.py` | 把视觉能力封装成 smolagents 工具 |
| `vision_flow_demo.py` | 不调用 API，只演示视觉 observation 流程 |
| `first_agent.py` | 调用真实 DeepSeek API，让 Agent 使用视觉工具完成任务 |
| `vlm_api_shape_demo.py` | 对比 GPT-4o 原生图片输入写法和 DeepSeek 改造写法 |
| `requirements.txt` | 本目录需要的 Python 依赖 |

## 先运行无 API 演示

```bash
cd /Users/yuyuan/Desktop/agents-learn/examples/15-smolagents-vision-agents-practice
python vision_flow_demo.py
python vlm_api_shape_demo.py
```

这两个脚本不会调用模型 API，适合先理解流程。

## 再运行真实 Agent

确保项目根目录 `.env` 里已经配置：

```bash
OPENAI_API_KEY=你的真实 API Key
OPENAI_MODEL=你的模型名
OPENAI_BASE_URL=你的 DeepSeek 或中转 API 地址
```

如果要让第 15 天工具真正识别图片，而不是使用课程里的模拟 observation，再额外配置 996tokens 的视觉模型：

```bash
VISION_API_KEY=你的 996tokens API Key
VISION_BASE_URL=https://api.996tokens.com/v1
VISION_MODEL=gpt-4o
```

`OPENAI_*` 给 DeepSeek Agent 使用，负责推理和工具调用。`VISION_*` 只给 `tools.py` 里的图片识别工具使用，负责把图片或截图变成文字 observation。

真实图片放到：

```text
images/guests/guest_claim_wonder_woman.png
images/screenshots/party_signup_error.png
```

也可以在任务里直接传入图片绝对路径或 `https` 图片 URL。

然后运行：

```bash
cd /Users/yuyuan/Desktop/agents-learn/examples/15-smolagents-vision-agents-practice
python first_agent.py
```

## 这个 Agent 的核心流程

`first_agent.py` 里创建的是：

```text
CodeAgent = DeepSeek 模型 + 视觉工具菜单 + 执行规则
```

当用户说“图片名称是 guest_claim_wonder_woman”时，Agent 不应该直接猜，而应该先调用：

```python
describe_guest_image("guest_claim_wonder_woman")
```

如果 `images/guests/guest_claim_wonder_woman.png` 存在，工具会调用 996tokens / gpt-4o 识别真实图片，并返回文本 observation。

如果没有真实图片文件，工具会明确提示“没有找到真实图片文件”，然后回退到课程练习里的模拟 observation：

```text
白色底妆、绿色头发、红色夸张笑容、紫色外套，更像 The Joker。
```

然后 DeepSeek 根据这个 observation 得出结论。

## 和课程原版有什么区别

| 对比项 | 课程原版 | 这份代码 |
|---|---|---|
| 模型 | GPT-4o / VLM | DeepSeek / OpenAI-compatible 文本模型 |
| 图片输入 | `images=images` | 先由工具转成文本 observation |
| 截图处理 | `observations_images` 交给 VLM | OCR / 布局工具转成文本 |
| 核心能力 | 模型直接看图 | 工具看图，模型推理 |
| 学习重点 | 原生视觉 Agent | DeepSeek 版视觉 Agent 架构 |

## 后续如何接入真实图片

现在 `tools.py` 里的视觉工具是模拟实现。

以后你可以逐步替换：

```text
describe_guest_image
-> 调用真实 VLM API 或本地视觉模型

read_text_from_screenshot
-> 调用 OCR 工具

inspect_screenshot_layout
-> 调用浏览器截图分析工具或 VLM
```

替换工具内部实现后，`first_agent.py` 的 Agent 流程基本不用改。
