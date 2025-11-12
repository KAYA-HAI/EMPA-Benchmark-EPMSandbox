#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强版 Director（多维度控制）
"""

from Benchmark.topics.config_loader import load_config
from Benchmark.agents.director import Director

def test_director_enhanced_initialization():
    """测试增强版 Director 的初始化"""
    print("=" * 70)
    print("测试 1: 增强版 Director 初始化")
    print("=" * 70)
    
    # 加载完整配置
    config = load_config("001")
    
    # 初始化 Director（现在需要传入 actor_prompt）
    director = Director(
        scenario=config['scenario'],
        actor_prompt=config['actor_prompt']
    )
    
    print(f"\n✅ Director 初始化成功")
    print(f"\n📊 Director 持有的信息:")
    print(f"   1. 故事阶段: {len(director.stages)} 个")
    for i, stage in enumerate(director.stages):
        print(f"      [{i}] {stage['阶段名']}: {stage['标题']}")
    
    print(f"\n   2. Actor Profile 部分: {len(director.actor_profile)} 个")
    for key in director.actor_profile.keys():
        print(f"      - {key}")
    
    print(f"\n   3. 故事附加信息:")
    print(f"      - 故事结果: {director.get_story_result()}")
    print(f"      - 故事插曲: 存在" if director.scenario.get('故事的插曲') else "      - 故事插曲: 无")
    
    return director


def test_release_stage(director):
    """测试释放故事阶段"""
    print("\n" + "=" * 70)
    print("测试 2: 释放故事阶段")
    print("=" * 70)
    
    result = director._handle_select_and_reveal_fragment({
        "stage_index": 0,
        "reason": "对话建立了信任，适合引入第一个回忆阶段"
    })
    
    print(f"\n📤 释放阶段 0 的结果:")
    print(f"   ✅ should_continue: {result['should_continue']}")
    print(f"   ✅ plot_action: {result['plot_action']}")
    print(f"   ✅ 已释放阶段: {director.revealed_stages}")
    
    if result.get('guidance'):
        print(f"\n💬 给 Actor 的指令（前250字符）:")
        print(result['guidance'][:250] + "...")


def test_release_memory(director):
    """测试释放角色记忆"""
    print("\n" + "=" * 70)
    print("测试 3: 释放角色记忆")
    print("=" * 70)
    
    result = director._handle_reveal_memory({
        "memory_period": "少年经历",
        "reason": "当前话题涉及失败经历，少年时期的辩论赛失利可以产生共鸣"
    })
    
    print(f"\n📤 释放记忆的结果:")
    print(f"   ✅ should_continue: {result['should_continue']}")
    print(f"   ✅ plot_action: {result['plot_action']}")
    print(f"   ✅ 已释放记忆: {director.revealed_memories}")
    
    if result.get('guidance'):
        print(f"\n💬 给 Actor 的指令（前300字符）:")
        print(result['guidance'][:300] + "...")


def test_adjust_empathy_strategy(director):
    """测试调整共情策略"""
    print("\n" + "=" * 70)
    print("测试 4: 调整共情策略")
    print("=" * 70)
    
    result = director._handle_adjust_emotion({
        "focus_aspect": "动机共情",
        "reason": "AI的回应过于浅显，需要引导倾诉者强调自己的付出和专业精神"
    })
    
    print(f"\n📤 调整策略的结果:")
    print(f"   ✅ should_continue: {result['should_continue']}")
    print(f"   ✅ plot_action: {result['plot_action']}")
    
    if result.get('guidance'):
        print(f"\n💬 给 Actor 的指令（前300字符）:")
        print(result['guidance'][:300] + "...")


def test_introduce_turning_point(director):
    """测试综合转折点"""
    print("\n" + "=" * 70)
    print("测试 5: 综合转折点（剧情 + 共情）")
    print("=" * 70)
    
    result = director._handle_introduce_turning_point({
        "stage_index": 2,  # 阶段3
        "empathy_aspect": "认知共情",
        "reason": "对话深入，可以结合剧情转折和认知共情需求"
    })
    
    print(f"\n📤 综合转折的结果:")
    print(f"   ✅ should_continue: {result['should_continue']}")
    print(f"   ✅ plot_action: {result['plot_action']}")
    print(f"   ✅ 已释放阶段: {director.revealed_stages}")
    
    if result.get('guidance'):
        print(f"\n💬 给 Actor 的指令（前400字符）:")
        print(result['guidance'][:400] + "...")


def test_function_summary(director):
    """总结可用的函数"""
    print("\n" + "=" * 70)
    print("测试 6: Director 可用函数总结")
    print("=" * 70)
    
    from Benchmark.prompts.director_function_schemas_selector import DIRECTOR_FUNCTIONS_SELECTOR
    
    print(f"\n📋 Director 现在有 {len(DIRECTOR_FUNCTIONS_SELECTOR)} 个可用函数:\n")
    
    for i, func in enumerate(DIRECTOR_FUNCTIONS_SELECTOR, 1):
        print(f"{i}. {func['name']}")
        print(f"   描述: {func['description'].strip().split('。')[0]}...")
        print()


def test_multidimensional_control():
    """展示多维度控制能力"""
    print("\n" + "=" * 70)
    print("测试 7: 多维度控制能力展示")
    print("=" * 70)
    
    print("""
Director 现在可以从三个维度控制对话：

┌─────────────────────────────────────────────────────────────┐
│ 📖 剧情维度 (scenario.json)                                │
│    - 4个故事阶段：引发回忆 → 引发思考 → 引发自审 → 情绪崩发  │
│    - 故事插曲：大学答辩的回忆                               │
├─────────────────────────────────────────────────────────────┤
│ 💭 记忆维度 (actor_prompt - experience)                    │
│    - 童年经历：别人家的孩子                                 │
│    - 少年经历：辩论赛失利                                   │
│    - 青年经历：实习被批评                                   │
│    - 角色现状：广告公司设计师                               │
├─────────────────────────────────────────────────────────────┤
│ 🎭 策略维度 (actor_prompt - psychological_profile)         │
│    - 动机共情：强调付出和专业精神                           │
│    - 情感共情：强调喜悦和释放感                             │
│    - 认知共情：强调职业自信提升                             │
└─────────────────────────────────────────────────────────────┘

💡 使用策略示例：

第3轮 - 对话初期：
  → 释放【阶段1：引发回忆】
  → Actor说出："这让我想起第一个项目被说'学生气太重'..."

第5轮 - AI共情浅显：
  → 调整策略：聚焦【动机共情】
  → Actor强调："我真的很努力，两个月熬了那么多夜..."

第7轮 - 需要增加深度：
  → 释放记忆：【少年经历】
  → Actor提到："以前辩论赛失利，让我一直害怕失败..."

第10轮 - 关键转折：
  → 综合转折：阶段3 + 认知共情
  → Actor表达："我意识到，这次表扬不只是运气，是我专业能力的证明..."

这样对话会更有层次感和真实性！
    """)


if __name__ == "__main__":
    print("\n🧪 增强版 Director 功能测试\n")
    
    try:
        # 测试1: 初始化
        director = test_director_enhanced_initialization()
        
        # 测试2: 释放故事阶段
        test_release_stage(director)
        
        # 测试3: 释放记忆
        test_release_memory(director)
        
        # 测试4: 调整共情策略
        test_adjust_empathy_strategy(director)
        
        # 测试5: 综合转折
        test_introduce_turning_point(director)
        
        # 测试6: 函数总结
        test_function_summary(director)
        
        # 测试7: 多维度能力展示
        test_multidimensional_control()
        
        print("\n" + "=" * 70)
        print("✅ 所有测试通过！Director 现在支持多维度控制！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

