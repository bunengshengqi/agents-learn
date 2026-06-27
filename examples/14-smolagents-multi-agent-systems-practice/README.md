# Day14-smolagents 多智能体系统练习项目

这个目录对应 Hugging Face Agents Course 第 2.1 单元：

[多智能体系统](https://huggingface.co/learn/agents-course/zh-CN/unit2/smolagents/multi_agent_systems)

Day14 的重点是：

- 什么是多智能体系统。
- 什么是 Manager Agent / Orchestrator Agent。
- `managed_agents` 如何让一个 Agent 管理另一个 Agent。
- `visualize()` 如何查看团队结构。
- 为什么复杂任务适合拆给不同专业 Agent。

## 第一步：安装依赖

```bash
pip install -r examples/14-smolagents-multi-agent-systems-practice/requirements.txt
```

## 第二步：配置真实 API

在项目根目录创建 `.env`：

```env
OPENAI_API_KEY=你的 API Key
OPENAI_BASE_URL=你的中转站地址，例如 https://xxx.com/v1
OPENAI_MODEL=你的模型名称
```

## 第三步：先看不调用模型的手动编排

```bash
cd examples/14-smolagents-multi-agent-systems-practice
python manual_orchestration_demo.py
```

这个脚本帮助你先理解：

```text
Manager 决定做什么
-> Research Agent 查资料
-> Manager 调用计算工具
-> Manager 整合结果
```

## 第四步：运行主线多智能体练习

```bash
python first_agent.py
```

这个脚本会使用你的真实模型 API，并创建两个 Agent：

1. `research_agent`：专业子 Agent，负责查 Batman 拍摄地点和城市坐标。
2. `manager_agent`：管理智能体，负责委派任务、调用计算工具、整合答案。

关键代码：

```python
manager_agent = CodeAgent(
    tools=get_manager_tools(),
    managed_agents=[research_agent],
    model=build_model(),
)
```

只要一个 Agent 有 `managed_agents=[...]`，它就开始扮演 Manager / Orchestrator 的角色。

## 第五步：可选，运行真实 DuckDuckGo 多智能体示例

```bash
python duckduckgo_multi_agent_example.py
```

这个脚本会使用：

- 真实模型 API。
- DuckDuckGo 真实网页搜索。
- Manager Agent + Web Agent 的多智能体结构。

## 文件说明

- `model_config.py`：读取 API 配置，创建模型对象。
- `tools.py`：定义拍摄地点查询、城市坐标查询、货运飞行时间计算工具。
- `manual_orchestration_demo.py`：不调用模型，手动模拟编排流程。
- `first_agent.py`：主线多智能体练习，使用本地稳定工具。
- `duckduckgo_multi_agent_example.py`：可选真实网页检索多智能体示例。

## 今日核心结论

Manager Agent 不是能力最多的 Agent，而是负责组织协作的 Agent。

它的关键职责是：

- 拆解任务。
- 委派专业 Agent。
- 调用自己的工具。
- 收集结果。
- 综合最终答案。

多智能体系统的核心不是“Agent 数量多”，而是：

```text
每个 Agent 有清楚的职责，Manager 负责让它们按顺序协作。
```

