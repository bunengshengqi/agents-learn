# 本模块保存与 Transport 无关的 JSON-RPC 协议处理和三类 MCP-like 能力。
# 它只实现 Day39 所需的教学子集，真实 MCP 项目应使用官方 SDK 或 FastMCP。
from __future__ import annotations  # 推迟类型注解求值，减少运行时耦合。
#
# 导入 Any，用于表达 JSON 中可能出现的任意值。
from typing import Any  # JSON 的字段值可能是字典、列表、字符串、数字或 null。
#
#
# 声明教学 Client 与 Server 在 initialize 中使用的协议版本。
PROTOCOL_VERSION = "2025-11-25"  # 带日期的版本号体现 MCP 协议会持续演进。
#
# 定义 Server 对外公开的 Tool 元数据列表。
TOOLS = [  # tools/list 会把该列表放进 result.tools。
    {  # 列表中第一个也是唯一一个教学 Tool。
        "name": "add",  # Tool 唯一名称，模型调用时必须使用它。
        "description": "Add two numbers.",  # 描述帮助模型判断何时调用该 Tool。
        "inputSchema": {  # JSON Schema 用于描述和校验 arguments。
            "type": "object",  # Tool 参数整体必须是 JSON 对象。
            "properties": {  # properties 定义允许出现的字段。
                "a": {"type": "number"},  # 参数 a 必须是数字。
                "b": {"type": "number"},  # 参数 b 必须是数字。
            },  # 结束 properties。
            "required": ["a", "b"],  # a 和 b 都是必填字段。
            "additionalProperties": False,  # 拒绝 Schema 中未声明的额外字段。
        },  # 结束 inputSchema。
    }  # 结束 add Tool 元数据。
]  # 结束 Tool 列表。
#
# 定义 Server 对外公开的 Resource 元数据列表。
RESOURCES = [  # resources/list 会返回该列表。
    {  # 列表中唯一的教学 Resource。
        "uri": "memo://course/day39",  # URI 是 Resource 的稳定标识。
        "name": "Day 39 memo",  # 供用户和应用显示的资源名称。
        "description": "A small read-only resource for the JSON-RPC demo.",  # 解释资源内容和用途。
        "mimeType": "text/plain",  # 告诉 Client 内容是普通文本。
    }  # 结束 Resource 元数据。
]  # 结束 Resource 列表。
#
# 定义 Server 对外公开的 Prompt 元数据列表。
PROMPTS = [  # prompts/list 会返回该列表。
    {  # 列表中唯一的教学 Prompt。
        "name": "explain_concept",  # Prompt 唯一名称。
        "description": "Create an instruction for explaining a concept.",  # 说明模板用途。
        "arguments": [  # 声明实例化 Prompt 时可传入的参数。
            {  # 定义 concept 参数。
                "name": "concept",  # 参数名称。
                "description": "The concept to explain.",  # 参数语义说明。
                "required": True,  # concept 是必填参数。
            }  # 结束 concept 参数定义。
        ],  # 结束 Prompt 参数列表。
    }  # 结束 Prompt 元数据。
]  # 结束 Prompt 列表。
#
#
# 定义可安全转换为 JSON-RPC error 的业务异常。
class RpcError(Exception):  # 继承 Exception，便于在分发层统一捕获。
    # 初始化协议错误码、错误消息和可选详情。
    def __init__(  # 构造一个 RpcError 实例。
        self,  # 当前异常对象。
        code: int,  # JSON-RPC 整数错误码。
        message: str,  # 稳定且简洁的错误描述。
        data: Any | None = None,  # 可选的调试或业务详情。
    ) -> None:  # 构造函数不返回值。
        super().__init__(message)  # 初始化父类，使 str(exc) 返回 message。
        self.code = code  # 保存错误码供响应生成器读取。
        self.message = message  # 保存错误消息。
        self.data = data  # 保存可选错误详情。
#
#
# 创建成功的 JSON-RPC Response。
def _result(request_id: Any, value: Any) -> dict[str, Any]:  # id 可能是数字、字符串或 null。
    return {  # 成功响应使用 result 字段。
        "jsonrpc": "2.0",  # 声明 JSON-RPC 2.0。
        "id": request_id,  # 原样返回 Request id 以便 Client 匹配。
        "result": value,  # 放入具体 MCP-like 方法结果。
    }  # 返回完整成功响应。
#
#
# 创建失败的 JSON-RPC Response。
def _error(  # 把错误码、消息和详情包装成标准 error 对象。
    request_id: Any,  # 与原 Request 对应的 id。
    code: int,  # JSON-RPC 或应用自定义整数错误码。
    message: str,  # 人类可读的错误描述。
    data: Any | None = None,  # 可选错误详情。
) -> dict[str, Any]:  # 返回 JSON-RPC Error Response。
    error: dict[str, Any] = {  # 先创建必需的 error 字段。
        "code": code,  # 机器可识别的错误码。
        "message": message,  # 简洁错误消息。
    }  # 结束基础 error 对象。
    # 只有调用方提供详情时才添加 data，避免无意义的 null。
    if data is not None:  # data 是 JSON-RPC error 的可选字段。
        error["data"] = data  # 加入调试或结构化业务详情。
    # 把 error 对象包装成完整 JSON-RPC Response。
    return {  # 错误响应不能同时拥有 result。
        "jsonrpc": "2.0",  # 声明 JSON-RPC 2.0。
        "id": request_id,  # 返回原 Request id。
        "error": error,  # 放入刚刚构造的错误对象。
    }  # 返回完整错误响应。
#
#
# 校验某个值是否为 JSON Object，并返回更具体的字典类型。
def _require_mapping(value: Any, label: str) -> dict[str, Any]:  # label 用于生成准确错误消息。
    # JSON Object 在 Python 中应当解析为 dict。
    if not isinstance(value, dict):  # 列表、字符串和 null 都不符合要求。
        raise RpcError(-32602, f"{label} must be an object")  # -32602 表示参数无效。
    # 类型检查通过后返回原字典。
    return value  # 调用方可安全使用 .get 等字典方法。
#
#
# 根据 method 把请求分发到具体 MCP-like 功能。
def _dispatch(method: str, params: dict[str, Any]) -> Any:  # 返回值稍后会放入 result。
    # 处理初始化请求，返回版本、能力和 Server 信息。
    if method == "initialize":  # MCP 连接进入 Operation 前必须先初始化。
        return {  # 初始化成功结果。
            "protocolVersion": PROTOCOL_VERSION,  # 教学 Server 选择的协议版本。
            "capabilities": {  # 声明 Server 支持的能力集合。
                "tools": {},  # 表示支持 Tool 能力。
                "resources": {},  # 表示支持 Resource 能力。
                "prompts": {},  # 表示支持 Prompt 能力。
            },  # 结束 capabilities。
            "serverInfo": {  # 提供 Server 实现名称和版本。
                "name": "day39-teaching-server",  # Server 名称。
                "version": "1.0.0",  # Server 实现版本。
            },  # 结束 serverInfo。
        }  # 返回 initialize result。
#
    # 处理连接存活检查。
    if method == "ping":  # ping 不需要业务参数。
        return {}  # 空对象表示 Server 正常响应。
#
    # 处理 Tool 能力发现。
    if method == "tools/list":  # Client 请求 Tool 元数据列表。
        return {"tools": TOOLS}  # 返回名称、描述和输入 Schema。
#
    # 处理具体 Tool 调用。
    if method == "tools/call":  # Client 请求执行某个 Tool。
        name = params.get("name")  # 读取目标 Tool 名称。
        arguments = _require_mapping(params.get("arguments", {}), "arguments")  # 校验参数对象。
        # 教学 Server 只实现 add，因此拒绝其他名称。
        if name != "add":  # Tool 名称必须与 tools/list 暴露的名称一致。
            raise RpcError(-32602, f"unknown tool: {name!r}")  # 返回清晰的无效参数错误。
        # 从 arguments 读取两个加数。
        a = arguments.get("a")  # 缺少字段时得到 None。
        b = arguments.get("b")  # 缺少字段时得到 None。
        # 校验 a 是数字，同时排除 Python 中属于 int 子类的 bool。
        if not isinstance(a, (int, float)) or isinstance(a, bool):  # True 不应被当作数字 1。
            raise RpcError(-32602, "a must be a number")  # 明确指出字段 a 错误。
        # 对 b 做相同数字校验。
        if not isinstance(b, (int, float)) or isinstance(b, bool):  # False 不应被当作数字 0。
            raise RpcError(-32602, "b must be a number")  # 明确指出字段 b 错误。
        # 执行 Tool 的真实计算逻辑。
        total = a + b  # 把两个经过校验的数字相加。
        # 同时返回文本结果和结构化结果，展示两种消费方式。
        return {  # tools/call 的教学结果对象。
            "content": [  # content 适合模型和通用 Client 展示。
                {"type": "text", "text": str(total)}  # 把数字转为文本内容块。
            ],  # 结束 content 列表。
            "structuredContent": {"sum": total},  # 结构化字段便于程序直接读取。
            "isError": False,  # 表示 Tool 业务执行成功。
        }  # 返回 Tool 执行结果。
#
    # 处理 Resource 能力发现。
    if method == "resources/list":  # Client 请求可发现的 Resource 元数据。
        return {"resources": RESOURCES}  # 返回 URI、名称、描述和 MIME Type。
#
    # 处理按 URI 读取 Resource。
    if method == "resources/read":  # Client 请求具体资源内容。
        uri = params.get("uri")  # 读取目标 Resource URI。
        # 教学 Server 只允许读取预先公开的 URI。
        if uri != "memo://course/day39":  # 未知 URI 不应访问任意本地文件。
            raise RpcError(-32602, f"unknown resource: {uri!r}")  # 返回无效 URI 错误。
        # 返回包含 URI、MIME Type 和文本的 Resource 内容。
        return {  # resources/read result。
            "contents": [  # MCP 结果可以包含一个或多个内容项。
                {  # 唯一的教学文本资源。
                    "uri": uri,  # 原样返回已读取的 Resource URI。
                    "mimeType": "text/plain",  # 声明内容类型。
                    "text": "JSON-RPC defines message shape; transport moves bytes.",  # 资源正文。
                }  # 结束 Resource 内容项。
            ]  # 结束 contents 列表。
        }  # 返回 Resource 读取结果。
#
    # 处理 Prompt 能力发现。
    if method == "prompts/list":  # Client 请求 Prompt 元数据列表。
        return {"prompts": PROMPTS}  # 返回名称、描述和参数定义。
#
    # 处理 Prompt 模板实例化。
    if method == "prompts/get":  # Client 按名称和参数获取具体消息。
        # 教学 Server 只实现 explain_concept 模板。
        if params.get("name") != "explain_concept":  # 拒绝未知 Prompt 名称。
            raise RpcError(-32602, f"unknown prompt: {params.get('name')!r}")  # 返回无效参数错误。
        # 读取并校验 Prompt arguments 对象。
        arguments = _require_mapping(params.get("arguments", {}), "arguments")  # 保证可使用 .get。
        # 读取要解释的概念文本。
        concept = arguments.get("concept")  # 缺少参数时得到 None。
        # 要求 concept 是去除空白后仍有内容的字符串。
        if not isinstance(concept, str) or not concept.strip():  # 排除 null、数字和空字符串。
            raise RpcError(-32602, "concept must be a non-empty string")  # 返回字段级错误。
        # 返回实例化后的 Prompt 描述和消息列表。
        return {  # prompts/get result。
            "description": "Explain one concept with an analogy and an example.",  # 模板用途。
            "messages": [  # Prompt 被表示为可加入对话的消息。
                {  # 唯一的 user 消息。
                    "role": "user",  # 指定消息角色。
                    "content": {  # 使用类型化内容块。
                        "type": "text",  # 内容是普通文本。
                        "text": (  # 用括号拼接较长的模板字符串。
                            f"Explain {concept.strip()} in plain language, then give "  # 插入已清理概念。
                            "one analogy and one concrete example."  # 补充输出要求。
                        ),  # 结束模板字符串。
                    },  # 结束 content。
                }  # 结束 Prompt 消息。
            ],  # 结束 messages 列表。
        }  # 返回实例化 Prompt。
#
    # 所有已实现 method 都未匹配时返回标准 Method not found。
    raise RpcError(-32601, f"method not found: {method}")  # -32601 是 JSON-RPC 标准错误码。
#
#
# 处理一个已经由 Transport 解析出来的 JSON-RPC 消息。
def handle_message(message: Any) -> dict[str, Any] | None:  # Request 返回响应，Notification 返回 None。
    # JSON-RPC 消息顶层必须是对象；教学 Demo 不实现 Batch 数组。
    if not isinstance(message, dict):  # 字符串、数字、列表等都属于无效请求。
        return _error(None, -32600, "invalid request: expected an object")  # 返回标准 Invalid Request。
#
    # 读取 id；Notification 没有该字段，因此 get 会得到 None。
    request_id = message.get("id")  # 用于后续成功或错误响应。
    # 必须用字段是否存在判断 Notification，不能只判断 id 值是否为 None。
    is_notification = "id" not in message  # 没有 id 的消息不期待 Response。
#
    # 同时校验 JSON-RPC 版本和 method 类型。
    if message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):  # 基础信封无效。
        # 无效 Notification 仍不能响应；无效 Request 返回 -32600。
        return None if is_notification else _error(request_id, -32600, "invalid request")  # 条件返回。
#
    # 没有 params 时按空对象处理。
    params = message.get("params", {})  # 教学方法全部使用对象形式参数。
    # 本 Demo 不支持位置参数数组，要求 params 是对象。
    if not isinstance(params, dict):  # 数组、字符串和 null 都不被教学方法接受。
        # Notification 不响应，Request 返回 Invalid params。
        return None if is_notification else _error(  # 根据消息类型决定是否生成响应。
            request_id,  # 关联原 Request id。
            -32602,  # JSON-RPC 标准 Invalid params 错误码。
            "params must be an object",  # 清晰说明期望的参数形态。
        )  # 返回参数错误响应。
#
    # 统一捕获协议可预期错误和意外实现错误。
    try:  # 尝试分发并执行 method。
        value = _dispatch(message["method"], params)  # 得到将放入 result 的方法结果。
        # Notification 执行后不响应；Request 包装为成功响应。
        return None if is_notification else _result(request_id, value)  # 遵守 JSON-RPC 响应规则。
    # 把主动抛出的 RpcError 转成结构化 JSON-RPC error。
    except RpcError as exc:  # 捕获方法不存在、参数错误等预期失败。
        # Notification 不响应；Request 返回异常携带的 code、message 和 data。
        return None if is_notification else _error(  # 根据消息类型分流。
            request_id,  # 关联原 Request。
            exc.code,  # 使用 RpcError 中保存的错误码。
            exc.message,  # 使用稳定错误消息。
            exc.data,  # 透传可选详情。
        )  # 返回协议错误响应。
    # 最后一层防御避免未预料异常直接导致 Server 崩溃。
    except Exception as exc:  # pragma: no cover - 教学边界中的兜底处理。
        # 不向 Client 泄露完整堆栈，只返回异常类型作为教学详情。
        return None if is_notification else _error(  # Notification 仍遵守不响应原则。
            request_id,  # 关联原 Request。
            -32603,  # JSON-RPC 标准 Internal error 错误码。
            "internal error",  # 对外使用稳定且有限的信息。
            type(exc).__name__,  # 只附带异常类型，不暴露敏感内部数据。
        )  # 返回内部错误响应。
