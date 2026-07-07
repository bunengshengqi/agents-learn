# Day26 Agentic RAG Invitees

这组代码配套 `notes/Day26-Agentic-RAG宾客信息检索工具.md`。

第 26 天重点是理解这条链路：

```text
Dataset -> Document -> Retriever -> Tool -> Agent
```

## 运行方式

这些脚本只使用 Python 标准库，不需要 API Key。

```bash
python examples/26-agentic-rag-invitees/01_load_and_preprocess_invitees.py
python examples/26-agentic-rag-invitees/02_guest_info_retriever_tool.py
python examples/26-agentic-rag-invitees/03_alfred_invitee_agent.py
python examples/26-agentic-rag-invitees/04_pipeline_map.py
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `01_load_and_preprocess_invitees.py` | 加载本地宾客数据，并转换成 Document |
| `02_guest_info_retriever_tool.py` | 创建一个简单关键词检索工具 |
| `03_alfred_invitee_agent.py` | 模拟 Alfred 调用宾客检索工具回答问题 |
| `04_pipeline_map.py` | 输出流程图 |
| `data/invitees.json` | 本地复刻课程数据集的 3 条宾客记录 |

## 说明

你要求“每一行代码都需要加注释”，所以 Python 文件里每一行代码都加了行内说明。
