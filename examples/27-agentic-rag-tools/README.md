# Day27 Agentic RAG Tools

这组代码配套 `notes/Day27-Agentic-RAG工具集成.md`。

第 27 天实现三类工具：

- Web 搜索工具
- 天气信息工具
- Hugging Face Hub 模型统计工具

并用三种风格实现：

- smolagents
- LlamaIndex
- LangGraph

## 运行方式

这些脚本默认使用离线 mock 数据，不需要 API Key，也不需要访问外网。

```bash
python examples/27-agentic-rag-tools/01_smolagents_style_tools.py
python examples/27-agentic-rag-tools/02_llama_index_style_tools.py
python examples/27-agentic-rag-tools/03_langgraph_style_tools.py
python examples/27-agentic-rag-tools/04_compare_three_styles.py
python examples/27-agentic-rag-tools/05_tools_flow_map.py
```

## 文件说明

| 文件 | 说明 |
|---|---|
| `common_tools.py` | 离线 mock 的搜索、天气、Hub 统计函数 |
| `01_smolagents_style_tools.py` | smolagents 风格：继承 `Tool` |
| `02_llama_index_style_tools.py` | LlamaIndex 风格：`FunctionTool.from_defaults` |
| `03_langgraph_style_tools.py` | LangGraph 风格：`Tool` + 图式流程 |
| `04_compare_three_styles.py` | 对比三种风格输出 |
| `05_tools_flow_map.py` | 输出 Mermaid 流程图 |

## 说明

课程里的真实实现会使用：

- `DuckDuckGoSearchTool`
- `DuckDuckGoSearchToolSpec`
- `DuckDuckGoSearchRun`
- `huggingface_hub.list_models`

这里为了本地学习稳定，先用离线数据模拟外部 API。后续可以把 `common_tools.py` 中的函数替换为真实 API 调用。
