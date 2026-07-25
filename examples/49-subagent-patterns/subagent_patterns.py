"""
Day 49：子代理的四大模式（Subagent Patterns）示例

本代码用普通 Python 函数模拟四种子代理模式的执行流程：
1. Fan-Out / Fan-In：分发-聚合
2. Pipeline：流水线
3. Supervisor：监督者 / 层级式
4. Swarm：蜂群 / 协作式

注意：这里用 Python 函数和线程模拟子代理，真实场景中子代理通常由
Agent 框架（如 Claude Code、Codex、LangGraph、smolagents 等）创建和调度。
"""

import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Dict, Any


def log(msg: str) -> None:
    """打印带时间戳的日志，方便观察执行顺序。"""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


# ============================================================================
# 模拟子代理调度器
# ============================================================================

def spawn_subagent(name: str, task: Callable[[], Any]) -> Any:
    """
    模拟派生一个子代理去执行任务。

    真实场景中，这里会调用 Agent 框架的 spawn API。
    这里简化为直接执行一个函数。
    """
    log(f"🤖 子代理 [{name}] 开始工作...")
    result = task()
    log(f"✅ 子代理 [{name}] 完成工作")
    return result


# ============================================================================
# Pattern 1: Fan-Out / Fan-In（分发-聚合）
# ============================================================================

def evaluate_model(model_name: str) -> Dict[str, Any]:
    """模拟评估一个模型，返回模型名称和分数。"""
    # 模拟耗时：0.5 ~ 1.5 秒
    sleep_time = random.uniform(0.5, 1.5)
    time.sleep(sleep_time)
    score = round(random.uniform(0.7, 0.95), 3)
    return {"model": model_name, "score": score, "time": round(sleep_time, 2)}


def fan_out_fan_in_demo() -> None:
    """Fan-Out / Fan-In 模式演示：并行评估多个模型。"""
    print("\n" + "=" * 60)
    print("Pattern 1: Fan-Out / Fan-In（分发-聚合）")
    print("=" * 60)

    models = ["Model-A", "Model-B", "Model-C", "Model-D", "Model-E"]
    log(f"父代理：需要并行评估 {len(models)} 个模型")

    start = time.time()

    # Fan-Out：同时派生多个子代理
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_model = {
            executor.submit(spawn_subagent, model, lambda m=model: evaluate_model(m)): model
            for model in models
        }

        # Fan-In：等待所有子代理完成并收集结果
        for future in as_completed(future_to_model):
            results.append(future.result())

    elapsed = round(time.time() - start, 2)

    # 聚合结果
    ranked = sorted(results, key=lambda x: x["score"], reverse=True)

    log(f"聚合完成，总耗时：{elapsed} 秒（注意：≈ 最慢子代理的时间）")
    print("\n📊 评估结果排名：")
    for i, r in enumerate(ranked, 1):
        print(f"  第 {i} 名：{r['model']}，分数 {r['score']}，耗时 {r['time']}s")


# ============================================================================
# Pattern 2: Pipeline（流水线）
# ============================================================================

def extract_data(raw_data: str) -> List[str]:
    """阶段1：从原始数据中提取字段。"""
    time.sleep(0.5)
    return raw_data.split(",")


def clean_data(data: List[str]) -> List[str]:
    """阶段2：清洗数据。"""
    time.sleep(0.5)
    return [item.strip().upper() for item in data if item.strip()]


def analyze_data(data: List[str]) -> Dict[str, int]:
    """阶段3：分析数据。"""
    time.sleep(0.5)
    return {"total": len(data), "unique": len(set(data))}


def generate_report(analysis: Dict[str, int]) -> str:
    """阶段4：生成报告。"""
    time.sleep(0.5)
    return f"报告：共 {analysis['total']} 条记录，去重后 {analysis['unique']} 条。"


def pipeline_demo() -> None:
    """Pipeline 模式演示：数据按阶段依次处理。"""
    print("\n" + "=" * 60)
    print("Pattern 2: Pipeline（流水线）")
    print("=" * 60)

    raw_data = "apple, banana, apple, cherry, banana, , date"
    log(f"父代理：启动数据流水线，原始数据：{raw_data!r}")

    start = time.time()

    # 阶段1：Extract
    extracted = spawn_subagent("Extract", lambda: extract_data(raw_data))
    log(f"阶段1输出：{extracted}")

    # 阶段2：Clean（依赖阶段1输出）
    cleaned = spawn_subagent("Clean", lambda: clean_data(extracted))
    log(f"阶段2输出：{cleaned}")

    # 阶段3：Analyze（依赖阶段2输出）
    analysis = spawn_subagent("Analyze", lambda: analyze_data(cleaned))
    log(f"阶段3输出：{analysis}")

    # 阶段4：Report（依赖阶段3输出）
    report = spawn_subagent("Report", lambda: generate_report(analysis))
    log(f"阶段4输出：{report}")

    elapsed = round(time.time() - start, 2)

    print(f"\n📄 最终报告：{report}")
    print(f"⏱️  总耗时：{elapsed} 秒（各阶段串行相加）")


# ============================================================================
# Pattern 3: Supervisor（监督者 / 层级式）
# ============================================================================

def sales_agent() -> Dict[str, Any]:
    """销售专家子代理：使用 CRM 工具查询销售数据。"""
    time.sleep(0.6)
    return {
        "role": "Sales",
        "tool": "CRM",
        "result": "本季度销售额 1200 万，转化率 3.2%",
    }


def engineering_agent() -> Dict[str, Any]:
    """工程专家子代理：使用 GitHub API 查询开发进度。"""
    time.sleep(0.7)
    return {
        "role": "Engineering",
        "tool": "GitHub API",
        "result": "完成 15 个新功能，修复 42 个 bug",
    }


def marketing_agent() -> Dict[str, Any]:
    """市场专家子代理：使用分析平台查询市场反馈。"""
    time.sleep(0.5)
    return {
        "role": "Marketing",
        "tool": "Analytics Platform",
        "result": "社媒曝光 500 万，用户满意度 4.6/5",
    }


def supervisor_demo() -> None:
    """Supervisor 模式演示：父代理协调多个专业子代理。"""
    print("\n" + "=" * 60)
    print("Pattern 3: Supervisor（监督者 / 层级式）")
    print("=" * 60)

    log("父代理（Supervisor）：需要准备产品发布报告，调用三位专家")

    start = time.time()

    # 同时派出三位专家（并行）
    specialists = {
        "Sales": sales_agent,
        "Engineering": engineering_agent,
        "Marketing": marketing_agent,
    }

    findings = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_role = {
            executor.submit(spawn_subagent, name, task): name
            for name, task in specialists.items()
        }
        for future in as_completed(future_to_role):
            role = future_to_role[future]
            findings[role] = future.result()

    elapsed = round(time.time() - start, 2)

    # 父代理整合各专业输出
    print("\n📋 各专业子代理输出：")
    for role, finding in findings.items():
        print(f"  [{finding['role']}] 使用 {finding['tool']}：{finding['result']}")

    report = (
        "产品发布报告：\n"
        f"  - {findings['Sales']['result']}\n"
        f"  - {findings['Engineering']['result']}\n"
        f"  - {findings['Marketing']['result']}"
    )
    print(f"\n📄 Supervisor 整合后的报告：\n{report}")
    print(f"⏱️  总耗时：{elapsed} 秒（专家并行工作）")


# ============================================================================
# Pattern 4: Swarm（蜂群 / 协作式）
# ============================================================================

def architect_review(design: str) -> str:
    """架构师角度评审。"""
    time.sleep(0.6)
    return f"架构评审：'{design}' 应采用微服务架构，便于后续扩展。"


def security_review(design: str) -> str:
    """安全专家角度评审。"""
    time.sleep(0.7)
    return f"安全评审：'{design}' 需要增加 OAuth2 认证和输入校验。"


def performance_review(design: str) -> str:
    """性能专家角度评审。"""
    time.sleep(0.5)
    return f"性能评审：'{design}' 建议引入缓存，目标响应时间 < 100ms。"


def swarm_demo() -> None:
    """Swarm 模式演示：多个子代理多角度评审同一份设计稿。"""
    print("\n" + "=" * 60)
    print("Pattern 4: Swarm（蜂群 / 协作式）")
    print("=" * 60)

    initial_design = "设计一个用户订单查询 API"
    log(f"父代理：发布初始设计稿——{initial_design}")

    start = time.time()

    # 三个专家从各自角度同时评审同一份设计稿
    reviewers = {
        "Architect": architect_review,
        "Security": security_review,
        "Performance": performance_review,
    }

    reviews = {}
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_role = {
            executor.submit(spawn_subagent, name, lambda d=initial_design, t=task: t(d)): name
            for name, task in reviewers.items()
        }
        for future in as_completed(future_to_role):
            role = future_to_role[future]
            reviews[role] = future.result()

    elapsed = round(time.time() - start, 2)

    print("\n📝 各角度评审意见：")
    for role, review in reviews.items():
        print(f"  [{role}] {review}")

    # 父代理综合所有意见，生成改进版设计
    improved_design = (
        f"改进版设计：{initial_design}，采用微服务架构，"
        "集成 OAuth2 认证、输入校验和缓存机制，目标响应时间 < 100ms。"
    )
    print(f"\n🔧 父代理整合后的改进版设计：\n  {improved_design}")
    print(f"⏱️  总耗时：{elapsed} 秒（多角度并行评审）")


# ============================================================================
# 主程序：运行所有模式演示
# ============================================================================

def main() -> None:
    print("\n🚀 开始运行子代理四大模式演示...\n")
    print("注意：本示例用 Python 线程模拟子代理并行执行。")
    print("真实场景中，spawn_subagent 会调用 Agent 框架的 API。\n")

    # 为了演示效果可复现，固定随机种子
    random.seed(42)

    fan_out_fan_in_demo()
    pipeline_demo()
    supervisor_demo()
    swarm_demo()

    print("\n" + "=" * 60)
    print("✅ 所有模式演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
