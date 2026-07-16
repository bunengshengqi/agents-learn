# agents-learn

AI Agent 系统学习、代码实操与求职项目仓库。

本仓库用于记录我从大模型 API 调用开始，逐步学习 Tool Calling、Agent Loop、LangGraph、RAG、MCP、FastAPI、Docker、测试与评测，并最终完成可用于求职面试的企业级 Agent 项目。

---

## 一、学习目标

通过持续学习和代码实践，掌握以下内容：

* 大模型 API 调用
* System Prompt 与 Messages
* 多轮对话与上下文管理
* Structured Output
* Pydantic 数据校验
* Tool Calling
* Function Calling
* Agent Loop
* LangGraph
* RAG
* 向量检索与混合检索
* MCP
* FastAPI
* Docker
* Agent 测试与评测
* Human-in-the-loop
* Agent 安全与权限控制

最终求职方向：

* AI Agent 应用开发工程师
* 大模型应用开发工程师
* Python AI 应用开发工程师
* RAG 应用开发工程师
* AI 自动化工程师

---

## 二、学习原则

本项目采用“边学边做”的方式推进。

每天必须完成：

1. 学习一个 Agent 知识点；
2. 完成一个可以运行的代码功能；
3. 至少测试三条数据；
4. 编写当天学习笔记；
5. 至少提交一次 Git；
6. 整理一道面试题。

学习时间分配：

```text
理论学习：20%
代码实操：60%
测试评测：10%
笔记面试：10%
```

只看课程但没有代码产出，不算完成当天任务。

---

## 三、当前进度

* [x] 创建 Hugging Face 账号
* [x] 创建 GitHub 仓库
* [x] 初始化 Python 3.11 开发环境
* [x] 初始化项目目录
* [x] 配置 `.gitignore`
* [x] 配置 `.env`
* [x] 安装 OpenAI Python SDK
* [x] Day 1：完成第一次大模型 API 调用
* [ ] Day 2：Messages 与多轮对话
* [ ] Day 3：第一个 Tool
* [ ] Day 4：多个工具调用
* [ ] Day 5：手写 Agent Loop
* [ ] Day 6：异常处理、重试与测试
* [ ] Day 7：第一周总结

---

## 四、Day 1 完成内容

Day 1 完成了第一个大模型 API 调用程序。

实现功能：

* 使用 Python 调用 OpenAI 兼容接口；
* 使用 `.env` 保存 API 配置；
* 从环境变量读取 API Key；
* 从环境变量读取 Base URL；
* 从环境变量读取模型名称；
* 支持终端输入用户问题；
* 调用大模型生成回答；
* 输出模型返回结果；
* 捕获模型调用异常。

代码位置：

```text
examples/01-llm-api/main.py
```

测试问题：

1. 请用三个要点解释什么是 AI Agent。
2. AI Agent 和普通聊天机器人有什么区别？
3. 为什么 AI Agent 需要调用外部工具？

三个问题均成功获得模型回答。

---

## 五、当前程序执行流程

当前程序的执行流程：

```text
用户输入问题
→ Python 读取环境变量
→ Python 调用大模型 API
→ 模型生成回答
→ Python 输出结果
```

当前程序属于普通的大模型调用程序。

它暂时还不是完整的 Agent。

---

## 六、当前程序的局限

目前程序还不具备以下能力：

* 工具调用
* Function Calling
* 多步骤任务规划
* Agent Loop
* 状态管理
* 对话记忆
* 条件路由
* 任务中断恢复
* 人工审核
* RAG
* MCP
* Agent 评测

后续会逐步补充这些能力。

---

## 七、项目结构

```text
agents-learn/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
│
├── docs/
│   ├── architecture/
│   ├── interview/
│   └── weekly-reports/
│
├── notes/
│   ├── day01.md
│   └── ...
│
├── examples/
│   ├── 01-llm-api/
│   ├── 02-messages/
│   ├── 03-structured-output/
│   ├── 04-tool-calling/
│   ├── 05-agent-loop/
│   ├── 06-langgraph/
│   ├── 07-rag/
│   └── 08-mcp/
│
├── projects/
│   ├── bank-risk-agent/
│   └── rpa-error-agent/
│
└── tests/
```

目录说明：

* `examples/`：每日基础代码练习；
* `notes/`：每天的学习笔记；
* `docs/`：架构说明、周报和面试笔记；
* `tests/`：自动化测试；
* `projects/`：完整求职项目。

---

## 八、环境要求

推荐环境：

```text
Python 3.11
```

创建虚拟环境：

```bash
python3 -m venv .venv
```

激活虚拟环境：

Mac/Linux：

```bash
source .venv/bin/activate
```

Windows：

```bash
.venv\Scripts\activate
```

安装依赖：

```bash
python -m pip install -r requirements.txt
```

---

## 九、环境变量配置

复制配置模板：

```bash
cp .env.example .env
```

在 `.env` 中填写真实配置：

```env
OPENAI_API_KEY=你的_API_Key
OPENAI_BASE_URL=你的_API地址
OPENAI_MODEL=你的模型名称
```

`.env.example` 只保存配置格式：

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://your-api-domain.com/v1
OPENAI_MODEL=your-model-name
```

真实 API Key 只能保存在 `.env` 中。

---

## 十、运行 Day 1 示例

进入项目根目录：

```bash
cd agents-learn
```

运行：

```bash
python examples/01-llm-api/main.py
```

终端会提示：

```text
请输入你的问题：
```

输入问题后，程序会调用大模型并输出回答。

---

## 十一、安全说明

本仓库为公开仓库，必须遵守以下安全规则：

* 不上传真实 API Key；
* 不上传 `.env`；
* 不上传银行内部制度；
* 不上传客户信息；
* 不上传生产环境地址；
* 不上传数据库密码；
* 不上传服务器账号密码；
* 不上传内部接口报文；
* 所有业务数据均使用模拟数据。

`.gitignore` 中已经配置：

```gitignore
.env
.venv/
venv/
__pycache__/
*.pyc
.pytest_cache/
.DS_Store
.idea/
.vscode/
logs/
```

---

## 十二、后续学习路线

### 第一阶段：Agent 基础

```text
LLM API
→ Messages
→ Structured Output
→ Tool Calling
→ Agent Loop
```

### 第二阶段：Agent 工作流

```text
LangGraph State
→ Node
→ Edge
→ Conditional Edge
→ Checkpoint
→ Human-in-the-loop
```

### 第三阶段：RAG

```text
文档加载
→ 文档清洗
→ 文档分块
→ Embedding
→ 向量检索
→ 混合检索
→ 引用回答
→ RAG 评测
```

### 第四阶段：MCP

```text
MCP Server
→ MCP Client
→ Tools
→ Resources
→ 权限控制
```

### 第五阶段：完整项目

计划完成两个求职项目：

#### 银行企业风险分析 Agent

```text
企业信息查询
→ 历史业务查询
→ 风险记录查询
→ 制度 RAG
→ 风险分析
→ 人工审核
→ 生成报告
```

#### RPA 异常诊断 Agent

```text
读取日志
→ 异常分类
→ 检索历史案例
→ 判断恢复策略
→ 安全重试
→ 生成工单
```

---

## 十三、提交规范

Git 提交类型：

```text
feat: 新增功能
fix: 修复问题
docs: 更新文档
test: 增加测试
refactor: 重构代码
chore: 配置或维护
```

示例：

```bash
git commit -m "feat: add first llm api example"
git commit -m "docs: complete day one learning notes"
git commit -m "test: add agent loop test cases"
```

---

## 十四、学习成果目标

8 周后计划完成：

* 56 篇每日学习记录；
* 8 篇每周总结；
* 20 个以上基础代码练习；
* 2 个完整 Agent 项目；
* 80 条以上自动化测试；
* 100 条以上评测数据；
* 60 道以上面试题；
* 2 个项目演示视频；
* 2 份项目架构说明；
* 1 份大模型应用开发简历。

最终目标不是证明“看过 Agent 课程”，而是证明：

> 能够使用 Python、LangGraph、RAG、MCP、FastAPI 和 Docker，独立开发、测试并交付企业级 Agent 应用。

---

## 十五、交流与联系

如果你也在学习 AI Agent、LangGraph、RAG 或 MCP，欢迎交流。

添加微信时请备注：`GitHub + 来意`

<details>
<summary>查看微信二维码</summary>

<br>

<img src="./assets/wechat-qr.jpg" alt="微信二维码" width="180">

</details>
