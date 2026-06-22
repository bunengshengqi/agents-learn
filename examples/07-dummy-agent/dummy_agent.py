"""
Day 7: Dummy Agent Library

这个脚本是一个“简单智能体库”的教学版实现。

它把前 6 天的知识串起来：

- Day 1：LLM 负责理解文本和生成文本
- Day 2：messages 保存上下文
- Day 3：Thought -> Action -> Observation 循环
- Day 4：Thought 负责推理和规划
- Day 5：Action 用 JSON 表达工具调用
- Day 6：Observation 是工具执行后的现实反馈，必须放回 messages
- Day 7：把这些零件封装成一个 DummyAgent 类

运行前需要在项目根目录准备 .env：

OPENAI_API_KEY=你的 key
OPENAI_BASE_URL=你的中转站地址
OPENAI_MODEL=你的模型名
"""

import json
import os
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI

from tools import TOOL_DESCRIPTIONS, TOOLS


load_dotenv()


class DummyAgent:
    """
    极简智能体类。

    对应知识点：
    - 这就是“简单智能体库”的核心。
    - 真正框架会更复杂，但底层仍然离不开：
      messages、LLM、Action、Tool、Observation、Loop。
    """

    def __init__(self) -> None:
        """
        初始化 Agent。

        对应知识点：
        - Day 2 messages：Agent 需要保存上下文。
        - Day 5 tools：Agent 需要知道自己有哪些工具。
        """
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.model = os.getenv("OPENAI_MODEL")

        self.client = self._build_client()

        self.messages: list[dict[str, str]] = [
            {
                "role": "system",
                "content": self._build_system_prompt(),
            }
        ]

    def _build_client(self) -> OpenAI:
        """
        创建 OpenAI 兼容客户端。

        对应知识点：
        - Day 7 Serverless API：不自己部署模型，通过 API 调用模型。
        - 这里使用你的 OpenAI 兼容中转站，而不是 Hugging Face API。
        """
        missing = []

        if not self.api_key:
            missing.append("OPENAI_API_KEY")
        if not self.base_url:
            missing.append("OPENAI_BASE_URL")
        if not self.model:
            missing.append("OPENAI_MODEL")

        if missing:
            raise ValueError("缺少环境变量：" + ", ".join(missing))

        return OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60.0,
        )

    def _build_system_prompt(self) -> str:
        """
        构造 system prompt。

        对应知识点：
        - Day 2 system message：定义 Agent 的身份和规则。
        - Day 5 Action：规定模型必须用 JSON 表达工具调用。
        - Day 6 Observation：告诉模型拿到 Observation 后再输出最终答案。
        """
        return f"""
你是一个教学用 Dummy Agent。

你的任务：
1. 理解用户问题。
2. 如果需要工具，输出 Thought 和 Action。
3. Action 必须是严格 JSON，不要使用 Markdown 代码块。
4. 程序会解析 Action，执行工具，并把结果作为 Observation 放回 messages。
5. 当你看到 Observation 后，基于 Observation 输出 Final Answer。

{TOOL_DESCRIPTIONS}

当你需要调用工具时，必须输出下面格式：

Thought: 这里写简短推理，说明为什么需要工具。
Action:
{{
  "action": "工具名称",
  "action_input": {{
    "参数名": "参数值"
  }}
}}

当你已经可以回答用户时，输出：

Final Answer: 这里写最终中文答案。

注意：
- 不要自己编造 Observation。
- 不要在没有执行工具的情况下假装已经拿到工具结果。
- 如果用户问题不需要工具，可以直接输出 Final Answer。
"""

    def call_llm(self) -> str:
        """
        调用大模型。

        对应知识点：
        - Day 1 LLM：模型根据输入生成输出。
        - Day 2 messages：每次调用都把完整 messages 发给模型。
        - Day 7 chat 方法：使用 messages，而不是手写特殊 token。
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0.1,
        )

        return response.choices[0].message.content or ""

    def extract_action(self, text: str) -> dict[str, Any] | None:
        """
        从模型输出中提取 Action JSON。

        对应知识点：
        - Day 5 Stop and Parse：
          模型输出 Action 后，程序停下来解析 JSON。
        """
        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1 or end <= start:
            return None

        json_text = text[start : end + 1]

        try:
            action = json.loads(json_text)
        except json.JSONDecodeError as exc:
            return {
                "action": "__parse_error__",
                "action_input": {
                    "error": str(exc),
                    "raw_text": text,
                },
            }

        if "action" not in action or "action_input" not in action:
            return {
                "action": "__parse_error__",
                "action_input": {
                    "error": "Action JSON 必须包含 action 和 action_input",
                    "raw_text": text,
                },
            }

        return action

    def run_tool(self, action: dict[str, Any]) -> dict[str, Any]:
        """
        根据 Action 执行工具。

        对应知识点：
        - Day 5 Action：Action 决定调用哪个工具。
        - Day 6 Observation：工具返回结果会包装成结构化 Observation。
        """
        tool_name = action["action"]
        tool_input = action["action_input"]

        if tool_name == "__parse_error__":
            return {
                "status": "error",
                "tool": "action_parser",
                "error_type": "json_parse_error",
                "message": tool_input["error"],
                "retryable": True,
            }

        tool = TOOLS.get(tool_name)

        if tool is None:
            return {
                "status": "error",
                "tool": tool_name,
                "error_type": "unknown_tool",
                "message": f"未知工具：{tool_name}",
                "retryable": False,
            }

        try:
            result = tool(**tool_input)
        except TypeError as exc:
            return {
                "status": "error",
                "tool": tool_name,
                "error_type": "bad_arguments",
                "message": str(exc),
                "retryable": True,
            }
        except Exception as exc:
            return {
                "status": "error",
                "tool": tool_name,
                "error_type": type(exc).__name__,
                "message": str(exc),
                "retryable": False,
            }

        return {
            "status": "success",
            "tool": tool_name,
            "data": result,
            "retryable": False,
        }

    def append_observation(self, observation: dict[str, Any]) -> None:
        """
        把 Observation 放回 messages。

        对应知识点：
        - Day 6：Observation 必须进入上下文。
        - 模型下一轮才能根据真实工具结果继续思考。
        """
        self.messages.append(
            {
                "role": "user",
                "content": f"Observation: {observation}\n请基于这个 Observation 继续。如果已足够回答，请输出 Final Answer。",
            }
        )

    def run(self, user_input: str, max_steps: int = 3) -> str:
        """
        运行 Agent。

        对应知识点：
        - Day 3 Agent Loop：Thought -> Action -> Observation。
        - Day 7 Dummy Agent：把循环封装成 agent.run()。

        参数：
        - user_input：用户输入
        - max_steps：最多允许几轮工具调用，防止无限循环
        """
        self.messages.append(
            {
                "role": "user",
                "content": user_input,
            }
        )

        for step in range(1, max_steps + 1):
            print(f"\n===== Step {step}: LLM 输出 =====")

            assistant_output = self.call_llm()
            print(assistant_output)

            self.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_output,
                }
            )

            if "Final Answer:" in assistant_output:
                return assistant_output

            action = self.extract_action(assistant_output)

            if action is None:
                return "Final Answer: 模型没有输出 Action，也没有输出 Final Answer，流程结束。"

            print("\n===== Stop and Parse：解析到 Action =====")
            print(action)

            observation = self.run_tool(action)

            print("\n===== Execute：工具执行结果 Observation =====")
            print(observation)

            self.append_observation(observation)

        return "Final Answer: 已达到最大工具调用次数，流程停止，建议人工检查。"


def main() -> None:
    """
    命令行入口。

    推荐测试：
    - 3 乘以 4 等于多少？
    - 今天苏州天气怎么样？
    """
    agent = DummyAgent()

    print("Day 7: Dummy Agent Library")
    print("输入 exit / quit / q 退出")
    print("推荐测试：")
    print("1. 3 乘以 4 等于多少？")
    print("2. 今天苏州天气怎么样？")
    print("-" * 60)

    while True:
        user_input = input("用户：").strip()

        if user_input.lower() in {"exit", "quit", "q"}:
            print("程序已退出。")
            break

        if not user_input:
            print("输入不能为空。")
            continue

        final_answer = agent.run(user_input)

        print("\n===== 最终输出 =====")
        print(final_answer)
        print("-" * 60)


if __name__ == "__main__":
    main()


