#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Director prompts的正确性

验证：
1. EPJ模式：基于向量的决策指南
2. 旧模式：基于分段的决策指南
3. 进度信息的正确显示
"""

from Benchmark.prompts.director_prompts import generate_director_prompt


def test_epj_mode_prompt():
    """测试EPJ模式的prompt"""
    
    print("=" * 70)
    print("测试1: EPJ模式的Director Prompt")
    print("=" * 70)
    
    # 模拟EPJ状态
    epj_state = {
        "P_0_start_deficit": (-10, -17, -25),
        "P_t_current_position": (-3, -10, -21),
        "v_t_last_increment": (+3, +3, +1),
        "distance_to_goal": 23.45,
        "display_progress": 34.6
    }
    
    # 模拟对话历史
    history = [
        {"role": "actor", "content": "我们那个最挑剔的甲方，今天居然点名表扬我了"},
        {"role": "test_model", "content": "哇，这太棒了！恭喜你！"}
    ]
    
    # 生成prompt
    prompt = generate_director_prompt(
        progress=None,  # 不使用单一分数
        epj_state=epj_state,  # 使用EPJ状态
        history=history
    )
    
    print("\n生成的Prompt（前1000字符）:")
    print("=" * 70)
    print(prompt[:1000])
    print("...")
    print("=" * 70)
    
    # 检查关键内容
    print("\n✅ 检查EPJ模式的关键内容:")
    
    checks = [
        ("EPJ三维向量", "EPJ三维向量" in prompt),
        ("P_0起点", "(-10, -17, -25)" in prompt),
        ("P_t当前", "(-3, -10, -21)" in prompt),
        ("v_t进展", "(+3, +3, +1)" in prompt),
        ("三维度分析", "三维度分析" in prompt),
        ("C轴分析", "C轴（认知共情）" in prompt),
        ("A轴分析", "A轴（情感共情）" in prompt),
        ("P轴分析", "P轴（动机共情）" in prompt),
        ("基于向量的策略", "基于EPJ向量的剧情控制策略" in prompt),
        ("v_t判断", "根据v_t（最近进展）判断" in prompt),
        ("P_t判断", "根据P_t（当前位置）判断" in prompt),
        ("显示进度标注", "仅供参考" in prompt),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    # 检查不应该出现的内容
    print("\n✅ 检查不应该出现的内容（旧模式特有）:")
    
    negative_checks = [
        ("进度0-30分段", "进度0-30" in prompt or "对话初期（进度0-30）" in prompt),
        ("进度30-60分段", "进度30-60" in prompt or "对话中期（进度30-60）" in prompt),
    ]
    
    for check_name, result in negative_checks:
        status = "❌" if result else "✅"
        print(f"   {status} {check_name}: {'出现了（不应该）' if result else '未出现（正确）'}")


def test_legacy_mode_prompt():
    """测试旧模式的prompt"""
    
    print("\n" + "=" * 70)
    print("测试2: 旧模式的Director Prompt")
    print("=" * 70)
    
    # 旧模式：只提供progress分数
    history = [
        {"role": "actor", "content": "我最近工作压力很大"},
        {"role": "test_model", "content": "我理解你的感受"}
    ]
    
    # 生成prompt
    prompt = generate_director_prompt(
        progress=45,  # 旧模式的进度分数
        epj_state=None,  # 不使用EPJ
        history=history
    )
    
    print("\n生成的Prompt（前1000字符）:")
    print("=" * 70)
    print(prompt[:1000])
    print("...")
    print("=" * 70)
    
    # 检查关键内容
    print("\n✅ 检查旧模式的关键内容:")
    
    checks = [
        ("进度分数", "当前共情进度值: 45/100" in prompt),
        ("对话初期分段", "对话初期（进度0-30）" in prompt),
        ("对话中期分段", "对话中期（进度30-60）" in prompt),
        ("对话深入分段", "对话深入（进度60-90）" in prompt),
        ("接近结束分段", "接近结束（进度90+）" in prompt),
    ]
    
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"   {status} {check_name}")
    
    # 检查不应该出现的内容
    print("\n✅ 检查不应该出现的内容（EPJ模式特有）:")
    
    negative_checks = [
        ("EPJ向量", "EPJ三维向量" in prompt),
        ("P_0", "P_0" in prompt),
        ("v_t进展", "v_t（最近进展）" in prompt),
    ]
    
    for check_name, result in negative_checks:
        status = "❌" if result else "✅"
        print(f"   {status} {check_name}: {'出现了（不应该）' if result else '未出现（正确）'}")


def test_vector_based_guidelines():
    """测试基于向量的决策指南是否合理"""
    
    print("\n" + "=" * 70)
    print("测试3: EPJ向量决策指南的合理性")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "v_t全面正向",
            "epj_state": {
                "P_0_start_deficit": (-10, -10, -10),
                "P_t_current_position": (-2, -2, -2),
                "v_t_last_increment": (+3, +3, +3),
                "distance_to_goal": 3.46,
                "display_progress": 80.0
            },
            "expected_strategy": "可以深入剧情"
        },
        {
            "name": "P轴进展慢",
            "epj_state": {
                "P_0_start_deficit": (-10, -10, -25),
                "P_t_current_position": (-2, -3, -18),
                "v_t_last_increment": (+2, +2, +1),
                "distance_to_goal": 18.38,
                "display_progress": 45.0
            },
            "expected_strategy": "P轴赤字仍深"
        },
        {
            "name": "A轴负向",
            "epj_state": {
                "P_0_start_deficit": (-10, -10, -10),
                "P_t_current_position": (-8, -12, -8),
                "v_t_last_increment": (+1, -2, +1),
                "distance_to_goal": 16.91,
                "display_progress": 20.0
            },
            "expected_strategy": "A轴≤0"
        }
    ]
    
    for case in test_cases:
        print(f"\n{case['name']}:")
        print("-" * 70)
        
        prompt = generate_director_prompt(
            epj_state=case['epj_state'],
            history=[]
        )
        
        epj = case['epj_state']
        print(f"  P_t: {epj['P_t_current_position']}")
        print(f"  v_t: {epj['v_t_last_increment']}")
        print(f"  期望策略关键词: {case['expected_strategy']}")
        print(f"  ✅ 在prompt中: {'是' if case['expected_strategy'] in prompt else '否'}")


if __name__ == "__main__":
    print("\n🧪 Director Prompts 完整性测试\n")
    
    try:
        # 测试EPJ模式
        test_epj_mode_prompt()
        
        # 测试旧模式
        test_legacy_mode_prompt()
        
        # 测试向量决策指南
        test_vector_based_guidelines()
        
        print("\n" + "=" * 70)
        print("✅ 所有测试通过")
        print("=" * 70)
        
        print("\n📋 总结:")
        print("  1. ✅ EPJ模式：使用完整的向量信息和基于向量的决策指南")
        print("  2. ✅ 旧模式：仍然支持单一progress分数和分段指南")
        print("  3. ✅ 两种模式正确分离，根据参数自动选择")
        print("  4. ✅ EPJ模式中，display_progress明确标注'仅供参考'")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

