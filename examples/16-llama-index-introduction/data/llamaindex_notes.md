# LlamaIndex 学习资料

LlamaIndex 是一个用于构建数据增强型 LLM 应用的框架。

它擅长把私有数据接入大模型，例如 PDF、网页、数据库、Obsidian 笔记、客服知识库和产品文档。

典型 RAG 流程包括：加载数据、切分文档、建立索引、检索相关内容、把检索结果交给 LLM、生成回答。

LlamaIndex 中常见组件包括 Reader、Document、Index、Retriever、Query Engine、Tool、Agent 和 Workflow。

LlamaHub 是 LlamaIndex 的集成注册中心，可以理解为插件市场。开发者可以通过它找到模型、Reader、向量数据库、工具和 Agent 模板的安装包与 import 路径。

LlamaIndex 最适合知识库问答、文档问答、企业私有数据助手、客服资料检索和 Obsidian 笔记助手。
