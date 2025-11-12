#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量运行EPJ对话 - 依次运行所有剧本

功能：
1. 自动遍历所有可用的剧本（001-100）
2. 依次运行每个剧本的EPJ对话
3. 保存每个剧本的结果到独立的JSON文件
4. 生成汇总报告
"""

import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '.')

# 尝试从config/api_config.py加载API key
try:
    from config.api_config import OPENROUTER_API_KEY
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_api_key_here":
        os.environ['OPENROUTER_API_KEY'] = OPENROUTER_API_KEY
        print(f"✅ 从 api_config.py 加载API key")
except ImportError:
    print(f"⚠️ 未找到 config/api_config.py，将使用 .env 文件")

from Benchmark.topics.config_loader import load_config, list_scenarios
from Benchmark.agents.actor import Actor
from Benchmark.agents.director import Director
from Benchmark.agents.judger import Judger
from Benchmark.agents.test_model import TestModel
from Benchmark.orchestrator.chat_loop_epj import run_chat_loop_epj


class BatchRunner:
    """批量运行器"""
    
    def __init__(self, 
                 max_turns=15, 
                 K=3,
                 actor_model="google/gemini-2.5-flash",
                 director_model="google/gemini-2.5-pro",
                 judger_model="google/gemini-2.5-pro",
                 test_model="openai/gpt-4o-mini",
                 output_dir="results/batch_runs"):
        """
        初始化批量运行器
        
        Args:
            max_turns: 最大对话轮数
            K: 评估周期
            actor_model: Actor使用的模型
            director_model: Director使用的模型
            judger_model: Judger使用的模型
            test_model: 被测试的模型
            output_dir: 结果输出目录
        """
        self.max_turns = max_turns
        self.K = K
        self.actor_model = actor_model
        self.director_model = director_model
        self.judger_model = judger_model
        self.test_model_name = test_model
        self.output_dir = Path(output_dir)
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 运行统计
        self.stats = {
            "total_scripts": 0,
            "successful": 0,
            "failed": 0,
            "results": []
        }
    
    def run_single_script(self, script_id: str) -> dict:
        """
        运行单个剧本
        
        Args:
            script_id: 剧本ID
        
        Returns:
            dict: 运行结果
        """
        print(f"\n{'='*70}")
        print(f"🎭 运行剧本 {script_id}")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        try:
            # 加载配置
            config = load_config(script_id)
            actor_prompt = config['actor_prompt']
            scenario = config['scenario']
            
            print(f"\n✅ 配置加载成功")
            print(f"   剧本编号: {scenario.get('剧本编号')}")
            
            # 初始化 Agents
            actor = Actor(model_name=self.actor_model)
            actor.set_system_prompt(actor_prompt)  # 🔧 修复：设置Actor的system prompt
            
            director = Director(
                scenario=scenario,
                actor_prompt=actor_prompt,
                model_name=self.director_model,
                use_function_calling=True
            )
            judger = Judger(model_name=self.judger_model)
            test_model = TestModel(model_name=self.test_model_name)
            
            print(f"\n✅ Agents 初始化成功")
            
            # 运行对话
            print(f"\n🎬 开始对话循环...")
            result = run_chat_loop_epj(
                actor=actor,
                director=director,
                judger=judger,
                test_model=test_model,
                script_id=script_id,
                max_turns=self.max_turns,
                K=self.K
            )
            
            # 添加运行时间
            elapsed_time = time.time() - start_time
            result['elapsed_time_seconds'] = round(elapsed_time, 2)
            result['timestamp'] = datetime.now().isoformat()
            
            # 保存单个结果
            self._save_single_result(script_id, result)
            
            print(f"\n✅ 剧本 {script_id} 完成")
            print(f"   总轮数: {result['total_turns']}")
            print(f"   终止原因: {result['termination_reason']}")
            print(f"   用时: {elapsed_time:.2f}秒")
            
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
            print(f"\n❌ 剧本 {script_id} 失败: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "script_id": script_id,
                "status": "failed",
                "error": str(e),
                "elapsed_time": elapsed_time
            }
    
    def _save_single_result(self, script_id: str, result: dict):
        """保存单个剧本的结果"""
        output_file = self.output_dir / f"result_{script_id}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"   💾 结果已保存: {output_file}")
    
    def run_batch(self, script_ids: list = None, start_from: str = None, end_at: str = None):
        """
        批量运行剧本
        
        Args:
            script_ids: 指定要运行的剧本ID列表，为None则运行所有
            start_from: 从哪个剧本开始（如"010"）
            end_at: 运行到哪个剧本结束（如"020"）
        """
        # 获取所有可用剧本
        all_scripts = list_scenarios()
        
        # 确定要运行的剧本列表
        if script_ids is not None:
            # 使用指定的列表
            target_scripts = script_ids
        else:
            # 使用范围过滤
            target_scripts = all_scripts
            
            if start_from:
                target_scripts = [s for s in target_scripts if s >= start_from]
            
            if end_at:
                target_scripts = [s for s in target_scripts if s <= end_at]
        
        self.stats["total_scripts"] = len(target_scripts)
        
        print(f"\n{'='*70}")
        print(f"📦 批量运行模式")
        print(f"{'='*70}")
        print(f"\n📋 运行计划:")
        print(f"   总剧本数: {len(target_scripts)}")
        print(f"   剧本范围: {target_scripts[0]} - {target_scripts[-1]}")
        print(f"   最大轮数: {self.max_turns}")
        print(f"   评估周期K: {self.K}")
        print(f"   输出目录: {self.output_dir}")
        
        print(f"\n🤖 模型配置:")
        print(f"   Actor: {self.actor_model}")
        print(f"   Director: {self.director_model}")
        print(f"   Judger: {self.judger_model}")
        print(f"   TestModel: {self.test_model_name}")
        
        # 确认开始
        print(f"\n{'='*70}")
        input("按 Enter 开始批量运行...")
        
        # 运行所有剧本
        for i, script_id in enumerate(target_scripts, 1):
            print(f"\n\n{'#'*70}")
            print(f"# 进度: {i}/{len(target_scripts)} - 剧本 {script_id}")
            print(f"{'#'*70}")
            
            result = self.run_single_script(script_id)
            self.stats["results"].append(result)
            
            if result["status"] == "success":
                self.stats["successful"] += 1
            else:
                self.stats["failed"] += 1
            
            # 显示进度
            print(f"\n📊 当前进度: {self.stats['successful']}成功 / {self.stats['failed']}失败 / {len(target_scripts)}总数")
            
            # 短暂休息，避免API限流
            if i < len(target_scripts):
                print(f"   ⏸️  休息3秒...")
                time.sleep(3)
        
        # 生成汇总报告
        self._generate_summary_report()
    
    def _generate_summary_report(self):
        """生成汇总报告"""
        print(f"\n\n{'='*70}")
        print(f"📊 批量运行完成 - 汇总报告")
        print(f"{'='*70}")
        
        print(f"\n📈 总体统计:")
        print(f"   总剧本数: {self.stats['total_scripts']}")
        print(f"   成功: {self.stats['successful']} ({self.stats['successful']/self.stats['total_scripts']*100:.1f}%)")
        print(f"   失败: {self.stats['failed']} ({self.stats['failed']/self.stats['total_scripts']*100:.1f}%)")
        
        # 成功的剧本
        if self.stats['successful'] > 0:
            print(f"\n✅ 成功的剧本:")
            for result in self.stats['results']:
                if result['status'] == 'success':
                    print(f"   {result['script_id']}: {result['total_turns']}轮, "
                          f"P_0={result['P_0']}, P_final={result['P_final']}, "
                          f"{result['elapsed_time']:.1f}秒")
        
        # 失败的剧本
        if self.stats['failed'] > 0:
            print(f"\n❌ 失败的剧本:")
            for result in self.stats['results']:
                if result['status'] == 'failed':
                    print(f"   {result['script_id']}: {result['error']}")
        
        # 保存汇总报告
        summary_file = self.output_dir / "batch_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 汇总报告已保存: {summary_file}")
        
        print(f"\n{'='*70}")
        print(f"✅ 批量运行完成！")
        print(f"{'='*70}")


def main():
    """主函数"""
    
    print("=" * 70)
    print("🚀 EPJ 批量运行工具")
    print("=" * 70)
    
    # ================================================================
    # 配置参数
    # ================================================================
    
    # 基础参数
    MAX_TURNS = 15          # 每个剧本的最大轮数
    K = 3                   # 评估周期
    
    # 模型配置
    ACTOR_MODEL = "google/gemini-2.5-flash"         # Gemini Flash 2.5
    DIRECTOR_MODEL = "google/gemini-2.5-pro"        # Gemini Pro 2.5
    JUDGER_MODEL = "google/gemini-2.5-pro"          # Gemini Pro 2.5
    TEST_MODEL = "openai/gpt-4o-mini"               # 被测模型
    
    # 输出目录
    OUTPUT_DIR = "results/batch_runs"
    
    # ================================================================
    # 运行模式选择
    # ================================================================
    
    print(f"\n请选择运行模式:")
    print(f"  1. 运行所有剧本 (001-100)")
    print(f"  2. 运行指定范围 (如 001-010)")
    print(f"  3. 运行指定的剧本列表 (如 001,005,010)")
    print(f"  4. 测试模式（只运行前3个剧本）")
    
    choice = input(f"\n请输入选项 (1-4): ").strip()
    
    # 初始化批量运行器
    runner = BatchRunner(
        max_turns=MAX_TURNS,
        K=K,
        actor_model=ACTOR_MODEL,
        director_model=DIRECTOR_MODEL,
        judger_model=JUDGER_MODEL,
        test_model=TEST_MODEL,
        output_dir=OUTPUT_DIR
    )
    
    # 根据选择确定运行范围
    if choice == "1":
        # 运行所有剧本
        runner.run_batch()
        
    elif choice == "2":
        # 运行指定范围
        start = input("起始剧本ID (如 001): ").strip()
        end = input("结束剧本ID (如 010): ").strip()
        runner.run_batch(start_from=start, end_at=end)
        
    elif choice == "3":
        # 运行指定列表
        scripts_input = input("请输入剧本ID，用逗号分隔 (如 001,005,010): ").strip()
        script_list = [s.strip() for s in scripts_input.split(",")]
        runner.run_batch(script_ids=script_list)
        
    elif choice == "4":
        # 测试模式
        print(f"\n🧪 测试模式：只运行前3个剧本")
        runner.run_batch(script_ids=["001", "002", "003"])
        
    else:
        print(f"\n❌ 无效选项")
        return


if __name__ == "__main__":
    main()

