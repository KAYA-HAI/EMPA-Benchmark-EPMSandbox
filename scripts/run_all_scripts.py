#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行所有剧本 - 简化版批量运行工具

特点：
1. 自动运行所有剧本（001-100）
2. 支持断点续传（跳过已完成的剧本）
3. 实时保存进度
4. 详细的日志记录
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '.')

# 加载API key
try:
    from config.api_config import OPENROUTER_API_KEY
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_api_key_here":
        os.environ['OPENROUTER_API_KEY'] = OPENROUTER_API_KEY
        print(f"✅ API key 已配置")
except ImportError:
    print(f"⚠️ 请在 config/api_config.py 中配置 API key")

from Benchmark.topics.config_loader import load_config, list_scenarios
from Benchmark.agents.actor import Actor
from Benchmark.agents.director import Director
from Benchmark.agents.judger import Judger
from Benchmark.agents.test_model import TestModel
from Benchmark.orchestrator.chat_loop_epj import run_chat_loop_epj


# ================================================================
# 配置参数（可以在这里修改）
# ================================================================

MAX_TURNS = 15                                      # 每个剧本的最大轮数
K = 3                                               # EPJ评估周期
ACTOR_MODEL = "google/gemini-2.5-flash"            # Actor模型（Gemini Flash 2.5）
DIRECTOR_MODEL = "google/gemini-2.5-pro"           # Director模型（Gemini Pro 2.5）
JUDGER_MODEL = "google/gemini-2.5-pro"             # Judger模型（Gemini Pro 2.5）
TEST_MODEL = "openai/gpt-4o-mini"                  # 被测模型
OUTPUT_DIR = "results/all_scripts"                 # 输出目录
SLEEP_BETWEEN_SCRIPTS = 3                          # 剧本之间的休息时间（秒）

# ================================================================


def get_completed_scripts(output_dir: Path) -> set:
    """获取已完成的剧本ID"""
    completed = set()
    
    if not output_dir.exists():
        return completed
    
    for file in output_dir.glob("result_*.json"):
        # 从文件名提取ID: result_001.json -> 001
        script_id = file.stem.replace("result_", "")
        completed.add(script_id)
    
    return completed


def save_progress(output_dir: Path, stats: dict):
    """保存进度"""
    progress_file = output_dir / "progress.json"
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


def run_single_script(script_id: str, output_dir: Path) -> dict:
    """运行单个剧本"""
    
    start_time = time.time()
    
    try:
        # 加载配置
        config = load_config(script_id)
        actor_prompt = config['actor_prompt']
        scenario = config['scenario']
        
        # 初始化 Agents
        actor = Actor(model_name=ACTOR_MODEL)
        actor.set_system_prompt(actor_prompt)  # 🔧 修复：设置Actor的system prompt
        
        director = Director(
            scenario=scenario,
            actor_prompt=actor_prompt,
            model_name=DIRECTOR_MODEL,
            use_function_calling=True
        )
        judger = Judger(model_name=JUDGER_MODEL)
        test_model = TestModel(model_name=TEST_MODEL)
        
        # 运行对话
        result = run_chat_loop_epj(
            actor=actor,
            director=director,
            judger=judger,
            test_model=test_model,
            script_id=script_id,
            max_turns=MAX_TURNS,
            K=K
        )
        
        # 添加元数据
        elapsed_time = time.time() - start_time
        result['elapsed_time_seconds'] = round(elapsed_time, 2)
        result['timestamp'] = datetime.now().isoformat()
        
        # 保存结果
        output_file = output_dir / f"result_{script_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return {
            "script_id": script_id,
            "status": "success",
            "total_turns": result['total_turns'],
            "termination_reason": result['termination_reason'],
            "elapsed_time": elapsed_time,
            "P_0": result['epj']['P_0_initial_deficit'],
            "P_final": result['epj']['P_final_position']
        }
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        import traceback
        error_msg = traceback.format_exc()
        
        return {
            "script_id": script_id,
            "status": "failed",
            "error": str(e),
            "error_trace": error_msg,
            "elapsed_time": elapsed_time
        }


def main():
    """主函数"""
    
    print("=" * 70)
    print("🚀 运行所有剧本")
    print("=" * 70)
    
    # 创建输出目录
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 获取所有可用剧本
    all_scripts = list_scenarios()
    
    # 检查已完成的剧本
    completed = get_completed_scripts(output_dir)
    
    # 确定待运行的剧本
    pending_scripts = [s for s in all_scripts if s not in completed]
    
    print(f"\n📋 运行状态:")
    print(f"   总剧本数: {len(all_scripts)}")
    print(f"   已完成: {len(completed)}")
    print(f"   待运行: {len(pending_scripts)}")
    
    if completed:
        print(f"\n   已完成的剧本: {sorted(completed)[:10]}{'...' if len(completed) > 10 else ''}")
    
    if not pending_scripts:
        print(f"\n✅ 所有剧本都已完成！")
        return
    
    print(f"\n⚙️ 运行配置:")
    print(f"   最大轮数: {MAX_TURNS}")
    print(f"   评估周期K: {K}")
    print(f"   模型: {ACTOR_MODEL}")
    print(f"   输出目录: {output_dir}")
    
    print(f"\n💡 提示:")
    print(f"   - 结果将保存到 {output_dir}/result_XXX.json")
    print(f"   - 可以随时中断(Ctrl+C)，下次会自动跳过已完成的剧本")
    print(f"   - 每个剧本之间会休息 {SLEEP_BETWEEN_SCRIPTS} 秒")
    
    # 确认开始
    print(f"\n{'='*70}")
    response = input(f"准备运行 {len(pending_scripts)} 个剧本，是否继续？(y/n): ").strip().lower()
    
    if response != 'y':
        print("已取消")
        return
    
    # 初始化统计
    stats = {
        "start_time": datetime.now().isoformat(),
        "total_scripts": len(pending_scripts),
        "successful": 0,
        "failed": 0,
        "results": []
    }
    
    # 运行所有待处理的剧本
    for i, script_id in enumerate(pending_scripts, 1):
        print(f"\n\n{'#'*70}")
        print(f"# 进度: {i}/{len(pending_scripts)} - 剧本 {script_id}")
        print(f"# 已完成: {stats['successful']}成功 / {stats['failed']}失败")
        print(f"{'#'*70}")
        
        try:
            result = run_single_script(script_id, output_dir)
            stats["results"].append(result)
            
            if result["status"] == "success":
                stats["successful"] += 1
                print(f"\n✅ 剧本 {script_id} 完成")
                print(f"   轮数: {result['total_turns']}")
                print(f"   P_0: {result['P_0']}")
                print(f"   P_final: {result['P_final']}")
                print(f"   用时: {result['elapsed_time']:.1f}秒")
            else:
                stats["failed"] += 1
                print(f"\n❌ 剧本 {script_id} 失败: {result['error']}")
            
            # 保存进度
            save_progress(output_dir, stats)
            
            # 休息一下（避免API限流）
            if i < len(pending_scripts):
                print(f"\n⏸️  休息 {SLEEP_BETWEEN_SCRIPTS} 秒...")
                time.sleep(SLEEP_BETWEEN_SCRIPTS)
                
        except KeyboardInterrupt:
            print(f"\n\n⚠️ 用户中断")
            stats["interrupted_at"] = script_id
            save_progress(output_dir, stats)
            print(f"   进度已保存，下次运行会从剧本 {script_id} 继续")
            return
        
        except Exception as e:
            print(f"\n❌ 意外错误: {e}")
            import traceback
            traceback.print_exc()
            stats["failed"] += 1
            stats["results"].append({
                "script_id": script_id,
                "status": "failed",
                "error": str(e)
            })
            save_progress(output_dir, stats)
            
            # 询问是否继续
            response = input(f"\n是否继续运行剩余剧本？(y/n): ").strip().lower()
            if response != 'y':
                return
    
    # 完成
    stats["end_time"] = datetime.now().isoformat()
    
    # 生成最终报告
    print(f"\n\n{'='*70}")
    print(f"📊 批量运行完成")
    print(f"{'='*70}")
    
    print(f"\n📈 统计:")
    print(f"   总剧本: {stats['total_scripts']}")
    print(f"   成功: {stats['successful']} ({stats['successful']/stats['total_scripts']*100:.1f}%)")
    print(f"   失败: {stats['failed']} ({stats['failed']/stats['total_scripts']*100:.1f}%)")
    
    # 保存最终汇总
    summary_file = output_dir / "final_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果保存位置:")
    print(f"   - 单个结果: {output_dir}/result_XXX.json")
    print(f"   - 汇总报告: {summary_file}")
    
    print(f"\n{'='*70}")
    print(f"✅ 完成！")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

