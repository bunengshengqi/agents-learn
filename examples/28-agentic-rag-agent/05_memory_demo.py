# 第28天对话记忆演示脚本。  # 说明本文件用途
from __future__ import annotations  # 启用延迟类型注解

from common_alfred_tools import run_alfred  # 导入公共端到端执行函数

def main() -> None:  # 定义脚本入口函数
    memory: list[dict[str, str]] = []  # 创建共享会话记忆
    first_query = "Tell me about Lady Ada Lovelace."  # 准备第一轮问题
    second_query = "What projects is she currently working on?"  # 准备依赖上下文的第二轮问题
    print("=" * 80)  # 打印分隔线
    print("First turn")  # 打印第一轮标签
    print(run_alfred(first_query, memory))  # 运行第一轮并写入记忆
    print("=" * 80)  # 打印分隔线
    print("Second turn with memory")  # 打印第二轮标签
    print(run_alfred(second_query, memory))  # 运行第二轮并使用记忆解析 she

if __name__ == "__main__":  # 判断是否直接执行脚本
    main()  # 调用脚本入口
