
## 一、今天学习目标

今天学习 Hugging Face Agents Course 中 smolagents 的 Tools 工具章节。

今天重点不是继续学 Agent 流程，而是搞清楚：

- 工具是什么
- LLM 为什么需要工具接口描述
- 工具接口描述包含哪些关键要素
- 如何用 `@tool` 装饰器创建简单工具
- 如何用 Python 类创建复杂工具
- smolagents 默认工具箱有哪些
- 工具如何共享和导入
- 工具和我自己的项目有什么关系

---

## 二、一句话理解工具

在 smolagents 中，工具就是：

```text
LLM 可以在智能体系统中调用的函数。
```

如果没有工具，Agent 只能：

- 聊天
- 推理
- 写文本
- 写代码

如果有工具，Agent 才能：

- 查天气
- 查网页
- 读文件
- 查数据库
- 调 API
- 计算价格
- 判断风险
- 生成报告

所以可以这样理解：

```text
模型是 Agent 的大脑。
工具是 Agent 的手脚和外部能力。
```

---

## 三、LLM 调用工具需要什么？

LLM 不能凭空知道一个工具怎么用。

要让 LLM 正确调用工具，需要给它一份“工具说明书”。

这份说明书主要包含四个关键要素：

| 要素 | 含义 |
|---|---|
| 名称 | 工具的标识名称，比如 `web_search` |
| 工具描述 | 说明这个工具能做什么 |
| 输入类型及描述 | 说明工具需要哪些参数、参数类型和含义 |
| 输出类型 | 说明工具会返回什么结果 |

例如一个搜索工具：

```text
名称：web_search
工具描述：根据特定查询进行网络搜索
输入：query，字符串，需要查找的搜索关键词
输出：包含搜索结果的字符串
```

这四个东西就是给 LLM 的工具说明书。

---

## 四、工具接口描述在代码中怎么体现？

以一个天气查询工具为例：

```python
from smolagents import tool

@tool
def get_weather(city: str) -> str:
    """
    查询城市天气。

    Args:
        city: 城市名称，比如苏州、上海、北京
    """
    weather_data = {
        "苏州": "晴，28度，湿度55%",
        "上海": "小雨，24度，湿度80%",
        "北京": "晴，22度，湿度40%",
    }
    return weather_data.get(city, "暂无天气数据")
```

对应关系：

| 工具接口要素 | 代码中的体现 |
|---|---|
| 名称 | 函数名 `get_weather` |
| 工具描述 | docstring 中的 `查询城市天气` |
| 输入类型 | `city: str` |
| 输入描述 | `Args` 中对 `city` 的说明 |
| 输出类型 | `-> str` |

所以可以记住：

```text
函数名 + 类型注解 + docstring = 给 LLM 的工具说明书
```

---

## 五、工具调用管理流程

课程中的黑色流程图讲的是 Agent 调用工具的完整流程。

大致过程如下：

```text
1. System prompt 告诉 LLM 可用工具和任务
2. LLM 思考并决定调用工具
3. 框架解析 LLM 输出中的工具调用
4. 框架执行工具
5. 工具结果作为 Observation 写入 Memory
6. 下一轮 Prompt = System prompt + Memory
7. LLM 根据 Observation 决定继续调用工具或输出 final_answer
8. final_answer 被调用后，任务结束
```

例如任务是：

```text
how much is 2^0.27?
```

系统提示告诉模型：

```text
你可以使用 calculator、web_search 等工具。
```

模型可能先输出：

```text
Thought: I should use the calculator.
Action: calculator(2^0.27)
Observation: 1.2058
```

然后下一轮模型看到 Observation 后输出：

```text
Thought: I should return the result.
Action: final_answer(1.2058)
```

最终 Agent 返回：

```text
1.2058
```

这个流程和前面 Day03-Day08 学过的内容是一致的：

| 前面学的概念 | 工具流程中的对应 |
|---|---|
| Thought | LLM 的思考 |
| Action | 工具调用 |
| Observation | 工具返回结果 |
| Memory | 工具调用历史记录 |
| Final Answer | 最终答案 |

---

## 六、smolagents 创建工具的两种方式

在 smolagents 中，可以通过两种方式定义工具：

| 创建方式 | 适合场景 |
|---|---|
| `@tool` 装饰器 | 简单工具，一个函数就能完成 |
| 继承 `Tool` 类 | 复杂工具，需要配置、状态或更清晰的结构 |

一句话理解：

```text
@tool 是快捷方式。
Tool 类是正式工具类写法。
```

---

## 七、方式一：使用 `@tool` 装饰器

`@tool` 是 smolagents 提供的装饰器。

它的作用是：

```text
把一个普通 Python 函数包装成 Agent 可以调用的工具。
```

示例：餐厅评分查询工具

```python
from smolagents import tool

@tool
def get_restaurant_rating(restaurant_name: str) -> float:
    """
    查询餐厅评分。

    Args:
        restaurant_name: 餐厅名称，比如海底捞、肯德基、星巴克
    """
    ratings = {
        "海底捞": 4.8,
        "肯德基": 4.2,
        "星巴克": 4.5,
    }

    return ratings.get(restaurant_name, 0.0)
```

这个工具里包含：

| 要素 | 内容 |
|---|---|
| 名称 | `get_restaurant_rating` |
| 描述 | 查询餐厅评分 |
| 输入 | `restaurant_name: str` |
| 输入说明 | 餐厅名称 |
| 输出 | `float` |

然后可以把它交给 Agent：

```python
agent = CodeAgent(
    tools=[get_restaurant_rating],
    model=model,
)
```

---

## 八、`@tool` 工具适合什么？

适合简单工具：

- 查天气
- 查餐厅评分
- 计算折扣价格
- 查询商品价格
- 判断关键词风险
- 生成标题
- 读取一个固定文件

这种一个函数就能完成的工具，用 `@tool` 最合适。

---

## 九、方式二：通过 Python 类定义工具

如果工具比较复杂，可以继承 smolagents 的 `Tool` 类。

类工具需要定义五个核心元素：

| 元素 | 含义 |
|---|---|
| `name` | 工具名称 |
| `description` | 工具描述 |
| `inputs` | 输入参数定义 |
| `output_type` | 输出类型 |
| `forward` | 真正执行逻辑的方法 |

基本结构：

```python
from smolagents import Tool

class XxxTool(Tool):
    name = "工具名"
    description = "工具描述"

    inputs = {
        "参数名": {
            "type": "string",
            "description": "参数说明",
        }
    }

    output_type = "string"

    def forward(self, 参数名: str) -> str:
        ...
```

其中：

```text
name / description / inputs / output_type
```

是给 LLM 看的工具说明。

```text
forward
```

是真正执行工具逻辑的地方。

---

## 十、类工具示例：超级英雄派对主题工具

```python
from smolagents import Tool, CodeAgent, InferenceClientModel


class SuperheroPartyThemeTool(Tool):
    name = "superhero_party_theme_generator"
    description = """
    This tool suggests creative superhero-themed party ideas based on a category.
    It returns a unique party theme idea.
    """

    inputs = {
        "category": {
            "type": "string",
            "description": "The type of superhero party, such as classic heroes, villain masquerade, or futuristic Gotham.",
        }
    }

    output_type = "string"

    def forward(self, category: str) -> str:
        themes = {
            "classic heroes": "Justice League Gala: Guests come dressed as their favorite DC heroes with themed cocktails like The Kryptonite Punch.",
            "villain masquerade": "Gotham Rogues' Ball: A mysterious masquerade where guests dress as classic Batman villains.",
            "futuristic Gotham": "Neo-Gotham Night: A cyberpunk-style party inspired by Batman Beyond, with neon decorations and futuristic gadgets.",
        }

        return themes.get(
            category.lower(),
            "Themed party idea not found. Try classic heroes, villain masquerade, or futuristic Gotham.",
        )


party_theme_tool = SuperheroPartyThemeTool()

agent = CodeAgent(
    tools=[party_theme_tool],
    model=InferenceClientModel(),
)

result = agent.run(
    "What would be a good superhero party idea for a villain masquerade theme?"
)

print(result)
```

这段代码的流程：

```text
1. 定义 SuperheroPartyThemeTool 工具类
2. 设置工具名称 name
3. 设置工具描述 description
4. 设置输入参数 inputs
5. 设置输出类型 output_type
6. 在 forward 中写真正逻辑
7. 实例化工具 party_theme_tool
8. 创建 CodeAgent，并把工具交给它
9. 用户提问
10. Agent 判断应该调用这个工具
11. 工具执行 forward 方法
12. 返回派对主题创意
```

---

## 十一、`@tool` 和 `Tool` 类的区别

| 对比 | `@tool` 装饰器 | `Tool` 类 |
|---|---|---|
| 写法 | 函数 | 类 |
| 适合 | 简单工具 | 复杂工具 |
| 工具描述 | 从函数名、类型、docstring 解析 | 手动写 `name`、`description`、`inputs`、`output_type` |
| 执行逻辑 | 函数体 | `forward()` 方法 |
| 可维护性 | 简单直接 | 更适合复杂项目 |
| 是否方便保存状态 | 不方便 | 更方便 |

简单任务：

```python
@tool
def get_weather(city: str) -> str:
    ...
```

复杂任务：

```python
class XianyuProductAnalyzerTool(Tool):
    ...
```

---

## 十二、默认工具箱

smolagents 自带了一组预构建工具，可以直接注入到 Agent 中使用。

默认工具箱包括：

| 工具 | 作用 |
|---|---|
| `PythonInterpreterTool` | 执行 Python 代码 |
| `FinalAnswerTool` | 输出最终答案 |
| `UserInputTool` | 让 Agent 向用户请求补充输入 |
| `DuckDuckGoSearchTool` | 使用 DuckDuckGo 搜索 |
| `GoogleSearchTool` | 使用 Google 搜索 |
| `VisitWebpageTool` | 访问网页并读取内容 |

可以把默认工具箱理解成：

```text
Agent 的基础装备包。
```

---

## 十三、默认工具说明

### 1. PythonInterpreterTool

作用：

```text
让 Agent 执行 Python 代码。
```

适合：

- 数学计算
- 列表处理
- 表格处理
- 数据分析

### 2. FinalAnswerTool

作用：

```text
让 Agent 输出最终答案。
```

当 Agent 调用：

```python
final_answer(...)
```

说明任务完成。

### 3. UserInputTool

作用：

```text
当信息不够时，让 Agent 向用户追问。
```

例如用户只说：

```text
帮我订一个餐厅。
```

Agent 可以追问：

```text
请问城市、人数、预算和日期是什么？
```

### 4. DuckDuckGoSearchTool

作用：

```text
通过 DuckDuckGo 搜索公开网页信息。
```

### 5. GoogleSearchTool

作用：

```text
通过 Google 搜索信息。
```

通常需要 Google Search API 或相关配置。

### 6. VisitWebpageTool

作用：

```text
访问某个网页，并读取网页内容。
```

常见组合：

```text
先用搜索工具找到网页
再用 VisitWebpageTool 打开网页
最后让 Agent 总结网页内容
```

---

## 十四、共享与导入工具

smolagents 的工具不仅可以本地使用，还可以共享和导入。

也就是说：

```text
你写好的工具，可以分享出去。
别人写好的工具，你也可以导入来用。
```

---

## 十五、向 Hub 共享工具

如果你写了一个工具，比如：

```text
party_theme_tool
```

可以上传到 Hugging Face Hub：

```python
party_theme_tool.push_to_hub(
    "{your_username}/party_theme_tool",
    token="<YOUR_HUGGINGFACEHUB_API_TOKEN>"
)
```

这样别人就可以复用你的工具。

---

## 十六、从 Hub 导入工具

可以使用 `load_tool()` 导入别人上传的工具：

```python
from smolagents import load_tool

image_generation_tool = load_tool(
    "m-ric/text-to-image",
    trust_remote_code=True
)
```

然后交给 Agent：

```python
agent = CodeAgent(
    tools=[image_generation_tool],
    model=model,
)
```

这样 Agent 就拥有了图片生成能力。

---

## 十七、`trust_remote_code=True` 的含义

```python
trust_remote_code=True
```

意思是：

```text
我信任这个远程工具里的代码，允许它在本地运行。
```

这个参数有风险。

因为远程代码可能会：

- 读取文件
- 访问网络
- 执行危险操作
- 处理你的环境变量

所以不要随便加载陌生人的工具。

可以这样记：

```text
trust_remote_code=True = 我同意执行远程代码。
```

只有信任来源时才开启。

---

## 十八、将 Hugging Face Space 导入为工具

有些 Hugging Face Space 本来是一个小应用。

smolagents 可以把 Space 包装成 Agent 工具。

例如：

- 图片生成 Space
- 语音识别 Space
- OCR Space
- 文本转语音 Space

这意味着：

```text
别人已经做好的 AI 小应用，我可以包装成我的 Agent 工具。
```

---

## 十九、导入 LangChain 工具

LangChain 生态中已经有很多工具。

smolagents 可以导入一部分 LangChain 工具来复用。

这说明：

```text
不是所有工具都要自己写，可以复用社区已有工具。
```

---

## 二十、工具的四种来源

工具可以来自四个地方：

| 工具来源 | 说明 |
|---|---|
| 自己用 `@tool` 写 | 简单函数工具 |
| 自己继承 `Tool` 类写 | 复杂工具 |
| 使用 smolagents 默认工具箱 | 搜索、网页访问、Python 执行等 |
| 从 Hub / Space / LangChain 导入 | 复用社区已有工具 |

---

## 二十一、和我自己项目的关系

### 1. 视频转 SOP

可以设计的工具：

- 读取字幕工具
- 提取重点工具
- 总结工具
- SOP 结构化工具
- 生成脑图工具

### 2. 闲鱼 Agent

可以设计的工具：

- 选品工具
- 利润计算工具
- 标题生成工具
- 风控判断工具
- 客服话术工具
- 竞品搜索工具

### 3. 996tokens

可以设计的工具：

- 模型价格查询工具
- API 报错诊断工具
- 接口测试工具
- 模型选择建议工具
- 用户文档检索工具

### 4. 银行 RPA

可以设计的工具：

- 查询系统工具
- 下载文件工具
- 截图工具
- 异常判断工具
- 报表生成工具

### 5. Obsidian 知识库

可以设计的工具：

- 读取笔记工具
- 搜索笔记工具
- 总结笔记工具
- 生成课程索引工具

---

## 二十二、今天真正要掌握什么？

今天最重要的不是背所有工具，而是理解：

```text
Agent 的能力来自工具。
工具写得越清楚，Agent 用得越准。
```

一个好工具应该具备：

- 清楚的工具名
- 明确的工具描述
- 清晰的输入参数
- 正确的输入类型
- 明确的输出类型
- 稳定的执行逻辑

---

## 二十三、今日总结

第12天讲的是 smolagents 的工具系统。

核心内容：

```text
1. 工具是 LLM 可以调用的函数。
2. 工具需要名称、描述、输入类型及描述、输出类型。
3. 简单工具用 @tool。
4. 复杂工具用 Tool 类。
5. smolagents 有默认工具箱。
6. 工具可以上传到 Hub，也可以从 Hub、Space、LangChain 导入。
7. Agent 的真实能力，来自模型 + 工具。
```

---

## 二十四、今日金句

```text
工具不是代码里的附属品。
工具是 Agent 连接真实世界的手脚。
```

