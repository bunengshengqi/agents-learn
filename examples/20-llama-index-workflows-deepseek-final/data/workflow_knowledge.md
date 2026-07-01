### Workflow

LlamaIndex Workflow 是事件驱动的流程编排方式。它把复杂的 RAG 或 Agent 应用拆成多个 Step，每个 Step 接收 Event，处理后再返回新的 Event。流程从 StartEvent 开始，到 StopEvent 结束。

当前练习代码使用的导入路径是：from llama_index.core.workflow import Workflow, step, Event, StartEvent, StopEvent, Context。

### Event

Event 是步骤之间传递的数据包。它不负责干活，只负责携带信息。自定义 Event 通常继承 Event，并用类型标注明确字段，例如 query、documents、retry_count。

### Step

Step 是真正执行动作的异步函数。它用 @step 装饰器标记。一个 Step 的输入事件类型和输出事件类型会告诉 Workflow 这个流程该如何连接。

### Context

Context 是一次 workflow 运行期间的共享状态。可以用 await ctx.store.set(key, value) 写入状态，用 await ctx.store.get(key) 读取状态。它适合保存 query、检索结果、重试次数、调用次数和中间日志。

### Branch

分支的本质是一个 Step 根据条件返回不同类型的 Event。例如普通问题返回 DirectAnswerEvent，需要查资料的问题返回 RAGEvent。不同 Event 会触发不同的后续 Step。

### Loop

循环的本质是某个 Step 返回一个可以再次触发前面步骤的 Event。RAG 中常见的循环是：检索资料、判断是否足够、不够就改写问题并再次检索，直到资料足够或达到最大重试次数。

### Fan-out Fan-in

Fan-out 是把一个任务拆成多个子任务同时处理，Fan-in 是把多个子任务结果汇总回来。RAG 中可以同时检索 Obsidian、PDF、代码库和数据库，再统一生成答案。

### AgentWorkflow

AgentWorkflow 是 LlamaIndex 为多智能体协作提供的工作流。普通 Workflow 更像程序员手写事件流程，AgentWorkflow 更像配置多个有职责边界的 Agent，让它们通过工具调用和任务交接完成工作。
