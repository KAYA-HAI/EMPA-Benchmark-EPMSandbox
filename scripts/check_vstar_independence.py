#!/usr/bin/env python3
"""
检查v_star_0是否与P_0主导轴独立
"""

import json
import numpy as np

def load_data():
    with open('/Users/shiya/Desktop/Benchmark-test/results/iedr_batch_results.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def determine_dominant(values):
    """确定三个值中哪个最大"""
    max_idx = np.argmax(np.abs(values))
    return ['C', 'A', 'P'][max_idx]

def main():
    print("=" * 70)
    print("v_star_0主导方向 vs P_0主导轴 一致性分析")
    print("=" * 70)
    
    iedr_data = load_data()
    
    # 统计一致性
    consistent = 0
    inconsistent = 0
    inconsistent_cases = []
    
    for item in iedr_data:
        if 'P_0' in item and 'epm' in item and item.get('status') == 'success':
            p_0 = item['P_0']
            epm = item['epm']
            
            # P_0主导轴
            p0_dominant = determine_dominant([p_0['C'], p_0['A'], p_0['P']])
            
            # v_star_0主导方向
            v_star_0 = epm.get('v_star_0', [0, 0, 0])
            vstar_dominant = determine_dominant(v_star_0)
            
            if p0_dominant == vstar_dominant:
                consistent += 1
            else:
                inconsistent += 1
                inconsistent_cases.append({
                    'script_id': item['script_id'],
                    'P_0': [p_0['C'], p_0['A'], p_0['P']],
                    'P_0_dominant': p0_dominant,
                    'v_star_0': v_star_0,
                    'vstar_dominant': vstar_dominant
                })
    
    total = consistent + inconsistent
    consistency_rate = consistent / total * 100
    
    print(f"\n总案例数: {total}")
    print(f"一致案例: {consistent} ({consistency_rate:.1f}%)")
    print(f"不一致案例: {inconsistent} ({100-consistency_rate:.1f}%)")
    
    print("\n" + "=" * 70)
    print("【结论】")
    print("=" * 70)
    
    if consistency_rate > 95:
        print("\n❌ **v_star_0与P_0主导轴高度一致** (>95%)")
        print("\n结论:")
        print("  - v_star_0主导方向与P_0主导轴**几乎完全相同**")
        print("  - **不应该**将v_star_0作为独立的抽样维度")
        print("  - 这会导致维度冗余，无法增加测试覆盖度")
        print("\n✅ **建议保持当前三维抽样策略**:")
        print("  - 维度1: C-A-P轴均衡 (基于P_0)")
        print("  - 维度2: 难度分布 (基于总赤字)")
        print("  - 维度3: 情境多样性 (基于话题标签)")
    elif consistency_rate > 80:
        print("\n⚠️  **v_star_0与P_0主导轴较一致** (80-95%)")
        print(f"\n有 {inconsistent} 个案例 ({100-consistency_rate:.1f}%) 的v_star_0主导方向与P_0主导轴不同")
        print("\n结论:")
        print("  - 存在一定独立性，但关联性仍然很强")
        print("  - 是否作为抽样维度**取决于业务目标**")
        print("\n💡 如果您的EPM评估关注'最优策略'与'实际需求'的偏差:")
        print("  - 可以考虑增加v_star_0作为第四维度")
        print("  - 确保测试集包含'策略一致'和'策略不一致'的案例")
    else:
        print("\n✅ **v_star_0与P_0主导轴独立性较强** (<80%)")
        print(f"\n有 {inconsistent} 个案例 ({100-consistency_rate:.1f}%) 的v_star_0主导方向与P_0主导轴不同")
        print("\n结论:")
        print("  - v_star_0提供了与P_0不同的视角")
        print("  - **建议**将v_star_0作为第四个抽样维度")
    
    # 展示部分不一致案例
    if len(inconsistent_cases) > 0:
        print("\n" + "=" * 70)
        print(f"【不一致案例示例】(前10个)")
        print("=" * 70)
        print(f"\n{'Script ID':<15} {'P_0主导':<10} {'v*主导':<10} {'P_0向量':<25} {'v_star_0向量':<25}")
        print("-" * 70)
        
        for case in inconsistent_cases[:10]:
            p0_str = f"[{case['P_0'][0]:.1f}, {case['P_0'][1]:.1f}, {case['P_0'][2]:.1f}]"
            vstar_str = f"[{case['v_star_0'][0]:.3f}, {case['v_star_0'][1]:.3f}, {case['v_star_0'][2]:.3f}]"
            print(f"{case['script_id']:<15} {case['P_0_dominant']:<10} {case['vstar_dominant']:<10} {p0_str:<25} {vstar_str:<25}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()

