"""
Day12: tools.py

这个文件集中展示 smolagents 创建工具的两种方式：

1. 使用 @tool 装饰器创建简单函数工具。
2. 继承 Tool 类创建结构更完整的复杂工具。

工具写得越清楚，Agent 越容易正确调用。
"""

from __future__ import annotations  # 允许类型注解延迟解析，保持代码兼容性。

from smolagents import Tool, tool  # Tool 用于类工具，tool 装饰器用于函数工具。


@tool  # 把普通 Python 函数包装成 smolagents 可调用工具。
def get_restaurant_rating(restaurant_name: str) -> float:
    """
    查询餐厅评分。

    Args:
        restaurant_name: 餐厅名称，比如海底捞、肯德基、星巴克。
    """
    ratings = {  # 用一个本地字典模拟餐厅评分数据库。
        "海底捞": 4.8,  # 海底捞的模拟评分。
        "肯德基": 4.2,  # 肯德基的模拟评分。
        "星巴克": 4.5,  # 星巴克的模拟评分。
        "苏州面馆": 4.6,  # 苏州面馆的模拟评分。
        "轻食实验室": 4.7,  # 轻食实验室的模拟评分。
    }  # 餐厅评分字典结束。
    return ratings.get(restaurant_name, 0.0)  # 找到餐厅就返回评分，找不到就返回 0.0。


@tool  # 把性价比计算函数注册成 Agent 工具。
def calculate_service_score(rating: float, price_per_person: float) -> float:
    """
    根据评分和人均价格计算服务性价比分数。

    Args:
        rating: 餐厅评分，通常是 0 到 5 分。
        price_per_person: 人均价格，单位为元。
    """
    if price_per_person <= 0:  # 防止人均价格为 0 或负数时出现除法错误。
        return 0.0  # 无效价格直接返回 0 分。

    return round(rating * 100 / price_per_person, 2)  # 用评分和价格计算性价比，并保留两位小数。


@tool  # 把关键词风险判断函数注册成 Agent 工具。
def judge_keyword_risk(text: str) -> str:
    """
    判断一段文本中是否包含简单风险关键词。

    Args:
        text: 需要检查的文本，比如商品标题、广告文案或客服话术。
    """
    risk_keywords = ["绝对", "稳赚", "包过", "最低价", "第一"]  # 定义一组简单风险关键词。
    hits = [keyword for keyword in risk_keywords if keyword in text]  # 找出文案中命中的风险词。

    if not hits:  # 如果没有命中任何风险词。
        return "低风险：未发现明显风险关键词。"  # 返回低风险说明。

    return f"较高风险：发现风险关键词 {', '.join(hits)}。"  # 返回命中的风险关键词。


class PartyThemeTool(Tool):  # 继承 Tool 类，创建一个结构更完整的类工具。
    """
    使用 Tool 类创建的复杂工具示例。

    类工具把 name、description、inputs、output_type 和 forward 分开写，
    适合更复杂、更正式、更容易复用的工具。
    """

    name = "party_theme_generator"  # 工具名称，Agent 会通过这个名字调用工具。
    description = "根据活动类型生成一个中文派对主题方案。"  # 工具描述，帮助 LLM 判断何时使用它。
    inputs = {  # 定义工具的输入参数 schema。
        "category": {  # category 是这个工具需要的输入参数名。
            "type": "string",  # category 参数的类型是字符串。
            "description": "活动类型，比如 classic heroes、villain masquerade、futuristic city。",  # 参数说明。
        }  # category 参数定义结束。
    }  # inputs 定义结束。
    output_type = "string"  # 声明工具输出类型是字符串。

    def forward(self, category: str) -> str:
        """根据活动类型返回派对主题。"""
        themes = {  # 用字典模拟不同活动类型对应的派对方案。
            "classic heroes": "经典英雄之夜：嘉宾选择自己喜欢的英雄形象，并搭配主题饮品和互动游戏。",  # 经典英雄主题。
            "villain masquerade": "反派假面舞会：用神秘面具、暗色灯光和推理游戏打造沉浸式派对。",  # 反派假面主题。
            "futuristic city": "未来城市派对：使用霓虹灯、电子音乐和赛博风装饰营造科技感。",  # 未来城市主题。
        }  # 派对主题字典结束。
        return themes.get(  # 按用户输入的 category 查找主题。
            category.lower(),  # 转成小写，降低大小写不一致导致的匹配失败。
            "暂时没有这个类型的主题。可以试试 classic heroes、villain masquerade 或 futuristic city。",  # 默认兜底回复。
        )  # 返回匹配到的主题或兜底回复。


class ProductTitleOptimizerTool(Tool):  # 继承 Tool 类，创建商品标题优化工具。
    """
    更贴近个人项目的 Tool 类示例：优化商品标题。

    这个工具模拟“闲鱼 Agent”里的标题生成能力。
    """

    name = "product_title_optimizer"  # 工具名称，Agent 会用它来调用标题优化能力。
    description = "根据商品名称、卖点和目标人群生成更适合二手平台的中文标题。"  # 工具用途描述。
    inputs = {  # 定义工具需要的三个输入参数。
        "product_name": {  # 商品名称参数。
            "type": "string",  # 商品名称是字符串。
            "description": "商品名称，比如 iPad Air、机械键盘、露营灯。",  # 商品名称的说明。
        },  # product_name 参数定义结束。
        "selling_point": {  # 核心卖点参数。
            "type": "string",  # 核心卖点是字符串。
            "description": "核心卖点，比如几乎全新、配件齐全、适合学生。",  # 卖点参数说明。
        },  # selling_point 参数定义结束。
        "audience": {  # 目标人群参数。
            "type": "string",  # 目标人群是字符串。
            "description": "目标人群，比如学生、办公族、露营新手。",  # 目标人群参数说明。
        },  # audience 参数定义结束。
    }  # inputs 定义结束。
    output_type = "string"  # 声明工具输出为字符串。

    def forward(self, product_name: str, selling_point: str, audience: str) -> str:
        """生成一个结构化商品标题。"""
        return f"{product_name}｜{selling_point}｜适合{audience}｜实拍可验"  # 拼出适合二手平台的标题。


def get_decorator_tools() -> list:
    """
    返回通过 @tool 装饰器创建的简单工具。
    """
    return [  # 返回函数工具列表。
        get_restaurant_rating,  # 餐厅评分查询工具。
        calculate_service_score,  # 服务性价比计算工具。
        judge_keyword_risk,  # 关键词风险判断工具。
    ]  # 函数工具列表结束。


def get_class_tools() -> list:
    """
    返回通过 Tool 类创建的复杂工具。
    """
    return [  # 返回类工具实例列表。
        PartyThemeTool(),  # 派对主题生成工具实例。
        ProductTitleOptimizerTool(),  # 商品标题优化工具实例。
    ]  # 类工具列表结束。


def get_all_tools() -> list:
    """
    统一返回 Day12 的全部自定义工具。
    """
    return [*get_decorator_tools(), *get_class_tools()]  # 合并函数工具和类工具，形成完整工具菜单。
