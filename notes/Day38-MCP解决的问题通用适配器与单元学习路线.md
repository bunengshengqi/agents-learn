---
title: Day38 - MCP 解决的问题、通用适配器与单元学习路线
date: 2026-07-16
tags:
  - AI-Agent
  - Context-Engineering
  - MCP
  - Model-Context-Protocol
  - Agent-Skills
  - Slack
  - FastMCP
  - Gradio
  - HuggingFace-Spaces
  - HuggingFace-Context-Course
---

# 第38天：MCP 解决的问题、通用适配器与单元学习路线

> [!abstract] 本章定位
> 第32—37天学习了 Agent Skills：如何把稳定的知识、流程和资源交给 Agent。第38天进入 Hugging Face Context Course Unit 2，开始学习 MCP。今天先不钻进 JSON-RPC、传输协议和代码实现，而是回答三个基础问题：为什么需要 MCP、MCP 为什么被称为通用适配器，以及它与 Skills 到底是什么关系。

## 0. 学习资料

- 在线教材：[Introduction to Model Context Protocol](https://huggingface.co/learn/context-course/unit2/introduction)
- GitHub 原文：[introduction.mdx](https://github.com/huggingface/context-course/blob/main/units/en/unit2/introduction.mdx)
- MCP 官方介绍：[What is the Model Context Protocol?](https://modelcontextprotocol.io/docs/getting-started/intro)
- Slack 官方介绍：[What is Slack?](https://slack.com/help/articles/115004071768-What-is-Slack)

---

## 1. 本章一句话总结

```text
Skills 主要告诉 Agent“应该怎样做”，
MCP 主要给 Agent“连接外部系统并实际去做”的标准接口。
```

更完整地说：

```text
MCP 是连接 AI 应用与外部数据、工具和服务的开放标准。

它把原来“每个 Agent 分别适配每个外部系统”的做法，
变成“外部能力实现一次 MCP Server，兼容的 Agent 通过 MCP Client 复用”。
```

MCP 官方常用 USB-C 来类比：

```text
USB-C 统一了电子设备的连接方式；
MCP 统一了 AI 应用连接外部系统的方式。
```

---

## 2. MCP 是为了解决什么问题的？

MCP 的全称是：

```text
Model Context Protocol
模型上下文协议
```

它是一套开放标准，用于让 AI 应用以统一方式连接：

- 本地文件；
- 数据库；
- 搜索引擎；
- 企业 API；
- Slack、Jira、Notion 等软件服务；
- 预先定义的工作流和提示模板。

### 2.1 问题一：模型本身不知道实时外部信息

大模型只能根据当前上下文和训练中学到的知识生成内容。它天然不知道：

```text
公司数据库里今天新增了什么订单；
Slack 频道刚刚发了什么消息；
Jira 中哪些任务已经逾期；
用户本地文件夹里有哪些文件；
某个内部 API 当前返回什么数据。
```

这些都属于运行时的动态上下文，必须在执行任务时从外部系统读取。

### 2.2 问题二：模型本身不能直接在外部系统中行动

模型可以生成“请发送通知”这句话，但仅靠生成文本，并不会真的：

- 给 Slack 频道发送消息；
- 创建 Jira 工单；
- 查询数据库；
- 修改日历；
- 调用支付或审批 API。

要完成真实动作，Agent 必须获得受控的外部工具。

### 2.3 问题三：传统集成会产生 M×N 问题

假设有 3 个 Agent：

```text
Claude Desktop
VS Code 中的代码 Agent
公司内部客服 Agent
```

又有 5 个外部系统：

```text
本地文件
公司数据库
Slack
Jira
知识库
```

如果没有统一协议，每个 Agent 都要分别适配每个外部系统：

```text
3 个 Agent × 5 个外部系统 = 15 套定制集成
```

增加一个 Agent，就要再写 5 套集成；增加一个外部系统，就要为 3 个 Agent 分别适配。

这就是课程所说的 **M×N Problem**：

```text
N 个 AI 应用 × M 个外部系统
= N×M 个潜在的定制连接
```

### 2.4 MCP 的解决方式

MCP 把双方约定到同一套协议上：

```text
AI 应用实现 MCP Client
外部能力实现 MCP Server
双方通过 MCP 协议通信
```

于是，Slack 集成不必分别为每个 Agent 重写。开发者可以实现一个 Slack MCP Server，再由不同的 MCP 兼容客户端连接。

> [!important] 准确理解
> MCP 不是让集成代码凭空消失。外部系统仍然需要有人封装成 MCP Server，AI 应用也需要实现 MCP Client。MCP 真正减少的是每一对系统之间互不兼容、重复开发的专用胶水代码。

### 2.5 MCP 带来的核心价值

| 价值 | 说明 |
|---|---|
| 标准化 | 用统一协议描述和调用外部能力 |
| 复用 | 一个 MCP Server 可以被多个兼容客户端使用 |
| 解耦 | Agent 不必理解每个外部系统的私有接入细节 |
| 动态上下文 | 在运行时读取最新文件、数据和服务结果 |
| 实际行动 | 通过工具调用在外部系统中执行操作 |
| 可发现性 | 客户端可以查询 Server 暴露了哪些能力 |
| 可组合性 | 一个 Agent 可以同时连接多个 MCP Server |

---

## 3. 什么是 Slack？

Slack 是一款面向团队和企业的协作平台，可以把它理解成：

```text
企业内部即时通信
+ 按主题组织的工作频道
+ 文件和历史消息搜索
+ 第三方应用集成
+ 自动化工作流
```

### 3.1 Slack 的几个基本概念

| 概念 | 含义 | 类比 |
|---|---|---|
| Workspace | 一个公司或团队的工作空间 | 一家公司的线上办公区 |
| Channel | 围绕团队、项目或主题建立的频道 | 群聊，但组织性和可检索性更强 |
| Direct Message | 一对一或小范围私聊 | 私信 |
| Thread | 针对某条消息展开的回复串 | 对一条消息单独讨论 |
| App / Integration | 接入 Slack 的外部应用 | 机器人、GitHub、日历等插件 |
| Slack API | 程序读取或操作 Slack 的接口 | 给开发者使用的控制入口 |

例如，一家软件公司的 Slack 中可能有：

```text
#engineering      研发讨论
#product          产品讨论
#incident-alerts  线上故障告警
#ai-agent         AI Agent 项目协作
```

### 3.2 为什么 MCP 课程会拿 Slack 举例？

因为 Slack 是典型的外部动态系统：

- 消息会不断变化；
- 需要用户登录和授权；
- 有明确的 API；
- 既可以读取数据，也可以执行动作；
- 企业 Agent 经常需要访问它。

Agent 可能需要完成：

```text
读取 #incident-alerts 最近 20 条消息；
搜索过去一周提到 database timeout 的讨论；
总结某个项目频道今天的进展；
向 #engineering 发送部署完成通知。
```

前三项主要是读取信息，最后一项会真实改变外部系统，因此需要更严格的权限和人工确认。

> [!note] 国内产品类比
> 如果没有用过 Slack，可以先把它类比成“更强调频道、搜索、开放 API 和企业软件集成的企业微信/飞书团队协作空间”。这个类比便于入门，但三者的产品功能和权限体系并不完全相同。

---

## 4. “MCP 作为通用适配器”是什么意思？

通用适配器不是指 MCP 自动认识世界上所有 API，而是指：

```text
不同外部系统被转换成统一的 MCP 能力接口，
不同 AI 应用只要理解 MCP，
就可以用相对一致的方式发现和使用这些能力。
```

### 4.1 先看没有 MCP 的情况

假设要让两个 Agent 访问 Slack：

```text
Agent A → 自己处理 Slack OAuth → 自己调用 Slack API → 自己转换返回值
Agent B → 自己处理 Slack OAuth → 自己调用 Slack API → 自己转换返回值
```

再加入 Jira 后：

```text
Agent A → 再开发一套 Jira 集成
Agent B → 再开发一套 Jira 集成
```

每个 Agent 都要知道 Slack、Jira 的 URL、鉴权、参数和错误格式，重复工作越来越多。

### 4.2 使用 MCP 后

开发者分别把 Slack 和 Jira 封装成 MCP Server：

```text
Slack API ← Slack MCP Server ← MCP Client ← Agent
Jira API  ← Jira MCP Server  ← MCP Client ← Agent
```

对 Agent 来说，它看到的是按 MCP 方式公开的能力，例如：

```text
Slack MCP Server
├── list_channels
├── search_messages
├── read_channel_history
└── post_message

Jira MCP Server
├── search_issues
├── get_issue
├── create_issue
└── update_issue
```

Agent 不需要自己拼 Slack 或 Jira 的原生 HTTP 请求，而是通过 MCP Client 调用 Server 暴露的能力。

### 4.3 一个完整例子

用户提出：

```text
查看 Slack 的 #incident-alerts 频道，
把今天没有解决的故障整理成 Jira 工单，
创建前先让我确认。
```

可能的执行链是：

```text
1. 用户向 Agent 提出任务
2. Agent 通过 MCP Client 发现 Slack Server 的工具
3. Agent 调用 read_channel_history 读取最新消息
4. Slack MCP Server 调用 Slack API 并返回结果
5. Agent 分析哪些故障尚未解决
6. Agent 生成拟创建的 Jira 工单清单
7. 用户确认
8. Agent 通过另一个 MCP Client 调用 Jira Server
9. Jira MCP Server 调用 Jira API 创建工单
10. Agent 汇报创建结果
```

在这个例子中：

| 组件 | 职责 |
|---|---|
| Agent | 理解目标、规划步骤、分析消息、决定调用什么能力 |
| MCP Client | 与 MCP Server 建立连接并交换协议消息 |
| Slack MCP Server | 把 Slack 的能力转换成 MCP 接口 |
| Jira MCP Server | 把 Jira 的能力转换成 MCP 接口 |
| Slack / Jira API | 真正读取数据或执行操作 |
| 用户确认 | 控制高影响写操作 |

### 4.4 为什么称为“通用”？

因为复用发生在两个方向：

```text
一个 MCP Client 可以连接多个 MCP Server；
一个 MCP Server 可以服务多个兼容的 MCP Client。
```

例如，同一个数据库 MCP Server 可以被：

- 桌面 AI 助手；
- 代码 Agent；
- 企业内部 Agent；
- 自动化评测程序；

共同使用，只要这些应用支持相应的 MCP 能力和传输方式。

### 4.5 类比 USB-C 时要注意什么？

USB-C 是帮助理解的类比，不代表所有 MCP Server 都可以无条件即插即用。真实接入仍可能受到以下因素影响：

- 客户端是否支持该 Server 使用的传输方式；
- Server 是否需要本地进程或远程网络连接；
- 用户是否完成身份认证；
- 客户端是否允许对应权限；
- 工具参数和返回结果是否适合当前模型；
- 写入、删除、支付等高风险操作是否需要确认。

因此更准确的说法是：

```text
MCP 提供通用连接标准，
但不自动消除认证、权限、安全、部署和业务语义问题。
```

---

## 5. 怎样理解“Skills 已经取代 MCP 的部分功能”？

课程原文表达的是：

```text
MCP 早于 Skills 出现；
后来 Skills 覆盖或吸收了 MCP 的一部分使用场景；
但 MCP 仍然是扩展 Agent 动态能力的重要工具，
尤其适合需要身份认证的场景。
```

这里的“取代部分功能”不能理解为：

```text
Skills 已经让 MCP 没用了。   ×
Skills 可以完全替代 MCP。   ×
以后所有外部连接都用 Skill。×
```

### 5.1 Skills 主要解决什么？

Skills 适合给 Agent 提供稳定、可复用的知识和工作方法，例如：

- 怎样写合格的系统提示词；
- 怎样分析一封投诉邮件；
- 团队采用什么代码风格；
- 怎样验证 Hugging Face 数据集；
- 生成报告时必须使用什么模板。

可以把它概括为：

```text
Skills 教 Agent 怎样做事。
```

### 5.2 MCP 主要解决什么？

MCP 适合把运行时的数据和操作能力提供给 Agent，例如：

- 读取当前文件；
- 查询实时数据库；
- 搜索 Slack 最新消息；
- 调用企业 API；
- 创建 Jira 工单；
- 在需要认证的服务中执行操作。

可以把它概括为：

```text
MCP 给 Agent 数据和工具，让它能够实际做事。
```

### 5.3 哪些区域发生了重叠？

MCP 不只有工具，还可以暴露 `resources` 和 `prompts`。其中一部分静态提示词、参考资料和任务说明，也可以通过 Skills 目录中的 `SKILL.md`、`references/` 和 `assets/` 交付。

例如：

```text
“团队代码审查规范”
```

如果它只是一份稳定文档，做成 Skill 通常更简单，不一定需要为了读取它而运行 MCP Server。

这就是 Skills 覆盖 MCP 部分使用场景的含义。

### 5.4 Skills 为什么没有完全替代 MCP？

因为下面这些能力仍然更符合 MCP：

| 场景 | Skills | MCP |
|---|---|---|
| 固定说明和操作流程 | 很适合 | 可以，但可能过重 |
| 静态参考资料和模板 | 很适合 | 可以暴露为 Resource |
| 查询实时数据库 | 单靠格式本身不负责 | 很适合 |
| 调用远程 API | 可指导 Agent 或附带脚本 | 提供标准服务接口 |
| 跨多个客户端复用动态工具 | 缺少统一运行时服务协议 | 核心优势 |
| 身份认证和远程服务连接 | 通常依赖额外程序 | 重要使用场景 |
| 能力发现与协议协商 | 依赖具体 Agent 的 Skill 机制 | 协议组成部分 |

> [!important] 关于 Skill 脚本的细节
> Skill 可以携带脚本，Agent 运行脚本后也能读取动态数据或执行动作。因此“Skill 只能提供静态知识”是帮助初学者区分二者的简化表达。更精确地说，Skill 规范本身主要负责打包和传递任务知识；MCP 则专门定义 AI 应用与外部服务之间的运行时通信接口。Skill 脚本能做事，不等于它自动获得了 MCP 的跨客户端协议、能力发现、连接管理和服务复用机制。

### 5.5 Skills 与 MCP 怎样一起使用？

真实项目中通常不是二选一，而是组合：

```text
Skill：告诉 Agent 怎样分析线上事故、怎样判断优先级、报告必须有哪些字段

MCP：读取 Slack 告警、查询监控数据库、创建 Jira 工单
```

也就是：

```text
Skill = 方法、规则、知识、模板
MCP   = 实时数据、外部工具、服务连接
Agent = 根据 Skill 的方法，调用 MCP 提供的能力完成任务
```

---

## 6. 本单元要学习什么？

Unit 2 的目标是从“为什么需要 MCP”逐步走到“能够构建、连接、部署并验证一个 MCP 系统”。

课程覆盖以下内容：

### 6.1 MCP 架构

将学习四个核心角色或概念：

```text
Host
Client
Server
Capability Types
```

先建立一个预览：

| 概念 | 初步理解 |
|---|---|
| Host | 承载 Agent 和 MCP Client 的 AI 应用，例如桌面助手或代码 Agent |
| Client | Host 内负责连接某一个 MCP Server 的协议组件 |
| Server | 通过 MCP 暴露数据、工具或提示的程序 |
| Capability Types | Server 对外提供的能力类别 |

Server 端最重要的三种能力类型是：

| 能力 | 作用 | 例子 |
|---|---|---|
| Tools | 让模型调用函数并执行操作 | 查询天气、发送 Slack 消息、创建工单 |
| Resources | 向应用提供可读取的上下文数据 | 文件、数据库记录、配置、文档 |
| Prompts | 提供可复用的提示模板或工作流入口 | 代码审查模板、事故分析模板 |

这些概念将在下一课详细展开，本课只需先形成整体地图。

### 6.2 使用 FastMCP 构建 MCP Server

FastMCP 是帮助开发者用 Python 更方便地创建 MCP Server 的框架。预计会学习：

- 定义 Server；
- 暴露 Tool；
- 暴露 Resource；
- 暴露 Prompt；
- 启动和测试 Server；
- 处理参数、返回值与错误。

### 6.3 使用 Gradio 构建带界面的 MCP 应用

Gradio 常用于快速创建机器学习和 AI 应用的 Web UI。本单元会把 Web 界面与 MCP Server 结合起来，使同一套能力既可以给人使用，也可以被 Agent 通过 MCP 调用。

### 6.4 把 Agent 配置成 MCP Client

只有 Server 还不够，还需要让 Agent 所在的 Host：

- 知道 Server 在哪里；
- 选择正确的传输方式；
- 启动或连接 Server；
- 发现 Server 提供的能力；
- 把工具描述交给模型；
- 执行模型选中的调用；
- 把结果返回给模型继续推理。

### 6.5 部署到 Hugging Face Spaces

本地 Server 只能在自己的电脑上运行。部署到 Hugging Face Spaces 后，可以进一步学习：

- 怎样把项目打包成可运行应用；
- 怎样管理依赖；
- 怎样提供远程访问；
- 怎样保存密钥和配置；
- 怎样验证部署后的 MCP 服务。

### 6.6 完成实践项目

最终项目会把前面的知识串起来：

```text
设计能力
→ 构建 MCP Server
→ 配置 Agent Client
→ 本地测试
→ 构建 Gradio 界面
→ 部署到 Hugging Face Spaces
→ 端到端验证
```

完成本单元后，目标不是只会背 MCP 名词，而是能够解释并实现：

```text
谁在提供能力？
谁在建立连接？
谁在决定调用？
数据怎样返回？
权限在哪里控制？
服务怎样部署和复用？
```

---

## 7. Unit 2 学习路线图

```text
为什么需要 MCP
        ↓
理解 M×N 集成问题
        ↓
理解 Host / Client / Server
        ↓
理解 Tools / Resources / Prompts
        ↓
理解 JSON-RPC 与传输方式
        ↓
使用 FastMCP 构建 Server
        ↓
配置 Agent 成为 MCP Client
        ↓
使用 Gradio 构建 Web UI
        ↓
部署到 Hugging Face Spaces
        ↓
完成端到端实践项目
```

---

## 8. 容易混淆的概念

### 8.1 MCP 不是模型

MCP 不负责生成答案。负责生成和推理的是大模型，MCP 负责连接外部能力。

### 8.2 MCP 不是某一个工具

Slack 搜索、数据库查询、文件读取是具体工具或能力；MCP 是描述、发现和调用这些能力的标准协议。

### 8.3 MCP Server 不一定是远程服务器

这里的 Server 指提供 MCP 能力的一方。它既可以是本机启动的进程，也可以是远程服务，不一定是一台独立物理服务器。

### 8.4 MCP Client 不等于聊天界面

Client 是 Host 内负责 MCP 通信的协议组件。用户看到的聊天界面通常属于 Host 的一部分。

### 8.5 有 MCP 不代表可以绕过权限

MCP 统一连接方式，但不能替代：

- 登录认证；
- 用户授权；
- 最小权限；
- 输入校验；
- 写操作确认；
- 审计日志；
- 密钥管理。

### 8.6 MCP 不会让所有 Server 自动兼容所有客户端

协议兼容只是基础，还要考虑传输、版本、认证、客户端功能支持和部署环境。

---

## 9. 课程导论没有展开，但必须补上的桥梁知识

Hugging Face 的 Introduction 主要负责说明“为什么学 MCP”，并不打算在这一页讲完所有工程问题。因此它不是内容错误，而是作为完整学习材料仍缺少若干从概念走向实践的桥梁。

### 9.1 MCP、API、SDK、Function Calling 和 Tool Calling 有什么区别？

这几个概念经常同时出现，但不在同一层。

| 概念 | 解决的问题 | 一个简单例子 |
|---|---|---|
| API | 一个具体系统允许外部程序怎样访问自己 | Slack 提供发送消息的 HTTP API |
| SDK | 用某种编程语言更方便地调用 API | Slack Python SDK |
| Function Calling / Tool Calling | 让模型用结构化数据表达“我想调用哪个函数、传什么参数” | 模型生成 `post_message(channel, text)` |
| MCP | 统一 AI 应用发现、连接和调用外部能力的协议 | Agent 通过 MCP Client 发现 Slack Server 的工具 |
| Agent | 根据目标和上下文决定是否调用、如何组合以及何时停止 | 读取告警、总结问题、经确认后创建工单 |

它们可以同时存在于一条调用链中：

```text
用户
→ Agent 推理
→ 模型生成 Tool Call
→ MCP Client 发送标准请求
→ MCP Server 执行工具
→ Slack SDK
→ Slack API
→ Slack 服务
```

因此，MCP 并不是 API 的替代品，也不是 Function Calling 的另一种叫法。

```text
API / SDK 负责怎样访问具体系统；
Function Calling 负责模型怎样表达调用意图；
MCP 负责 AI 应用与能力提供方怎样用统一协议连接和通信。
```

### 9.2 模型不会直接连接 MCP Server

课程为了简洁，经常写成“Agent 调用 MCP 工具”。真正的控制链更加完整：

```text
1. Host 把可用工具的描述提供给模型
2. 模型根据用户目标提出工具调用
3. Host 根据权限和策略决定是否允许
4. 必要时请求用户确认
5. MCP Client 把请求发送给 MCP Server
6. Server 执行函数或调用底层 API
7. Client 接收结果并交回 Host
8. Host 把结果加入模型上下文
9. 模型继续推理或生成最终回答
```

这里最重要的认识是：

```text
模型负责提出调用意图，
Host 和 Client 负责控制与通信，
Server 负责执行能力。
```

不要把模型想象成直接握着数据库密码、自己发送网络请求的程序。

### 9.3 什么时候不应该使用 MCP？

标准协议有复用价值，也会增加进程、配置、序列化、连接和调试成本。以下场景通常不必急着使用 MCP：

- 只有一个应用调用一个简单的本地 Python 函数；
- 能力不会被其他 Agent 或客户端复用；
- 只是提供一份稳定说明文档，Skill 已经足够；
- 延迟极其敏感，额外协议层没有带来实际收益；
- 团队还没有权限控制、日志和故障处理能力；
- 外部系统根本没有稳定接口，MCP Server 也无法可靠封装；
- 高风险写操作还没有人工确认与回滚机制。

可以使用下面的判断方式：

```text
需要动态数据或外部动作？
        ├── 否 → 优先考虑 Prompt / Skill / 普通上下文
        └── 是
             ↓
能力需要跨多个 Agent、项目或团队复用？
        ├── 否 → 普通函数、SDK 或项目内 Tool 可能更简单
        └── 是 → MCP 的价值开始明显
```

### 9.4 MCP 的安全边界是什么？

MCP 统一连接方式，不会自动保证 Server、工具和返回数据可信。

主要风险包括：

- 恶意或被入侵的 MCP Server；
- 工具描述与真实行为不一致；
- Resource 或工具结果中包含提示注入；
- Server 获得过大的文件、网络或数据库权限；
- 模型误调用删除、发送、支付等副作用工具；
- Token、API Key 或用户数据被记录到日志；
- 远程连接中的身份认证、会话劫持和越权访问；
- 多个工具组合后产生单个工具之外的新风险。

最低安全基线应当是：

```text
只安装可信 Server
→ 使用最小权限
→ 区分只读与写入工具
→ 对高风险操作进行明确确认
→ 校验输入和输出
→ 隔离文件系统与网络范围
→ 不把密钥交给模型上下文
→ 记录调用者、参数摘要、结果和时间
→ 为副作用操作提供幂等、撤销或补偿机制
```

MCP 官方安全文档也强调：本地 MCP Server 可能以客户端相同的系统权限运行，因此应该限制文件系统、网络和其他资源访问，并优先使用沙箱和显式授权。

参考：[MCP Security Best Practices](https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices)

### 9.5 MCP 也会带来上下文成本

接入更多 Server 不代表 Agent 一定更强。客户端通常需要把工具名称、描述和参数 Schema 提供给模型，工具结果也会进入上下文。

如果一次暴露几百个相似工具，可能出现：

- 工具描述占用大量 Token；
- 模型难以选对工具；
- 同名或近似工具发生冲突；
- 工具结果过大，挤压用户需求和关键约束；
- 延迟、调用次数和费用上升；
- 错误工具扩大攻击面。

因此，MCP 仍然需要 Context Engineering：

```text
只连接当前任务需要的 Server；
只暴露当前用户有权使用的能力；
工具名称和描述必须清晰区分；
搜索和列表结果需要分页、截断或摘要；
大数据尽量返回引用、URI 或结构化摘要；
不要把所有工具和所有结果永久塞进上下文。
```

> [!important] MCP 与 Context Engineering 的真正关系
> MCP 负责把外部上下文送到 Agent 门口；Context Engineering 仍要决定什么内容在什么时候进入模型上下文、保留多久、以什么形式呈现。连接成功不等于上下文质量合格。

### 9.6 生产系统还需要生命周期、版本和可观测性

一个演示能够调用工具，不代表 MCP 服务已经可以上线。生产实现至少还要考虑：

| 方面 | 必须回答的问题 |
|---|---|
| 生命周期 | 怎样配置、连接、发现、调用、断线重连和关闭？ |
| 超时重试 | Server 无响应时怎么办？写操作能否安全重试？ |
| Schema 演进 | 参数或返回值改变后，旧 Client 是否仍能工作？ |
| 错误语义 | 参数错误、权限错误、业务失败怎样区分？ |
| 可观测性 | 能否追踪一次用户请求经过了哪些工具？ |
| 成本 | 工具列表、返回内容、网络调用消耗多少 Token 和时间？ |
| 评测 | 工具选择正确率、调用成功率和任务完成率是多少？ |
| 降级 | MCP Server 不可用时，Agent 应停止、重试还是使用缓存？ |

建议为每次调用记录：

```text
trace_id
server_name
tool_name
调用者与权限范围
参数摘要（脱敏）
开始时间与耗时
成功或错误类型
结果大小
是否产生副作用
是否经过用户确认
```

### 9.7 Unit 2 的完整目录

Introduction 只是 Unit 2 的第一篇。完整单元还包括：

1. [Introduction to Model Context Protocol](https://huggingface.co/learn/context-course/unit2/introduction)
2. [MCP Key Concepts and Architecture](https://huggingface.co/learn/context-course/unit2/key-concepts)
3. [Building MCP Servers with Python](https://huggingface.co/learn/context-course/unit2/building-servers)
4. [Quiz 1: MCP Fundamentals](https://huggingface.co/learn/context-course/unit2/quiz1)
5. [Configuring Agents as MCP Clients](https://huggingface.co/learn/context-course/unit2/mcp-clients)
6. [Gradio MCP Integration: Web UIs + MCP Servers](https://huggingface.co/learn/context-course/unit2/gradio-mcp)
7. [Hands-On: Build and Deploy an MCP Server](https://huggingface.co/learn/context-course/unit2/hands-on)
8. [Quiz 2: MCP in Practice](https://huggingface.co/learn/context-course/unit2/quiz2)

GitHub 源码目录：[units/en/unit2](https://github.com/huggingface/context-course/tree/main/units/en/unit2)

这也解释了为什么 Introduction 看起来“缺东西”：架构、协议、传输、代码、客户端配置和部署被有意拆到后续页面。本节补充的是阅读 Introduction 时必须先建立的边界，不替代后续逐章学习。

---

## 10. 面试题

### 10.1 MCP 主要解决什么问题？

参考回答：

> MCP 主要解决 AI 应用连接外部数据和工具时缺少统一标准的问题。没有 MCP，不同 Agent 与不同文件系统、数据库和 API 之间往往需要逐对开发集成，形成 M×N 的组合爆炸。MCP 通过 Client—Server 架构和统一协议，让外部能力实现一次后可以被多个兼容 Agent 复用，同时支持运行时读取动态上下文和执行外部操作。

### 10.2 为什么说 MCP 是通用适配器？

参考回答：

> 因为 MCP 把不同外部系统的能力转换成统一的协议接口。Agent 通过 MCP Client 发现并调用 Server 暴露的 Tools、Resources 和 Prompts，而不必分别理解每个外部系统的私有接入方式。“通用”指连接标准可以复用，不代表认证、权限和业务适配会自动消失。

### 10.3 Skills 与 MCP 有什么区别？

参考回答：

> Skills 主要打包稳定的任务知识、流程、参考资料和脚本，重点是教 Agent 怎样做；MCP 主要为 AI 应用提供运行时的外部数据和操作能力，重点是让 Agent 能连接系统并实际做。二者存在部分重叠，但通常互补：Skill 提供方法，MCP 提供实时数据与工具。

### 10.4 为什么 Slack 是合适的 MCP 示例？

参考回答：

> Slack 的消息持续变化，需要身份认证，并同时提供读取和写入 API。Agent 可以通过 MCP Server 搜索频道消息、总结讨论或发送通知，因此它能很好地展示动态上下文、工具调用、权限控制和写操作确认等 MCP 关键问题。

### 10.5 MCP 是否彻底消除了 M×N 问题？

参考回答：

> MCP 通过标准化大幅降低逐对集成的成本，但不会消除全部工程工作。Server 仍需封装外部系统，Client 仍需支持协议，认证、权限、部署、版本和业务语义也仍需处理。因此更准确地说，MCP 把大量定制连接转化为围绕统一协议的可复用实现。

---

### 10.6 MCP 与普通 API、Function Calling 有什么区别？

参考回答：

> API 定义具体系统的访问方式，Function Calling 让模型结构化表达调用意图，MCP 则标准化 AI 应用与外部能力之间的发现、连接和通信。MCP Server 内部往往仍会调用 API 或 SDK，而模型的 Tool Call 则由 Host、MCP Client 和 Server 共同完成执行。

### 10.7 什么情况下不值得使用 MCP？

参考回答：

> 如果只是单个应用调用一个简单本地函数、能力没有复用需求，或者只需静态说明，普通函数、项目内 Tool 或 Skill 往往更简单。MCP 的优势主要出现在动态能力需要跨客户端复用、独立部署或统一治理时。

---

## 11. 今日检查清单

- [ ] 能用一句话解释 MCP；
- [ ] 能说明静态知识与动态上下文的区别；
- [ ] 能画出 M×N 问题；
- [ ] 能解释 MCP 怎样降低重复集成；
- [ ] 知道 Slack 是什么；
- [ ] 能用 Slack 举例解释 MCP 通用适配器；
- [ ] 能说明 Skills 与 MCP 的区别和重叠；
- [ ] 不会误以为 Skills 已完全替代 MCP；
- [ ] 知道本单元将学习 Host、Client、Server；
- [ ] 知道 Server 的三种主要能力是 Tools、Resources、Prompts；
- [ ] 知道后续会使用 FastMCP、Gradio 和 Hugging Face Spaces；
- [ ] 能说明协议标准化不等于自动解决认证和安全问题。
- [ ] 能区分 API、SDK、Function Calling、Tool Calling 与 MCP；
- [ ] 知道模型不会绕过 Host 直接连接 MCP Server；
- [ ] 能判断一个需求是否值得使用 MCP；
- [ ] 知道 MCP Server、工具描述和返回内容都可能不可信；
- [ ] 能解释工具过多为什么会造成上下文过载；
- [ ] 知道生产 MCP 服务需要日志、超时、版本、评测和降级方案。

---

## 12. 最终总结

今天最重要的不是记住某个 SDK，而是建立 MCP 的问题意识。

没有 MCP 时：

```text
每个 Agent 都要分别连接每个文件、数据库、API 和服务，
最终形成 M×N 套定制集成。
```

有 MCP 后：

```text
外部能力由 MCP Server 统一暴露，
AI 应用通过 MCP Client 连接和调用，
同一套能力可以在多个兼容 Agent 中复用。
```

Skills 与 MCP 的关系是：

```text
Skills：给方法、知识、规则和模板；
MCP：给实时数据、外部工具和服务连接；
Agent：使用 Skills 指导的方法，调用 MCP 能力完成真实任务。
```

一句话收尾：

> MCP 的核心不是“又多了一个工具框架”，而是为 AI 应用连接外部世界建立一套可以复用的共同语言。
