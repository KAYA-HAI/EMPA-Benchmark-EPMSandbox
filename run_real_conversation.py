#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行真实EPJ对话

使用真实的LLM，基于 actor_prompt_001.md + scenario_001.json
"""

import sys
import os
sys.path.insert(0, '.')

# 尝试从config/api_config.py加载API key（如果.env不存在）
try:
    from config.api_config import OPENROUTER_API_KEY
    if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_api_key_here":
        os.environ['OPENROUTER_API_KEY'] = OPENROUTER_API_KEY
        print(f"✅ 从 api_config.py 加载API key")
except ImportError:
    print(f"⚠️ 未找到 config/api_config.py，将使用 .env 文件")

from Benchmark.topics.config_loader import load_config
from Benchmark.agents.actor import Actor
from Benchmark.agents.director import Director
from Benchmark.agents.judger import Judger
from Benchmark.agents.test_model import TestModel
from Benchmark.orchestrator.chat_loop_epj import run_chat_loop_epj


def main():
    """运行真实EPJ对话"""
    
    # ================================================================
    # 配置参数
    # ================================================================
    
    SCRIPT_ID = "001"  # 使用 actor_prompt_001.md + scenario_001.json
    
    print("=" * 70)
    print(f"🎭 真实EPJ对话 - {SCRIPT_ID}号剧本")
    print("=" * 70)
    MAX_TURNS = 45     # 最大对话轮数
    K = 1              # 每1轮评估一次EPJ（更精细的追踪）
    
    # LLM模型配置（使用OpenRouter支持的模型）
    # 注意：:free后缀的免费模型可能已失效，使用付费模型（费用很低）
    ACTOR_MODEL = "google/gemini-2.5-pro"  # Actor使用的模型（升级到Pro以更好遵守约束）
    DIRECTOR_MODEL = "google/gemini-2.5-pro"  # Director使用的模型（Gemini Pro 2.5）
    JUDGER_MODEL = "google/gemini-2.5-pro"  # Judger使用的模型（Gemini Pro 2.5）
    TEST_MODEL_NAME = "qwen/qwen3-32b"  # 被测试的AI助手模型（评测模型）
    
    # 其他可用模型（如果gpt-4o-mini不行）:
    # - "anthropic/claude-3-haiku"（便宜）
    # - "google/gemini-flash-1.5"（便宜）
    # - "meta-llama/llama-3.1-8b-instruct"（无:free后缀）
    
    print(f"\n📋 配置:")
    print(f"   剧本ID: {SCRIPT_ID}")
    print(f"   最大轮数: {MAX_TURNS}")
    print(f"   评估周期K: {K}")
    print(f"   Actor模型: {ACTOR_MODEL}")
    print(f"   Director模型: {DIRECTOR_MODEL}")
    print(f"   Judger模型: {JUDGER_MODEL}")
    print(f"   被测模型: {TEST_MODEL_NAME}")
    
    # ================================================================
    # 加载剧本
    # ================================================================
    
    print(f"\n{'='*70}")
    print(f"📚 加载剧本配置")
    print(f"{'='*70}")
    
    try:
        config = load_config(SCRIPT_ID)
        actor_prompt = config['actor_prompt']
        scenario = config['scenario']
        
        print(f"\n✅ 剧本加载成功")
        print(f"   Actor Prompt: {len(actor_prompt)} 字符")
        print(f"   剧本编号: {scenario.get('剧本编号')}")
        print(f"   故事阶段: {len(scenario.get('故事的经过', {}))} 个")
        
        # 显示剧本摘要（从配置中动态提取）
        print(f"\n📖 剧本摘要:")
        # 尝试从actor_prompt中提取角色信息（第一次出现的姓名、年龄）
        import re
        name_match = re.search(r'姓名[：:]\s*(\S+)', actor_prompt)
        age_match = re.search(r'年龄[：:]\s*(\d+)', actor_prompt)
        role_name = name_match.group(1) if name_match else "未知"
        role_age = age_match.group(1) if age_match else "未知"
        
        # 从scenario中提取话题
        topic = scenario.get('故事的起因', '未知话题')
        if len(topic) > 50:
            topic = topic[:50] + "..."
        
        print(f"   角色: {role_name}，{role_age}岁")
        print(f"   话题: {topic}")
        
        # 尝试从actor_prompt中提取共情需求优先级
        priority_match = re.search(r'共情需求优先级[：:]?\s*(.+)', actor_prompt)
        if priority_match:
            print(f"   共情需求优先级: {priority_match.group(1)}")
        else:
            print(f"   共情需求优先级: （未在配置中指定）")
        
        # 显示故事阶段
        print(f"\n📋 故事阶段:")
        for i, (key, stage) in enumerate(scenario.get('故事的经过', {}).items()):
            print(f"   [{i}] {stage.get('标题')}: {stage.get('内容')[:40]}...")
        
    except Exception as e:
        print(f"\n❌ 剧本加载失败: {e}")
        print(f"\n请确保以下文件存在:")
        print(f"   • Benchmark/topics/data/actor_prompt_001.md")
        print(f"   • Benchmark/topics/data/scenarios/scenario_001.json")
        return
    
    # ================================================================
    # 初始化Agents
    # ================================================================
    
    print(f"\n{'='*70}")
    print(f"🤖 初始化Agents")
    print(f"{'='*70}")
    
    try:
        # 初始化各个Agent
        actor = Actor(model_name=ACTOR_MODEL)
        actor.set_system_prompt(actor_prompt)  # 🔧 修复：设置Actor的system prompt
        
        director = Director(
            scenario=scenario,
            actor_prompt=actor_prompt,
            model_name=DIRECTOR_MODEL,
            use_function_calling=True
        )
        judger = Judger(model_name=JUDGER_MODEL)
        test_model = TestModel(model_name=TEST_MODEL_NAME)
        
        print(f"\n✅ 所有Agents初始化成功")
        
    except Exception as e:
        print(f"\n❌ Agent初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # ================================================================
    # 运行EPJ对话循环
    # ================================================================
    
    print(f"\n{'='*70}")
    print(f"🎬 开始EPJ对话循环")
    print(f"{'='*70}")
    
    print(f"\n✅ API key已配置，开始运行对话...")
    
    try:
        result = run_chat_loop_epj(
            actor=actor,
            director=director,
            judger=judger,
            test_model=test_model,
            script_id=SCRIPT_ID,
            max_turns=MAX_TURNS,
            K=K,
            test_model_name=TEST_MODEL_NAME  # 传递被测模型名称
        )
        
        # ================================================================
        # 显示结果
        # ================================================================
        
        print(f"\n{'='*70}")
        print(f"📊 对话结果")
        print(f"{'='*70}")
        
        print(f"\n基本信息:")
        print(f"   总轮数: {result['total_turns']}")
        print(f"   终止原因: {result['termination_reason']}")
        
        print(f"\nEPJ数据:")
        epj_data = result['epj']
        print(f"   初始赤字 P_0: {epj_data['P_0_initial_deficit']}")
        print(f"   最终位置 P_final: {epj_data['P_final_position']}")
        print(f"   总评估次数: {epj_data['total_evaluations']}")
        print(f"   评估周期K: {epj_data['K']}")
        print(f"   Epsilon阈值: {epj_data['epsilon']}")
        
        print(f"\n对话历史:")
        for i, msg in enumerate(result['history'], 1):
            role = role_name if msg['role'] == 'actor' else "AI助手"
            print(f"   {i}. {role}: {msg['content'][:60]}...")
        
        # 保存结果
        import json
        import os
        os.makedirs('results', exist_ok=True)
        with open('results/epj_conversation_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 结果已保存到: results/epj_conversation_result.json")
        
    except Exception as e:
        print(f"\n❌ 对话循环失败: {e}")
        import traceback
        traceback.print_exc()
        
        print(f"\n可能的原因:")
        print(f"   1. 缺少API key")
        print(f"   2. 网络连接问题")
        print(f"   3. LLM API调用失败")
        
        return
    
    print(f"\n{'='*70}")
    print(f"✅ 对话完成")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()

