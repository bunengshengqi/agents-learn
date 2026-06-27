# Day15 快速说明

先运行：

```bash
python vision_flow_demo.py
python vlm_api_shape_demo.py
```

再运行真实 DeepSeek Agent：

```bash
python first_agent.py
```

这一节的关键不是“让 DeepSeek 直接看图”，而是：

```text
视觉工具先把图片/截图变成文本 observation，DeepSeek 再根据 observation 推理。
```

