# 第28天三种端到端 Agent 风格对比脚本。  # 说明本文件用途
from __future__ import annotations  # 启用延迟类型注解

import importlib.util  # 导入动态模块加载工具
import sys  # 导入系统模块以注册动态模块
from pathlib import Path  # 导入路径工具

BASE_DIR = Path(__file__).parent  # 获取当前脚本所在目录

def load_function(file_name: str, function_name: str):  # 定义从相邻文件加载函数的工具
    module_path = BASE_DIR / file_name  # 拼出模块路径
    spec = importlib.util.spec_from_file_location(file_name.replace(".py", ""), module_path)  # 创建模块加载规格
    if spec is None or spec.loader is None:  # 判断加载规格是否有效
        raise RuntimeError(f"Cannot load module from {module_path}")  # 抛出加载失败错误
    module = importlib.util.module_from_spec(spec)  # 根据规格创建模块对象
    sys.modules[spec.name] = module  # 注册模块以兼容类和类型系统
    spec.loader.exec_module(module)  # 执行模块代码
    return getattr(module, function_name)  # 返回指定函数

def main() -> None:  # 定义脚本入口函数
    query = "I need to speak with Dr. Nikola Tesla about recent advancements in wireless energy."  # 准备多工具问题
    smol_builder = load_function("01_smolagents_end_to_end_agent.py", "build_smolagents_alfred")  # 加载 smolagents 构建函数
    llama_builder = load_function("02_llama_index_end_to_end_agent.py", "build_llama_index_alfred")  # 加载 LlamaIndex 构建函数
    langgraph_builder = load_function("03_langgraph_end_to_end_agent.py", "build_langgraph_alfred")  # 加载 LangGraph 构建函数
    smol_agent = smol_builder()  # 构建 smolagents 风格 Agent
    llama_agent = llama_builder()  # 构建 LlamaIndex 风格 Agent
    langgraph_agent = langgraph_builder()  # 构建 LangGraph 风格 Agent
    print("=" * 80)  # 打印分隔线
    print("smolagents style")  # 打印当前风格名称
    print(smol_agent.run(query))  # 运行 smolagents 风格 Agent
    print("=" * 80)  # 打印分隔线
    print("llama-index style")  # 打印当前风格名称
    print(llama_agent.run(query))  # 运行 LlamaIndex 风格 Agent
    print("=" * 80)  # 打印分隔线
    print("langgraph style")  # 打印当前风格名称
    print(langgraph_agent.invoke({"messages": query})["messages"][-1]["content"])  # 运行 LangGraph 风格 Agent

if __name__ == "__main__":  # 判断是否直接执行脚本
    main()  # 调用脚本入口
