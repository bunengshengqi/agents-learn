# 本脚本把 JSON-RPC Request 放进 HTTP POST Body，演示 HTTP Transport。
from __future__ import annotations  # 推迟类型注解求值。
#
# 导入命令行解析模块，用于允许用户覆盖 Server URL。
import argparse  # 提供 ArgumentParser。
# 导入 JSON 模块，用于序列化请求和解析响应。
import json  # 负责 Python 对象与 JSON 文本互转。
# 导入 Any，表示 JSON 字段可以包含多种值类型。
from typing import Any  # 用于字典类型注解。
# 导入标准库 HTTP Client 工具。
from urllib.request import Request, urlopen  # Request 构造请求，urlopen 发送请求。
#
#
# 定义发送一个 JSON-RPC HTTP 请求的辅助函数。
def send_request(  # 封装消息构造、HTTP 发送、响应解析和展示。
    url: str,  # MCP-like HTTP endpoint 地址。
    request_id: int,  # 用于关联请求与响应的 JSON-RPC id。
    method: str,  # 要调用的方法名。
    params: dict[str, Any] | None = None,  # 可选的方法参数。
) -> dict[str, Any]:  # 返回解析后的 JSON-RPC Response。
    # 构造 JSON-RPC Request 的基础字段。
    message: dict[str, Any] = {  # 该字典稍后会成为 HTTP Body。
        "jsonrpc": "2.0",  # 固定声明 JSON-RPC 2.0。
        "id": request_id,  # Server 响应必须返回相同 id。
        "method": method,  # 指定要执行的远程方法。
    }  # 结束基础 Request。
    # 仅在调用方传入参数时添加 params。
    if params is not None:  # 无参数方法可以省略 params 字段。
        message["params"] = params  # 写入结构化参数对象。
#
    # 把 JSON-RPC 对象编码为 UTF-8 HTTP Body。
    payload = json.dumps(message, ensure_ascii=False).encode("utf-8")  # 中文无需转义。
    # 输出消息载体和方向。
    print("\nCLIENT -> HTTP POST body")  # 说明下面打印的是请求体。
    # 把 bytes 解码回来，只用于人类查看。
    print(payload.decode("utf-8"))  # 展示 Transport 内部承载的 JSON-RPC 文本。
    # 创建 HTTP POST Request。
    request = Request(  # urllib 使用该对象保存 URL、Body、Header 和方法。
        url,  # 请求目标 endpoint。
        data=payload,  # JSON-RPC 消息成为 HTTP Body。
        headers={"Content-Type": "application/json"},  # 声明请求体格式。
        method="POST",  # 教学 Server 只接受 POST /mcp。
    )  # 完成 HTTP Request 构造。
    # 发送请求并设置五秒超时，避免 Server 不可用时无限等待。
    with urlopen(request, timeout=5) as response:  # noqa: S310 - 只访问用户指定的教学地址。
        result = json.loads(response.read())  # 读取 HTTP Body 并解析 JSON-RPC Response。
    # 输出响应载体和方向。
    print("SERVER -> HTTP response body")  # 说明下面打印的是响应体。
    # 用缩进格式显示 JSON-RPC Response。
    print(json.dumps(result, ensure_ascii=False, indent=2))  # 便于对照 id 与 result。
    # 返回响应，便于测试或上层代码继续处理。
    return result  # 结束本次同步 HTTP 调用。
#
#
# 定义 HTTP Client 演示入口。
def main() -> None:  # 解析 URL 并依次发送工具发现和工具调用请求。
    # 创建命令行参数解析器。
    parser = argparse.ArgumentParser()  # 自动提供 --help。
    # 允许通过 --url 修改教学 Server 地址。
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp")  # 默认只访问本机。
    # 解析用户输入的命令行参数。
    args = parser.parse_args()  # args.url 保存最终 endpoint。
#
    # 发送 tools/list，观察 JSON-RPC 消息在 HTTP Body 中的样子。
    send_request(args.url, 1, "tools/list")  # 请求 id 为 1。
    # 发送 tools/call，验证 HTTP Transport 复用同一协议逻辑。
    send_request(  # 开始构造 add Tool 调用。
        args.url,  # 使用命令行选择的 endpoint。
        2,  # 请求 id 为 2。
        "tools/call",  # 调用 Server 暴露的 Tool。
        {"name": "add", "arguments": {"a": 7, "b": 5}},  # 预期计算结果为 12。
    )  # 完成第二次 HTTP JSON-RPC 请求。
#
#
# 只有直接执行本文件时才运行 Client。
if __name__ == "__main__":  # 作为模块导入时不发送网络请求。
    main()  # 进入 HTTP Client 演示流程。
