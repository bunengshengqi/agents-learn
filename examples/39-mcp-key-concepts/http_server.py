# 本脚本用 HTTP 搬运共享 JSON-RPC 消息，仅用于演示协议与 Transport 分离。
# 它不是完整 Streamable HTTP：未实现 Session、SSE、认证和完整安全要求。
from __future__ import annotations  # 推迟类型注解求值。
#
# 导入命令行解析模块，用于配置监听地址和端口。
import argparse  # 提供 ArgumentParser。
# 导入标准库 HTTP Server 类。
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer  # 分别处理请求和监听连接。
# 导入 JSON 模块，用于解析 HTTP Body 和生成 Response Body。
import json  # 负责 JSON 文本与 Python 对象互转。
# 导入 Any，用于标注尚未校验的请求消息。
from typing import Any  # JSON 顶层理论上可能不是字典。
#
# 导入共享协议处理函数，使 HTTP 与 stdio 使用同一业务逻辑。
from protocol import handle_message  # Transport 只负责搬运，不复制方法实现。
#
#
# 定义处理教学 HTTP 请求的 Handler。
class JsonRpcHandler(BaseHTTPRequestHandler):  # 每个 HTTP 请求由一个 Handler 实例处理。
    # 修改响应中的 Server 标识，说明这是教学实现。
    server_version = "Day39TeachingHTTP/1.0"  # 不伪装成生产 MCP Server。
#
    # 实现 POST 请求处理；方法名由标准库接口规定。
    def do_POST(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler 要求该命名。
        # 只允许统一的 /mcp endpoint。
        if self.path != "/mcp":  # 其他路径不属于教学协议入口。
            self.send_error(404, "use POST /mcp")  # 返回标准 HTTP 404。
            return  # 终止当前请求处理。
#
        # 捕获 Content-Length 或 JSON Body 格式错误。
        try:  # 尝试读取并解析完整 HTTP Request Body。
            content_length = int(self.headers.get("Content-Length", "0"))  # 获取 Body 字节数。
            body = self.rfile.read(content_length)  # 从网络输入流读取指定长度的 bytes。
            message: Any = json.loads(body)  # 把 UTF-8 JSON Body 解析为 Python 对象。
        # ValueError 处理长度错误，JSONDecodeError 处理 JSON 文本错误。
        except (ValueError, json.JSONDecodeError) as exc:  # 保存具体解析异常。
            # 创建 JSON-RPC Parse error，而不是只返回普通 HTTP 错误文本。
            response = {  # HTTP Body 仍然承载 JSON-RPC 响应。
                "jsonrpc": "2.0",  # 声明 JSON-RPC 2.0。
                "id": None,  # 解析失败时无法确定请求 id。
                "error": {  # 使用 error 对象表达协议失败。
                    "code": -32700,  # JSON-RPC 标准 Parse error 代码。
                    "message": "parse error",  # 稳定的错误类型描述。
                    "data": str(exc),  # 附带教学调试详情。
                },  # 结束 error 对象。
            }  # 结束 JSON-RPC 错误响应。
        # Body 成功解析后交给共享协议层。
        else:  # 只有解析无异常时执行。
            response = handle_message(message)  # 处理 tools/list、tools/call 等方法。
#
        # Notification 没有 id，因此协议层返回 None，不发送 JSON-RPC Response。
        if response is None:  # 当前消息是无需响应的 Notification。
            self.send_response(202)  # HTTP 层确认已接受消息。
            self.end_headers()  # 结束无 Body 的 HTTP Response Header。
            return  # 完成本次请求。
#
        # 把 JSON-RPC Response 编码成 UTF-8 bytes。
        payload = json.dumps(response, ensure_ascii=False).encode("utf-8")  # 作为 HTTP Response Body。
        # 返回 HTTP 200，表示 Transport 层成功交换消息。
        self.send_response(200)  # JSON-RPC 层的业务错误仍可放在 200 Body 中。
        # 声明响应体是 UTF-8 JSON。
        self.send_header("Content-Type", "application/json; charset=utf-8")  # 帮助 Client 正确解析。
        # 告诉 Client Response Body 的准确字节长度。
        self.send_header("Content-Length", str(len(payload)))  # 防止读取边界不明确。
        # 结束 HTTP Response Header。
        self.end_headers()  # 后续写入的数据都属于 Body。
        # 把 JSON-RPC Response 写入网络输出流。
        self.wfile.write(payload)  # Client 将从 HTTP Response Body 读取结果。
#
    # 覆盖标准库默认日志格式，增加教学 Server 前缀。
    def log_message(self, format: str, *args: object) -> None:  # 保留标准库要求的参数签名。
        # 将访问日志输出到终端，不写入协议 Response Body。
        print(f"[http-server] {format % args}")  # 展示请求方法、路径和 HTTP 状态。
#
#
# 封装 Server 创建逻辑，方便测试代码选择随机端口。
def create_server(  # 返回已经绑定地址但尚未 serve_forever 的 Server。
    host: str = "127.0.0.1",  # 默认只监听本机回环地址。
    port: int = 8000,  # 默认使用 8000 端口。
) -> ThreadingHTTPServer:  # 返回支持并发请求的标准库 HTTP Server。
    return ThreadingHTTPServer((host, port), JsonRpcHandler)  # 绑定地址并指定 Handler。
#
#
# 定义 HTTP Server 命令行入口。
def main() -> None:  # 解析参数、启动监听并负责优雅清理。
    # 创建参数解析器。
    parser = argparse.ArgumentParser()  # 自动生成使用帮助。
    # 允许用户覆盖监听主机。
    parser.add_argument("--host", default="127.0.0.1")  # 默认不对局域网或互联网开放。
    # 允许用户覆盖监听端口。
    parser.add_argument("--port", type=int, default=8000)  # 把输入字符串转换为整数。
    # 解析命令行参数。
    args = parser.parse_args()  # 得到 args.host 和 args.port。
#
    # 创建并绑定 HTTP Server。
    server = create_server(args.host, args.port)  # 此时端口已经开始监听。
    # 向学习者展示 Client 应访问的 endpoint。
    print(f"Teaching JSON-RPC HTTP server: http://{args.host}:{args.port}/mcp")  # 启动提示。
    # 捕获 Ctrl+C，使终端停止时能够进入 finally 清理 socket。
    try:  # 开始长期处理 HTTP 请求。
        server.serve_forever()  # 循环接受连接并交给 JsonRpcHandler。
    # 用户按 Ctrl+C 时 Python 抛出 KeyboardInterrupt。
    except KeyboardInterrupt:  # 这是正常的手动停止路径。
        print("\nStopping server")  # 告知用户正在退出。
    # 无论为何退出，都关闭监听 socket。
    finally:  # 防止端口被遗留进程占用。
        server.server_close()  # 释放绑定的主机与端口资源。
#
#
# 只有直接执行本文件时才启动 HTTP Server。
if __name__ == "__main__":  # 作为模块导入时只提供类和 create_server。
    main()  # 进入 Server 运行流程。
