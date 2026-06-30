---
title: Day 01｜AI Agent 学习环境搭建与首次 LLM API 调用
date: 2026-06-18
tags:
  - AI-Agent
  - LLM
  - Python
  - API
  - Git
  - GitHub
  - 学习复盘
status: completed
---

# Day 01｜AI Agent 学习环境搭建与首次 LLM API 调用

## 一、今天的学习目标

今天是 AI Agent 系统学习的第一天。

今天不追求直接做出完整 Agent，而是完成最基础的开发链路：

```text
建立学习仓库
→ 配置 Python 环境
→ 管理 API 配置
→ 编写 Python 调用程序
→ 成功调用大模型
→ 测试不同问题
→ 提交到 GitHub
```

今天的核心目标是：

> 使用 Python 成功调用一次真实的大模型 API，并理解当前代码与真正 Agent 之间的区别。

---

# 二、今天完成的内容

## 1. 创建 Hugging Face 账号

完成 Hugging Face 账号注册和邮箱验证。

Hugging Face 后续主要用于：

- 学习 AI Agents Course；
- 查看模型、数据集和 Spaces；
- 运行课程中的在线案例；
- 学习 Agent、RAG、LangGraph 等内容；
- 后期提交课程作业或项目。

今天暂时没有创建 Hugging Face Access Token，因为当前代码调用的是外部 OpenAI 兼容 API，还不需要 Hugging Face Token。

## 2. 创建 GitHub 学习仓库

GitHub 仓库：

```text
https://github.com/bunengshengqi/agents-learn
```

仓库用途：

1. 保存每天的代码练习；
2. 保存每天的学习笔记；
3. 保存后续完整 Agent 项目；
4. 形成求职作品集；
5. 通过 Git 提交记录证明学习过程。

## 3. 将仓库克隆到本地

执行：

```bash
git clone https://github.com/bunengshengqi/agents-learn.git
```

本地路径：

```text
~/Desktop/agents-learn
```

克隆时出现提示：

```text
您似乎克隆了一个空仓库
```

这不是错误。

原因是 GitHub 上刚创建的仓库还没有任何文件，因此本地只能获得 Git 仓库本身，没有业务代码。

## 4. 使用 Python 3.11 环境

使用已有的 Python 环境：

```text
~/Desktop/envs/py311_dev
```

激活方式：

```bash
source ~/Desktop/envs/py311_dev/bin/activate
```

激活后，终端显示：

```text
(py311_dev)
```

说明虚拟环境已经生效。

检查 Python 版本：

```bash
python --version
```

当前使用 Python 3.11，适合后续学习：

- OpenAI SDK；
- LangGraph；
- FastAPI；
- Pydantic；
- MCP；
- pytest。

## 5. 创建项目目录

当前项目结构：

```text
agents-learn/
├── README.md
├── .gitignore
├── .env
├── .env.example
├── requirements.txt
├── docs/
├── examples/
│   └── 01-llm-api/
│       ├── main.py
│       └── README.md
├── notes/
│   └── day01.md
└── tests/
```

各目录用途：

| 目录 | 用途 |
|---|---|
| `examples/` | 每天的小型代码练习 |
| `notes/` | 每日学习笔记 |
| `docs/` | 架构图、周报、面试题 |
| `tests/` | 自动化测试 |
| `projects/` | 后续完整求职项目 |

---

# 三、今天掌握的核心知识

## 1. 普通大模型调用是什么

今天编写的程序流程是：

```text
用户输入问题
→ Python 调用大模型 API
→ 模型生成答案
→ Python 打印答案
```

这属于普通的 LLM API 调用。

当前程序能够：

- 接收用户输入；
- 读取 API 配置；
- 调用模型；
- 输出自然语言回答；
- 捕获接口异常。

但它还不能自动执行外部任务。

## 2. 什么是 AI Agent

普通大模型主要负责：

```text
用户提问
→ 模型回答
```

AI Agent 在大模型基础上增加了行动能力：

```text
用户提出目标
→ 模型理解目标
→ 判断下一步
→ 选择工具
→ 调用工具
→ 获取执行结果
→ 根据结果继续决策
→ 完成任务
```

AI Agent 的关键组成部分包括：

- 大模型；
- System Prompt；
- 工具；
- 状态；
- Agent Loop；
- 执行环境；
- 终止条件；
- 错误处理；
- 人工审核。

## 3. 当前代码为什么还不是 Agent

今天的代码只有：

```text
用户输入
→ 模型回答
```

还没有：

- Tool Calling；
- Function Calling；
- 多步骤决策；
- Agent Loop；
- 状态管理；
- 对话记忆；
- 任务规划；
- 工具执行；
- 人工审核。

因此当前程序应该准确描述为：

> 一个使用 Python 调用 OpenAI 兼容接口的大模型问答程序。

它是构建 Agent 的基础，但还不是完整 Agent。

---

# 四、今天完成的三个测试

## 测试一

```text
请用三个要点解释什么是 AI Agent。
```

模型能够从以下几个方面回答：

- 自主性；
- 感知和交互；
- 目标驱动。

## 测试二

```text
AI Agent 和普通聊天机器人有什么区别？
```

模型给出的核心区别：

```text
普通聊天机器人更像“问答机”
AI Agent 更像“数字员工”
```

普通聊天机器人主要回答问题。

Agent 可以：

- 设定目标；
- 分解任务；
- 调用工具；
- 访问数据库和 API；
- 根据结果调整策略；
- 执行多步骤任务。

## 测试三

```text
为什么 AI Agent 需要调用外部工具？
```

模型说明了工具的重要性：

1. 获取实时数据；
2. 执行精确计算；
3. 访问私有数据库；
4. 与外部系统交互；
5. 保存状态和长期记忆；
6. 执行专业任务。

最关键的理解是：

> 大模型主要负责理解、推理和生成，工具负责获取真实数据和执行真实操作。

---

# 五、今天暴露出来的薄弱环节

## 薄弱点一：不理解 GitHub 仓库与本地文件的关系

### 我的疑问

> 这个仓库就是从 GitHub 上拉下来的，为什么还要填写 `.gitignore`？

### 暴露的问题

之前对以下几个概念的边界不够清晰：

- GitHub 远程仓库；
- 本地 Git 仓库；
- Git 跟踪文件；
- Git 忽略文件；
- 本地生成文件；
- 远程已有文件。

### 正确认识

`git clone` 只是把远程仓库复制到本地。

它不会自动帮项目配置：

- `.gitignore`；
- Python 环境；
- `.env`；
- 项目目录；
- 依赖文件；
- 安全规则。

`.gitignore` 的作用是告诉 Git：

> 哪些本地文件不允许进入版本控制。

即使仓库是从 GitHub 拉下来的，也仍然需要根据项目实际情况维护 `.gitignore`。

## 薄弱点二：不理解 `.gitignore` 的实际作用

### 我的疑问

> 为什么必须填写 `.gitignore`？

### 暴露的问题

之前把 `.gitignore` 理解成了一个普通配置文件，没有意识到它与密钥泄漏和垃圾文件上传直接相关。

### 正确认识

`.gitignore` 主要用于忽略：

```text
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

其中最重要的是：

```text
.env
```

因为 `.env` 中存放真实 API Key。

如果没有忽略 `.env`，执行：

```bash
git add .
git commit
git push
```

就可能把真实 API Key 上传到公开 GitHub。

## 薄弱点三：不清楚 `.env` 和 `.env.example` 的区别

### 正确认识

#### `.env`

保存真实配置：

```env
OPENAI_API_KEY=真实密钥
OPENAI_BASE_URL=真实接口地址
OPENAI_MODEL=真实模型名
```

特点：

- 只存在于本地；
- 不能上传 GitHub；
- 必须写进 `.gitignore`。

#### `.env.example`

保存配置模板：

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://your-api-domain.com/v1
OPENAI_MODEL=your-model-name
```

特点：

- 不包含真实密码；
- 可以上传 GitHub；
- 用于告诉其他开发者项目需要什么配置。

一句话区分：

> `.env` 是真实答案，`.env.example` 是填写说明。

## 薄弱点四：API Key 安全意识不足

### 实际问题

在交流过程中曾直接展示完整 API Key。

### 风险

API Key 与密码类似。

一旦泄露，其他人可能：

- 使用接口；
- 消耗余额；
- 发起恶意请求；
- 导致账号被封；
- 产生额外费用。

### 正确处理方法

如果 API Key 被完整展示，应当：

1. 立即在后台禁用旧 Key；
2. 创建新的 Key；
3. 将新 Key 只写入 `.env`；
4. 不再截图或粘贴真实 Key；
5. Git 提交前检查 `.env` 是否被忽略。

检查命令：

```bash
git check-ignore .env
```

如果输出：

```text
.env
```

说明忽略规则已经生效。

## 薄弱点五：不熟悉 API 地址、模型名和中转站之间的关系

### 正确认识

如果使用官方 API：

```text
Base URL、API Key、模型名
```

都应该按照官方文档配置。

如果使用中转站：

```text
Base URL
```

应该填写中转站地址。

模型名称也必须以中转站实际支持的模型映射为准，不能简单照搬官方名称。

一句话理解：

> API Key、Base URL 和模型名称必须属于同一套服务体系。

## 薄弱点六：对 Shell 多行输入 heredoc 不熟悉

### 实际问题

执行：

```bash
cat > notes/day01.md <<'EOF'
```

之后，终端一直出现：

```text
heredoc>
```

### 原因

这个命令表示：

> 把接下来输入的所有内容写进文件，直到遇到一行完全等于 `EOF`。

### 结束方法

正常结束：

```text
EOF
```

必须满足：

- 单独一行；
- 前后没有空格；
- 大小写一致。

强制终止：

```text
Ctrl + C
```

### 更适合当前阶段的方式

对于较长的 Markdown 内容，可以使用：

```bash
open -e notes/day01.md
```

或者：

```bash
open -e README.md
```

在文本编辑器里粘贴并保存，比在终端输入超长 heredoc 更稳。

## 薄弱点七：Git 提交流程还不熟练

### 实际问题

代码已经提交并推送后，才发现：

- `README.md` 没有填写；
- `notes/day01.md` 没有填写。

### 正确认识

Git 提交不是只能提交一次。

第一次提交代码：

```bash
git commit -m "feat: complete day one llm api practice"
```

第二次补充文档：

```bash
git commit -m "docs: complete day one notes and readme"
```

这是正常且更清晰的开发方式。

## 薄弱点八：Git 用户身份配置不规范

第一次提交时，Git 提示用户名和邮箱是根据系统自动设置的。

后续应该配置自己的 Git 用户信息：

```bash
git config --global user.name "bunengshengqi"
git config --global user.email "你的GitHub邮箱"
```

检查：

```bash
git config --global user.name
git config --global user.email
```

## 薄弱点九：容易急着执行命令，但对命令含义理解不足

今天多次出现的共同问题是：

> 可以按照命令操作，但没有完全理解命令在做什么。

后续学习中需要坚持：

1. 先知道命令解决什么问题；
2. 再执行命令；
3. 执行后观察输出；
4. 判断结果是否符合预期；
5. 最后记录到笔记。

不能只追求“命令运行成功”。

---

# 六、今天使用的重要命令

## Git 仓库克隆

```bash
git clone https://github.com/bunengshengqi/agents-learn.git
```

## 进入项目

```bash
cd ~/Desktop/agents-learn
```

## 激活 Python 环境

```bash
source ~/Desktop/envs/py311_dev/bin/activate
```

## 安装依赖

```bash
python -m pip install openai python-dotenv
```

## 保存依赖

```bash
python -m pip freeze > requirements.txt
```

## 检查 `.env` 是否被忽略

```bash
git check-ignore .env
```

## 查看 Git 状态

```bash
git status
```

## 暂存文件

```bash
git add .
```

## 提交

```bash
git commit -m "feat: 第一天的内容：完成LLM的调用"
```

## 推送

```bash
git push origin main
```

## 运行程序

```bash
python examples/01-llm-api/main.py
```

---

# 七、今天建立起来的完整链路

```text
Hugging Face 账号
        ↓
GitHub 学习仓库
        ↓
本地 Git 仓库
        ↓
Python 3.11 虚拟环境
        ↓
OpenAI Python SDK
        ↓
.env 环境变量
        ↓
大模型 API
        ↓
模型回答
        ↓
Git commit
        ↓
GitHub push
```

---

# 八、今天最重要的认知

## 认知一

Agent 不是某一个框架。

Agent 的本质是：

```text
模型
+ 工具
+ 状态
+ 循环
+ 环境反馈
+ 终止条件
```

## 认知二

今天调用成功的程序还不是 Agent。

今天只是完成了 Agent 的“大脑连接”。

后续还需要为它增加：

- 工具；
- 多轮消息；
- 状态；
- 执行循环；
- 错误处理；
- 任务终止机制。

## 认知三

写代码只是学习的一部分。

真正用于求职的项目还必须包括：

- README；
- 学习笔记；
- 自动化测试；
- 架构说明；
- 评测数据；
- Git 提交记录；
- 演示视频。

---

# 九、Day 1 自我验收

## 已完成

- [x] 注册 Hugging Face 账号
- [x] 创建 GitHub 仓库
- [x] 克隆仓库到本地
- [x] 激活 Python 3.11 环境
- [x] 创建项目目录
- [x] 配置 `.gitignore`
- [x] 创建 `.env`
- [x] 创建 `.env.example`
- [x] 安装 OpenAI SDK
- [x] 编写第一个 API 调用程序
- [x] 成功调用真实模型
- [x] 完成三个问题测试
- [x] 检查 `.env` 已被忽略
- [x] 完成 Git commit
- [x] 完成 Git push

## 还需要完善

- [ ] 配置规范的 Git 用户名和邮箱
- [ ] 完成根目录 README
- [ ] 完善 Day 1 学习笔记
- [ ] 在 GitHub 页面确认文件内容正确
- [ ] 确认没有真实 API Key 被提交

---

# 十、Day 2 学习预告

## Day 2 主题

```text
Messages、多轮对话与上下文记忆
```

Day 1 的程序每次只能处理一个独立问题。

运行结束后，它就忘记了之前的内容。

Day 2 要解决的问题是：

> 如何让模型记住前面的对话，并基于历史内容继续回答？

## Day 2 核心知识

### 1. Messages 是什么

```python
messages = [
    {
        "role": "system",
        "content": "你是一名AI Agent学习助手。"
    },
    {
        "role": "user",
        "content": "什么是AI Agent？"
    },
    {
        "role": "assistant",
        "content": "AI Agent是……"
    }
]
```

### 2. 四种常见角色

#### system

定义模型身份、规则和行为边界。

#### user

用户输入的问题或任务。

#### assistant

模型以前生成的回答。

#### tool

外部工具返回给模型的结果。

Day 2 主要学习前三种。

### 3. 多轮对话的本质

大模型本身不会自动记住上一轮。

所谓多轮对话，实际上是程序每次调用模型时，把之前的消息重新发送给模型。

例如：

```text
第一轮：
用户：我叫小明
助手：你好，小明

第二轮实际发送：
用户：我叫小明
助手：你好，小明
用户：我叫什么名字？
```

模型看到完整历史，才能回答：

```text
你叫小明。
```

## Day 2 代码目标

创建目录：

```text
examples/02-messages/
```

建议包含：

```text
examples/02-messages/
├── single_turn.py
├── multi_turn.py
└── README.md
```

Day 2 要实现：

1. 使用 `messages` 保存对话；
2. 支持连续输入问题；
3. 把用户消息加入历史；
4. 把模型回答加入历史；
5. 验证模型能够记住上一轮；
6. 输入 `exit` 后退出程序；
7. 限制对话历史长度；
8. 对比不同 System Prompt 的效果。

## Day 2 测试问题

### 测试一：记忆名字

```text
用户：我叫鲁迪。
用户：我叫什么名字？
```

预期结果：

```text
你叫鲁迪。
```

### 测试二：记忆职业

```text
用户：我在银行从事RPA开发。
用户：我的工作是什么？
```

预期结果：

```text
你在银行从事RPA开发。
```

### 测试三：System Prompt 对比

System Prompt A：

```text
你是一名严谨的技术老师。
```

System Prompt B：

```text
你是一名幽默的脱口秀演员。
```

对两个模型询问同一个问题：

```text
什么是AI Agent？
```

观察回答风格的差异。

## Day 2 重点理解的问题

1. `system`、`user`、`assistant` 分别是什么？
2. 大模型为什么能记住上一轮对话？
3. 模型是真的长期记住了吗？
4. 为什么每轮都要重新发送历史消息？
5. 对话历史太长会有什么问题？
6. 如何限制上下文长度？
7. System Prompt 对模型有什么影响？
8. 多轮对话与 Agent 状态有什么关系？

## Day 2 预计薄弱点

- 不要只复制代码，要看懂 `messages.append()`；
- 理解列表中每一条消息为什么存在；
- 区分“模型记忆”和“程序保存历史”；
- 理解为什么重启程序后记忆会丢失；
- 不要把所有对话无限追加；
- 注意 API 调用次数和 Token 消耗；
- 每次修改代码后都要自己测试。

## 明天的执行顺序

```text
复习 Day 1
→ 学习 message roles
→ 创建 examples/02-messages
→ 编写单轮对话
→ 改造成多轮对话
→ 测试上下文记忆
→ 测试不同 System Prompt
→ 记录问题
→ 提交 GitHub
```

预计时间：

| 内容 | 时间 |
|---|---:|
| 理论学习 | 30分钟 |
| 编写代码 | 60分钟 |
| 测试与调试 | 30分钟 |
| 笔记复盘 | 20分钟 |
| Git提交 | 10分钟 |

---

# 十一、Day 1 总结

今天最重要的成果不是调用了一次模型，而是第一次建立了完整的 AI 应用开发流程：

```text
环境
→ 配置
→ 代码
→ API
→ 测试
→ Git
→ 文档
```

今天最明显的薄弱点集中在：

```text
Git基础
Shell命令
配置文件
密钥安全
API配置
开发流程理解
```

这些问题并不妨碍继续学习 Agent，但后续需要通过每天的实操逐步补齐。

Day 2 将从“单次模型回答”升级到“带有历史记录的多轮对话”，这是进入 Tool Calling 和 Agent Loop 之前必须掌握的一步。

---

# 十二、Obsidian 双向链接建议

建议在 Obsidian 中建立这些概念链接：

```text
[[AI Agent]]
[[LLM API]]
[[Git基础]]
[[环境变量]]
[[API Key安全]]
[[多轮对话]]
[[System Prompt]]
[[Tool Calling]]
```
