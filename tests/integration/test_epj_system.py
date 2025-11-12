#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPJ系统完整测试（使用Mock数据）

测试EPJ三层架构的完整流程：
1. Judger填写量表
2. Orchestrator计算向量
3. Director做出决策
"""

from Benchmark.epj.vector_calculator import VectorCalculator
from Benchmark.orchestrator.epj_orchestrator import EPJOrchestrator


# ═══════════════════════════════════════════════════════════════
# Mock Judger
# ═══════════════════════════════════════════════════════════════

class MockJudger:
    """模拟Judger（用于测试）"""
    
    def __init__(self):
        self.evaluation_count = 0
    
    def fill_iedr(self, script_content):
        """模拟填写IEDR"""
        print(f"   [MockJudger] 填写IEDR量表")
        return {
            "C.1": 2,  # 中等复杂性
            "C.2": 2,  # 核心认知需求
            "A.1": 2,  # 强烈情绪
            "A.2": 1,  # 隐含情绪
            "A.3": 3,  # 最高情感优先级
            "P.1": 2,  # 低能动性
            "P.2": 3,  # 价值危机
            "P.3": 3,  # 最高动机优先级
            "reasoning": "角色在职场受到挑剔甲方的压力，情感和价值需求都很高"
        }
    
    def fill_mdep_pr(self, recent_turns):
        """模拟填写MDEP-PR（模拟逐步改善的共情）"""
        self.evaluation_count += 1
        
        print(f"   [MockJudger] 填写MDEP-PR量表（第{self.evaluation_count}次）")
        
        # 模拟共情质量逐步提升
        if self.evaluation_count == 1:
            # 第1次评估：AI共情较弱
            return {
                "C.Prog": 1, "C.Neg": 0,
                "A.Prog": 1, "A.Neg": 0,
                "P.Prog": 0, "P.Neg": 0,
                "reasoning": "AI有基本理解和验证，但动机共情不足"
            }
        elif self.evaluation_count == 2:
            # 第2次评估：AI共情改善
            return {
                "C.Prog": 2, "C.Neg": 0,
                "A.Prog": 2, "A.Neg": 0,
                "P.Prog": 1, "P.Neg": 0,
                "reasoning": "AI深度理解和共鸣，开始认可"
            }
        elif self.evaluation_count == 3:
            # 第3次评估：AI共情很好
            return {
                "C.Prog": 2, "C.Neg": 0,
                "A.Prog": 2, "A.Neg": 0,
                "P.Prog": 2, "P.Neg": 0,
                "reasoning": "AI全面共情，有效赋能"
            }
        else:
            # 后续：持续良好
            return {
                "C.Prog": 1, "C.Neg": 0,
                "A.Prog": 2, "A.Neg": 0,
                "P.Prog": 2, "P.Neg": 0,
                "reasoning": "AI共情持续良好"
            }


# ═══════════════════════════════════════════════════════════════
# Mock Director
# ═══════════════════════════════════════════════════════════════

class MockDirector:
    """模拟Director（用于测试）"""
    
    def make_epj_decision(self, state_packet, history):
        """模拟EPJ决策"""
        is_in_zone = state_packet.get('is_in_zone', False)
        is_timeout = state_packet.get('is_timeout', False)
        distance = state_packet.get('distance_to_goal', 999)
        
        if is_in_zone:
            return {
                "decision": "STOP",
                "reason": "达到目标区域",
                "termination_type": "SUCCESS"
            }
        
        if is_timeout:
            return {
                "decision": "STOP",
                "reason": "超时",
                "termination_type": "FAILURE"
            }
        
        return {
            "decision": "CONTINUE",
            "reason": f"距离目标 {distance:.2f}",
            "guidance": "继续对话"
        }


# ═══════════════════════════════════════════════════════════════
# 测试函数
# ═══════════════════════════════════════════════════════════════

def test_epj_complete_flow():
    """测试EPJ完整流程"""
    
    print("=" * 70)
    print("EPJ系统完整流程测试")
    print("=" * 70)
    
    # 初始化
    mock_judger = MockJudger()
    mock_director = MockDirector()
    epj_orch = EPJOrchestrator(mock_judger, threshold_type="high_threshold", K=3, max_turns=30)
    
    # ═══════════════════════════════════════════════════════════════
    # T=0: 初始化
    # ═══════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 70)
    print("阶段1: T=0 初始化")
    print("=" * 70)
    
    script_content = {
        "actor_prompt": "刘静，26岁，设计师...",
        "scenario": {"剧本编号": "script_001"}
    }
    
    init_result = epj_orch.initialize_at_T0(script_content)
    P_0 = init_result['P_0']
    
    print(f"\n📊 初始化结果:")
    print(f"   P_0 = {P_0}")
    print(f"   初始距离 = {init_result['initial_distance']:.2f}")
    
    # ═══════════════════════════════════════════════════════════════
    # 模拟对话循环
    # ═══════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 70)
    print("阶段2: 对话循环")
    print("=" * 70)
    
    history = []
    
    for turn in range(1, 16):
        # 模拟对话
        actor_msg = f"Actor第{turn}轮消息"
        ai_msg = f"AI第{turn}轮回复"
        
        history.append({"role": "actor", "content": actor_msg})
        history.append({"role": "test_model", "content": ai_msg})
        
        print(f"\n--- 第{turn}轮 ---")
        print(f"  Actor: {actor_msg}")
        print(f"  AI: {ai_msg}")
        
        # 检查是否应该评估
        if epj_orch.should_evaluate(turn):
            print(f"\n🔬 EPJ评估时刻（第{turn}轮）")
            
            # 模拟最近K轮
            recent_turns = [
                {"actor": f"Actor第{i}轮", "test_model": f"AI第{i}轮"}
                for i in range(max(1, turn - epj_orch.K + 1), turn + 1)
            ]
            
            # EPJ评估
            state_packet = epj_orch.evaluate_at_turn_K(recent_turns, turn)
            
            # Director决策
            decision = mock_director.make_epj_decision(state_packet, history)
            
            print(f"\n📋 EPJ决策:")
            print(f"   决策: {decision['decision']}")
            print(f"   理由: {decision['reason']}")
            
            if decision['decision'] == 'STOP':
                print(f"\n🏁 对话终止")
                print(f"   类型: {decision.get('termination_type')}")
                break
    
    # ═══════════════════════════════════════════════════════════════
    # 最终统计
    # ═══════════════════════════════════════════════════════════════
    
    print("\n" + "=" * 70)
    print("📊 最终统计")
    print("=" * 70)
    
    trajectory = epj_orch.get_trajectory()
    final_position = epj_orch.get_current_position()
    
    print(f"\n基本信息:")
    print(f"   总轮次: {turn}")
    print(f"   总评估次数: {len(trajectory) - 1}")
    print(f"   初始赤字: {P_0}")
    print(f"   最终位置: {final_position}")
    
    print(f"\n完整轨迹:")
    for point in trajectory:
        t = point['turn']
        P = point['P_t']
        v = point['v_t']
        d = point['distance']
        status = "✅" if point['in_zone'] else "⏳"
        print(f"   T={t:2d}: P={P}, v={v}, 距离={d:5.2f} {status}")
    
    print("\n" + "=" * 70)
    print("✅ EPJ系统测试完成")
    print("=" * 70)


def test_vector_progression():
    """测试向量进展的可视化"""
    
    print("\n" + "=" * 70)
    print("向量进展可视化测试")
    print("=" * 70)
    
    from Benchmark.epj.scoring import calculate_initial_deficit, calculate_increment_vector, check_in_zone
    
    # 初始赤字
    filled_iedr = {
        "C.1": 2, "C.2": 2,
        "A.1": 2, "A.2": 1, "A.3": 3,
        "P.1": 2, "P.2": 3, "P.3": 3
    }
    
    P = calculate_initial_deficit(filled_iedr)
    print(f"\nP_0 (初始) = {P}")
    
    epsilon = 1.0
    
    # 模拟进展
    print(f"\n模拟共情进展轨迹（ε={epsilon}）:")
    print(f"{'轮次':<6} {'C':>5} {'A':>5} {'P':>5} {'距离':>8} {'状态':>10}")
    print("-" * 50)
    
    for t in range(0, 31, 3):
        C, A, P_val = P
        distance = (C**2 + A**2 + P_val**2) ** 0.5
        in_zone = check_in_zone(P, epsilon)
        status = "✅ 达标" if in_zone else "⏳ 进行中"
        
        print(f"T={t:<4} {C:>5} {A:>5} {P_val:>5} {distance:>8.2f} {status:>10}")
        
        if in_zone:
            print(f"\n🎉 在第{t}轮达到目标区域！")
            break
        
        if t >= 30:
            print(f"\n⏰ 达到最大轮次")
            break
        
        # 模拟下一轮增量（逐步改善）
        if t < 9:
            v_t = (1, 2, 2)  # 早期：较慢进展
        elif t < 18:
            v_t = (2, 3, 3)  # 中期：加速进展
        else:
            v_t = (3, 4, 4)  # 后期：快速进展
        
        P = tuple(P[i] + v_t[i] for i in range(3))


if __name__ == "__main__":
    print("\n🧪 EPJ系统测试套件\n")
    
    try:
        # 测试1: 完整流程
        test_epj_complete_flow()
        
        # 测试2: 向量进展可视化
        test_vector_progression()
        
        print("\n" + "=" * 70)
        print("✅ 所有EPJ测试通过！")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

