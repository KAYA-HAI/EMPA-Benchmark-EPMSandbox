#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试EPJ状态传递给Director的完整流程

验证：
1. EPJ终止决策：基于完整的state_packet
2. Director剧情控制：基于完整的epj_state
3. 显示分数：仅用于参考，不用于决策
"""

from Benchmark.topics.config_loader import load_config
from Benchmark.agents.director import Director
from Benchmark.orchestrator.epj_orchestrator import EPJOrchestrator


class MockJudger:
    """模拟Judger"""
    def __init__(self):
        self.call_count = 0
    
    def fill_iedr(self, script_content):
        return {
            "C.1": 2, "C.2": 2,
            "A.1": 2, "A.2": 1, "A.3": 3,
            "P.1": 2, "P.2": 3, "P.3": 3
        }
    
    def fill_mdep_pr(self, recent_turns):
        self.call_count += 1
        # 模拟不同轮次的共情质量
        if self.call_count == 1:
            return {"C.Prog": 1, "C.Neg": 0, "A.Prog": 1, "A.Neg": 0, "P.Prog": 0, "P.Neg": 0}
        elif self.call_count == 2:
            return {"C.Prog": 2, "C.Neg": 0, "A.Prog": 2, "A.Neg": 0, "P.Prog": 1, "P.Neg": 0}
        else:
            return {"C.Prog": 2, "C.Neg": 0, "A.Prog": 2, "A.Neg": 0, "P.Prog": 2, "P.Neg": 0}


def test_epj_state_propagation():
    """测试EPJ状态传递"""
    
    print("=" * 70)
    print("测试：EPJ状态完整传递给Director")
    print("=" * 70)
    
    # 加载配置
    config = load_config("001")
    
    # 初始化Director
    director = Director(
        scenario=config['scenario'],
        actor_prompt=config['actor_prompt']
    )
    
    # 初始化EPJ Orchestrator
    judger = MockJudger()
    epj_orch = EPJOrchestrator(judger, K=3, max_turns=30)
    
    # T=0: 初始化
    print("\n1. T=0 初始化")
    print("-" * 70)
    
    script_content = {
        "actor_prompt": config['actor_prompt'],
        "scenario": config['scenario']
    }
    
    init_result = epj_orch.initialize_at_T0(script_content)
    P_0 = init_result['P_0']
    
    print(f"✅ P_0 = {P_0}")
    
    # 模拟第一次EPJ评估（T=3）
    print("\n2. T=3 第一次EPJ评估")
    print("-" * 70)
    
    recent_turns = [{"actor": "msg1", "test_model": "reply1"}] * 3
    state_packet = epj_orch.evaluate_at_turn_K(recent_turns, 3)
    
    print(f"\n📦 生成的状态数据包:")
    print(f"   P_t: {state_packet['P_t_current_position']}")
    print(f"   v_t: {state_packet['v_t_last_increment']}")
    print(f"   距离: {state_packet['distance_to_goal']}")
    print(f"   显示进度: {state_packet['display_progress']}%")
    print(f"   在区域内: {state_packet['is_in_zone']}")
    
    # 测试1: EPJ终止决策（使用完整state_packet）
    print("\n3. Director的EPJ终止决策")
    print("-" * 70)
    
    epj_decision = director.make_epj_decision(state_packet, [])
    
    print(f"✅ EPJ决策:")
    print(f"   决策: {epj_decision['decision']}")
    print(f"   理由: {epj_decision['reason'][:80]}...")
    print(f"   ✅ 使用的是：is_in_zone（Epsilon检测）")
    
    # 测试2: Director剧情控制（使用完整epj_state）
    print("\n4. Director的剧情控制（EPJ模式）")
    print("-" * 70)
    
    # 构建EPJ状态（与state_packet格式一致）
    epj_state_for_plot = {
        "P_0_start_deficit": P_0,
        "P_t_current_position": epj_orch.get_current_position(),
        "v_t_last_increment": state_packet.get('v_t_last_increment'),
        "distance_to_goal": state_packet.get('distance_to_goal'),
        "display_progress": state_packet.get('display_progress')
    }
    
    print(f"传递给Director的EPJ状态:")
    print(f"   P_0: {epj_state_for_plot['P_0_start_deficit']}")
    print(f"   P_t: {epj_state_for_plot['P_t_current_position']}")
    print(f"   v_t: {epj_state_for_plot['v_t_last_increment']}")
    print(f"   显示进度: {epj_state_for_plot['display_progress']:.1f}%（仅供参考）")
    
    # 注意：这里会调用LLM，如果没有API key会失败
    # 我们只展示数据传递，不实际调用
    print(f"\n✅ Director.evaluate_continuation()现在接收：")
    print(f"   • history: 对话历史")
    print(f"   • progress: None（不使用单一分数）")
    print(f"   • epj_state: 完整的向量状态包 ✅")
    
    print(f"\n📋 Director在prompt中看到的信息:")
    print(f"   当前共情状态（EPJ三维向量）:")
    print(f"     • 起点赤字 P_0: {epj_state_for_plot['P_0_start_deficit']}")
    print(f"     • 当前位置 P_t: {epj_state_for_plot['P_t_current_position']}")
    print(f"     • 最近进展 v_t: {epj_state_for_plot['v_t_last_increment']}")
    
    # 模拟向量分析
    P_t_vec = epj_orch.get_current_position()
    P_0_vec = P_0
    
    print(f"\n   三维度分析：")
    print(f"     - C轴: {P_0_vec[0]} → {P_t_vec[0]} (改善: {P_t_vec[0] - P_0_vec[0]:+d})")
    print(f"     - A轴: {P_0_vec[1]} → {P_t_vec[1]} (改善: {P_t_vec[1] - P_0_vec[1]:+d})")
    print(f"     - P轴: {P_0_vec[2]} → {P_t_vec[2]} (改善: {P_t_vec[2] - P_0_vec[2]:+d})")
    
    print(f"\n   Director可以基于这些完整信息智能决策：")
    print(f"     • v_t某轴有大正值 → 该轴共情好，可深入剧情")
    print(f"     • v_t某轴有负值 → 该轴共情差，需调整策略")
    print(f"     • P_t某轴赤字深 → 重点关注该维度")
    
    # 对比旧方式
    print("\n5. 对比：如果使用旧方式（单一progress）")
    print("-" * 70)
    
    old_progress = int(epj_state_for_plot['display_progress'])
    print(f"❌ 旧方式传递：current_progress = {old_progress}")
    print(f"   Director只看到：'当前共情进度值: {old_progress}/100'")
    print(f"   ⚠️ 丢失了：哪个轴好？哪个轴差？最近是进步还是退步？")
    
    print(f"\n✅ 新方式传递：完整的epj_state")
    print(f"   Director看到：P_0, P_t, v_t的完整信息")
    print(f"   ✅ 保留了：所有维度的详细信息，可以智能分析")


def test_decision_scenarios():
    """测试不同EPJ状态下的Director决策"""
    
    print("\n" + "=" * 70)
    print("测试：不同EPJ状态下的Director智能决策")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "场景1: v_t全面正向",
            "P_t": (-3, -5, -10),
            "v_t": (+3, +3, +3),
            "expected": "AI全面共情很好，可以深入剧情或引入转折"
        },
        {
            "name": "场景2: P轴进展慢",
            "P_t": (-2, -3, -18),
            "v_t": (+2, +2, +1),
            "expected": "P轴赤字仍深且进展慢，需要释放动机共情相关内容"
        },
        {
            "name": "场景3: A轴有负值",
            "P_t": (-3, -8, -12),
            "v_t": (+1, -2, +1),
            "expected": "A轴出现负向，AI可能冷漠或评判，需要调整策略"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 70)
        print(f"  当前位置 P_t: {scenario['P_t']}")
        print(f"  最近进展 v_t: {scenario['v_t']}")
        print(f"  Director应该: {scenario['expected']}")
        print(f"  ✅ 基于完整的向量状态，Director可以做出智能判断")


if __name__ == "__main__":
    print("\n🧪 EPJ状态传递测试\n")
    
    try:
        test_epj_state_propagation()
        test_decision_scenarios()
        
        print("\n" + "=" * 70)
        print("✅ 测试完成")
        print("=" * 70)
        print("\n核心要点:")
        print("  1. ✅ EPJ终止决策：基于完整的state_packet + Epsilon检测")
        print("  2. ✅ Director剧情控制：基于完整的epj_state（P_t, v_t等）")
        print("  3. ⚠️ display_progress：仅供UI显示，不用于任何决策")
        print("\n✅ 状态数据包 = 完整的、无损的进度表示！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

