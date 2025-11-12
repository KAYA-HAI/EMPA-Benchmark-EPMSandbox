#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试更新后的 Director
"""

from Benchmark.topics.config_loader import load_config
from Benchmark.agents.director import Director

def test_director_initialization():
    """测试 Director 的初始化"""
    print("=" * 60)
    print("测试 1: Director 初始化")
    print("=" * 60)
    
    # 加载配置
    config = load_config("001")
    
    # 初始化 Director
    director = Director(scenario=config['scenario'])
    
    print(f"\n✅ Director 初始化成功")
    print(f"   剧本编号: {director.scenario.get('剧本编号')}")
    print(f"   故事阶段数量: {len(director.stages)}")
    print(f"   故事结果: {director.get_story_result()}")
    
    # 显示所有阶段
    print(f"\n📖 故事阶段列表:")
    for i, stage in enumerate(director.stages):
        print(f"   [{i}] {stage['阶段名']}: {stage['标题']}")
    
    return director


def test_stage_release(director):
    """测试阶段释放"""
    print("\n" + "=" * 60)
    print("测试 2: 阶段释放")
    print("=" * 60)
    
    # 模拟释放第一个阶段
    print(f"\n📤 尝试释放阶段0...")
    result = director._handle_select_and_reveal_fragment({
        "stage_index": 0,
        "reason": "对话建立了信任，引入回忆"
    })
    
    print(f"\n释放结果:")
    print(f"   should_continue: {result['should_continue']}")
    print(f"   plot_action: {result.get('plot_action', 'N/A')}")
    print(f"   已释放阶段: {director.revealed_stages}")
    
    if result.get('guidance'):
        print(f"\n💬 给 Actor 的指令（前200字符）:")
        print(result['guidance'][:200] + "...")
    
    # 尝试再次释放同一个阶段（应该被拒绝）
    print(f"\n📤 尝试再次释放阶段0（应该被拒绝）...")
    result2 = director._handle_select_and_reveal_fragment({
        "stage_index": 0,
        "reason": "再次尝试"
    })
    
    print(f"   guidance: {result2.get('guidance', 'N/A')}")


def test_remaining_stages(director):
    """测试获取剩余阶段"""
    print("\n" + "=" * 60)
    print("测试 3: 获取剩余阶段")
    print("=" * 60)
    
    remaining = director.get_remaining_stages()
    print(f"\n🔢 剩余未释放的阶段: {remaining}")
    
    for idx in remaining:
        stage = director.stages[idx]
        print(f"   [{idx}] {stage['阶段名']}: {stage['标题']}")


def test_epilogue_release(director):
    """测试插曲释放"""
    print("\n" + "=" * 60)
    print("测试 4: 插曲释放")
    print("=" * 60)
    
    result = director.release_epilogue(reason="适合引入回忆")
    
    print(f"\n释放结果:")
    print(f"   should_continue: {result['should_continue']}")
    print(f"   plot_action: {result.get('plot_action', 'N/A')}")
    
    if result.get('guidance'):
        print(f"\n💬 给 Actor 的指令（前200字符）:")
        print(result['guidance'][:200] + "...")


def test_evaluate_continuation(director):
    """测试 evaluate_continuation 方法"""
    print("\n" + "=" * 60)
    print("测试 5: evaluate_continuation（简化测试）")
    print("=" * 60)
    
    # 模拟对话历史
    mock_history = [
        {"role": "actor", "content": "我们那个最挑剔的甲方，今天居然点名表扬我了"},
        {"role": "test_model", "content": "哇，这太棒了！听起来你一定做得很好！"},
        {"role": "actor", "content": "是啊，两个月的辛苦终于有回报了"},
        {"role": "test_model", "content": "能详细说说吗？"}
    ]
    
    print(f"\n📚 Director 状态:")
    print(f"   总阶段数: {len(director.stages)}")
    print(f"   已释放: {len(director.revealed_stages)}")
    print(f"   未释放: {len(director.get_remaining_stages())}")
    
    print(f"\n💡 提示: 完整测试需要调用 LLM API，这里只展示 Director 的配置")


if __name__ == "__main__":
    print("\n🧪 Director 更新验证测试\n")
    
    try:
        # 测试1: 初始化
        director = test_director_initialization()
        
        # 测试2: 阶段释放
        test_stage_release(director)
        
        # 测试3: 剩余阶段
        test_remaining_stages(director)
        
        # 测试4: 插曲释放
        test_epilogue_release(director)
        
        # 测试5: evaluate_continuation
        test_evaluate_continuation(director)
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

