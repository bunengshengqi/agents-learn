# Day23 LangGraph First Graph

这组代码配套 `notes/Day23-构建第一个LangGraph邮件处理工作流.md`。

第 23 天重点是把前面学到的 LangGraph 构建模块拼成第一个完整工作流：

```text
START
  -> read_email
  -> classify_email
  -> spam 分支 or legitimate 分支
  -> END
```

课程里的例子是 Alfred 邮件处理系统：

- 读取邮件
- 判断是否垃圾邮件
- 垃圾邮件直接处理
- 正常邮件起草回复
- 通知主人查看草稿

## 安装依赖

```bash
pip install -r examples/23-langgraph-first-graph/requirements.txt
```

如果你已经安装了仓库根目录的依赖，通常不需要重复安装。

## 运行顺序

先跑不需要 API Key 的规则版：

```bash
python examples/23-langgraph-first-graph/01_email_graph_rule_based.py
```

再跑可视化脚本：

```bash
python examples/23-langgraph-first-graph/03_mermaid_visualization.py
```

如果 `.env` 已经配置好 OpenAI 兼容接口，再跑 LLM 版：

```bash
python examples/23-langgraph-first-graph/02_email_graph_with_llm.py
```

## `.env` 示例

```env
OPENAI_API_KEY=你的真实key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-v4-flash
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `01_email_graph_rule_based.py` | 不调用 LLM，用规则模拟邮件分类和回复，重点看 LangGraph 流程 |
| `02_email_graph_with_llm.py` | 调用 OpenAI 兼容接口，让 LLM 做分类和回复生成 |
| `03_mermaid_visualization.py` | 输出 Mermaid 图，方便粘贴到 Obsidian |
| `requirements.txt` | Day23 示例依赖 |

## 学习建议

先看懂规则版，再看 LLM 版。两者的图结构是一样的：

```text
State 保存信息
Node 执行步骤
Router 决定分支
Edge 连接流程
END 结束工作流
```

这也是后面做内容运营 Agent、音频生成 Agent、发布助手 Agent 的基础。
