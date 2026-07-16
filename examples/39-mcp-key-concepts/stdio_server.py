# 本脚本实现通过 stdin/stdout 搬运 JSON-RPC 消息的教学 Server。
from __future__ import annotations  # 推迟类型注解求值，保持注解兼容性。
#
# 导入 JSON 模块，用于在 Python 对象与 JSON 文本之间转换。
import json  # 负责解析 Client 请求和序列化 Server 响应。
# 导入 sys 模块，用于访问标准输入、标准输出和标准错误。
import sys  # 提供 stdin、stdout 和 stderr 三条进程数据流。
#
# 导入与 Transport 无关的共享消息处理函数。
from protocol import handle_message  # 把 JSON-RPC 对象交给协议层处理。
#
#
# 定义程序入口函数，集中管理 stdio Server 的读取循环。
def main() -> None:  # 该函数没有参数，也不返回业务结果。
    # stdout 只能输出协议消息，所以普通日志必须写入 stderr。
    print("[server] stdio transport ready", file=sys.stderr, flush=True)  # 立即输出启动日志。
#
    # 持续逐行读取 Client 写入 Server stdin 的内容。
    for line in sys.stdin:  # stdio Transport 约定一行承载一个 JSON-RPC 消息。
        # 跳过空行，避免把空字符串交给 JSON 解析器。
        if not line.strip():  # strip 后为空说明这一行没有有效消息。
            continue  # 直接读取下一行。
        # 捕获格式错误，保证一条坏消息不会让整个 Server 退出。
        try:  # 尝试把一行 JSON 文本解析成 Python 对象。
            message = json.loads(line)  # JSON-RPC Request 或 Notification 被解析为字典。
        # 单独处理 JSON 文本本身无法解析的情况。
        except json.JSONDecodeError as exc:  # exc 保存具体的解析失败位置和原因。
            # 按 JSON-RPC 2.0 格式创建 Parse error 响应。
            response = {  # 错误发生前无法读取请求 id，因此 id 使用 null。
                "jsonrpc": "2.0",  # 声明使用 JSON-RPC 2.0。
                "id": None,  # 无法识别原请求时使用空 id。
                "error": {  # error 与成功响应中的 result 互斥。
                    "code": -32700,  # -32700 是 JSON-RPC 标准解析错误码。
                    "message": "parse error",  # 提供稳定的机器可识别错误信息。
                    "data": str(exc),  # 附带便于学习和调试的解析详情。
                },  # 结束 error 对象。
            }  # 结束 JSON-RPC 错误响应。
        # JSON 解析成功后进入协议方法分发。
        else:  # 只有 try 没有抛出异常才执行这里。
            response = handle_message(message)  # 处理 initialize、tools/call 等方法。
#
        # Notification 没有 id，协议处理函数会返回 None，Server 不应响应。
        if response is not None:  # Request 或解析错误才需要向 Client 写回数据。
            # 把响应压缩为单行 JSON，防止换行被误认为下一条协议消息。
            wire_text = json.dumps(response, ensure_ascii=False, separators=(",", ":"))  # 保留中文并移除多余空格。
            # 将单行 JSON 写到 stdout，并立即刷新缓冲区。
            print(wire_text, flush=True)  # Client 可立刻从 Server stdout 读取响应。
#
#
# 只有直接运行本文件时才启动 Server，作为模块导入时不会自动执行。
if __name__ == "__main__":  # Python 直接执行入口判断。
    main()  # 进入持续读取 stdin 的 Server 主循环。
