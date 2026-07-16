# 本脚本启动 stdio Server 子进程，并演示 Request、Response 与 Notification。
from __future__ import annotations  # 推迟类型注解求值。
#
# 导入 JSON 模块，用于生成请求和解析响应。
import json  # 负责 Python 对象与 JSON 文本互转。
# 导入 Path，用于定位与本文件同目录的 Server 脚本。
from pathlib import Path  # 避免依赖用户当前工作目录拼接脚本路径。
# 导入 subprocess，用于启动和控制 Server 子进程。
import subprocess  # 提供 Popen 以及 stdin/stdout 管道。
# 导入 sys，用于取得当前 Python 解释器路径。
import sys  # sys.executable 保证 Client 与 Server 使用同一解释器。
# 导入类型工具，使函数输入输出更容易理解。
from typing import Any, TextIO  # Any 表示任意 JSON 值，TextIO 表示文本流。
#
#
# 计算 stdio_server.py 的绝对路径。
SERVER = Path(__file__).with_name("stdio_server.py")  # Client 可从任意目录启动。
#
#
# 定义发送一个 JSON-RPC Request 并等待对应 Response 的辅助函数。
def send_request(  # 把重复的序列化、写入、读取和展示逻辑封装起来。
    writer: TextIO,  # 指向 Server stdin 的文本写入流。
    reader: TextIO,  # 指向 Server stdout 的文本读取流。
    request_id: int,  # 用于关联请求与响应的 JSON-RPC id。
    method: str,  # 要调用的 MCP/JSON-RPC 方法名。
    params: dict[str, Any] | None = None,  # 可选的方法参数对象。
) -> dict[str, Any]:  # 返回解析后的 JSON-RPC Response。
    # 创建每个 Request 都必须包含的基础字段。
    request: dict[str, Any] = {  # 使用字典表达 JSON-RPC Request 对象。
        "jsonrpc": "2.0",  # 固定声明 JSON-RPC 版本。
        "id": request_id,  # Server 必须在响应中原样返回该 id。
        "method": method,  # 告诉 Server 要执行哪个方法。
    }  # 结束基础 Request 对象。
    # 只有调用方提供参数时才写入 params 字段。
    if params is not None:  # 无参数方法可以完全省略 params。
        request["params"] = params  # 加入结构化方法参数。
#
    # 将请求压缩成单行 JSON，满足 stdio 消息分隔要求。
    wire_text = json.dumps(request, ensure_ascii=False, separators=(",", ":"))  # 保留中文字符。
    # 展示消息流向，便于对照 Transport 行为。
    print(f"\nCLIENT -> STDIN\n{wire_text}")  # 这只是 Client 自己的教学输出。
    # 把 JSON 文本和消息分隔换行写入 Server stdin。
    writer.write(wire_text + "\n")  # Server 的 for line in stdin 会读到完整消息。
    # 立即刷新 Client 写入缓冲区。
    writer.flush()  # 避免 Server 一直等待尚未送出的数据。
#
    # 从 Server stdout 读取一条单行响应。
    response_line = reader.readline()  # Request 有 id，因此预期一定存在 Response。
    # 防止 Server 异常退出导致后续 json.loads 得到空字符串。
    if not response_line:  # 空字符串表示 stdout 已关闭。
        raise RuntimeError("server closed stdout before returning a response")  # 明确报告连接中断。
    # 把 JSON Response 文本解析为 Python 字典。
    response = json.loads(response_line)  # 后续可检查 id、result 或 error。
    # 输出响应方向标题。
    print("SERVER -> STDOUT")  # 帮助学习者区分请求与响应。
    # 以缩进格式展示响应内容。
    print(json.dumps(response, ensure_ascii=False, indent=2))  # 仅用于人类阅读。
    # 把响应返回给调用者，便于将来增加断言。
    return response  # 结束本次同步请求。
#
#
# 定义 Client 的完整演示流程。
def main() -> None:  # 负责启动 Server 并依次发送五个 Request。
    # 启动 Server 子进程，并为双向通信创建文本管道。
    process = subprocess.Popen(  # Popen 允许 Client 在 Server 运行期间持续交换消息。
        [sys.executable, str(SERVER)],  # 使用当前 Python 解释器执行 Server 文件。
        stdin=subprocess.PIPE,  # 创建 Client 写、Server 读的管道。
        stdout=subprocess.PIPE,  # 创建 Server 写、Client 读的管道。
        stderr=None,  # 让 Server stderr 直接显示在当前终端。
        text=True,  # 使用字符串而不是 bytes 读写管道。
        bufsize=1,  # 请求使用行缓冲，适合一行一个消息。
    )  # Server 子进程已经启动。
    # 类型和运行时双重确认两个协议管道创建成功。
    if process.stdin is None or process.stdout is None:  # PIPE 正常创建时两者都不是 None。
        raise RuntimeError("failed to open subprocess pipes")  # 无管道就无法继续通信。
#
    # 使用 try/finally 保证演示失败时也能关闭子进程输入。
    try:  # 开始执行 MCP-like 初始化和能力调用。
        # 发送初始化请求，让双方交换版本、能力和实现信息。
        send_request(  # 第一个同步 JSON-RPC Request。
            process.stdin,  # 请求写入 Server stdin。
            process.stdout,  # 响应从 Server stdout 读取。
            1,  # 初始化请求 id 为 1。
            "initialize",  # MCP 初始化方法名。
            {  # Client 在初始化时声明自身信息。
                "protocolVersion": "2025-11-25",  # Client 提议的协议版本。
                "capabilities": {},  # 教学 Client 暂不声明额外能力。
                "clientInfo": {  # 提供 Client 实现名称和版本。
                    "name": "day39-stdio-client",  # Client 名称。
                    "version": "1.0.0",  # Client 版本。
                },  # 结束 clientInfo。
            },  # 结束 initialize params。
        )  # 完成初始化 Request/Response。
#
        # 创建没有 id 的初始化完成 Notification。
        notification = {  # Notification 与 Request 的关键区别是没有 id。
            "jsonrpc": "2.0",  # 使用 JSON-RPC 2.0。
            "method": "notifications/initialized",  # 通知 Server 初始化阶段结束。
        }  # 结束 Notification 对象。
        # 把 Notification 写入 Server stdin。
        process.stdin.write(json.dumps(notification) + "\n")  # Server 不会返回响应。
        # 立即发送缓冲区中的 Notification。
        process.stdin.flush()  # 确保 Server 收到初始化完成事件。
        # 说明该消息没有响应，避免学习者误以为漏读一行。
        print("\nCLIENT -> STDIN (notification, no response expected)")  # 展示消息方向。
        # 打印 Notification 的 JSON 形态。
        print(json.dumps(notification, ensure_ascii=False))  # 用于观察它确实没有 id。
#
        # 发现 Server 暴露的 Tool 元数据。
        send_request(process.stdin, process.stdout, 2, "tools/list")  # id 2 对应工具列表。
        # 调用 add Tool，观察参数和结构化返回值。
        send_request(  # 开始 tools/call 请求。
            process.stdin,  # 写入 Server stdin。
            process.stdout,  # 读取 Server stdout。
            3,  # 工具调用请求 id。
            "tools/call",  # MCP Tool 调用方法。
            {"name": "add", "arguments": {"a": 7, "b": 5}},  # 选择 add 并传入两个数字。
        )  # 预期结果为 12。
        # 按 URI 读取 Server 暴露的只读 Resource。
        send_request(  # 开始 resources/read 请求。
            process.stdin,  # 写入 Server stdin。
            process.stdout,  # 读取 Server stdout。
            4,  # 资源读取请求 id。
            "resources/read",  # MCP Resource 读取方法。
            {"uri": "memo://course/day39"},  # 指定要读取的资源 URI。
        )  # 返回文本资源内容。
        # 获取带参数的 Prompt 模板实例。
        send_request(  # 开始 prompts/get 请求。
            process.stdin,  # 写入 Server stdin。
            process.stdout,  # 读取 Server stdout。
            5,  # Prompt 请求 id。
            "prompts/get",  # MCP Prompt 获取方法。
            {  # Prompt 名称与模板参数。
                "name": "explain_concept",  # 选择概念解释模板。
                "arguments": {"concept": "MCP transport"},  # 把概念填入模板。
            },  # 结束 Prompt 请求参数。
        )  # 返回实例化后的消息内容。
    # 无论请求成功还是失败，都执行子进程清理。
    finally:  # 防止教学 Server 遗留在后台。
        process.stdin.close()  # 关闭 stdin，让 Server 的读取循环自然结束。
        process.wait(timeout=5)  # 最多等待五秒确认 Server 子进程退出。
#
#
# 只有直接执行本文件时才运行演示。
if __name__ == "__main__":  # 模块导入不会自动启动子进程。
    main()  # 进入 stdio Client 主流程。
