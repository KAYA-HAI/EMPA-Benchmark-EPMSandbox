#!/usr/bin/env python3
"""
分析EPM参数的分布，评估是否应该作为抽样维度
"""

import json
import numpy as np
from collections import defaultdict

def load_iedr_data():
    with open('/Users/shiya/Desktop/Benchmark-test/results/iedr_batch_results.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_epm_parameters():
    print("=" * 70)
    print("EPM参数分布分析")
    print("=" * 70)
    
    iedr_data = load_iedr_data()
    
    # 收集EPM参数
    epm_params = {
        'P_0_norm': [],
        'epsilon_distance': [],
        'epsilon_direction': [],
        'epsilon_energy': [],
        'alpha': [],
        'v_star_0_C': [],
        'v_star_0_A': [],
        'v_star_0_P': []
    }
    
    for item in iedr_data:
        if 'epm' in item and item.get('status') == 'success':
            epm = item['epm']
            epm_params['P_0_norm'].append(epm.get('P_0_norm', 0))
            epm_params['epsilon_distance'].append(epm.get('epsilon_distance', 0))
            epm_params['epsilon_direction'].append(epm.get('epsilon_direction', 0))
            epm_params['epsilon_energy'].append(epm.get('epsilon_energy', 0))
            epm_params['alpha'].append(epm.get('alpha', 0))
            
            v_star_0 = epm.get('v_star_0', [0, 0, 0])
            epm_params['v_star_0_C'].append(v_star_0[0])
            epm_params['v_star_0_A'].append(v_star_0[1])
            epm_params['v_star_0_P'].append(v_star_0[2])
    
    print(f"\n✅ 已加载 {len(epm_params['P_0_norm'])} 个案例的EPM数据\n")
    
    # 统计分析
    print(f"{'参数':<20} {'均值':>10} {'中位数':>10} {'标准差':>10} {'最小值':>10} {'最大值':>10} {'变异系数':>10}")
    print("-" * 70)
    
    for param, values in epm_params.items():
        if len(values) > 0:
            arr = np.array(values)
            mean = np.mean(arr)
            median = np.median(arr)
            std = np.std(arr)
            min_val = np.min(arr)
            max_val = np.max(arr)
            cv = std / mean if mean != 0 else 0  # 变异系数
            
            print(f"{param:<20} {mean:>10.4f} {median:>10.4f} {std:>10.4f} {min_val:>10.4f} {max_val:>10.4f} {cv:>10.4f}")
    
    # 分析epsilon参数的分布特征
    print("\n" + "=" * 70)
    print("EPM参数分布特征分析")
    print("=" * 70)
    
    # 1. Alpha分布
    print("\n【Alpha参数】")
    alpha_values = epm_params['alpha']
    unique_alphas = set(alpha_values)
    print(f"唯一值数量: {len(unique_alphas)}")
    if len(unique_alphas) <= 10:
        alpha_counts = defaultdict(int)
        for a in alpha_values:
            alpha_counts[a] += 1
        print("分布:")
        for a, count in sorted(alpha_counts.items()):
            print(f"  alpha={a}: {count}个 ({count/len(alpha_values)*100:.1f}%)")
    
    # 2. Epsilon参数的区分度
    print("\n【Epsilon参数的区分度】")
    
    epsilon_dist = np.array(epm_params['epsilon_distance'])
    epsilon_dir = np.array(epm_params['epsilon_direction'])
    epsilon_energy = np.array(epm_params['epsilon_energy'])
    
    # 检查是否所有epsilon都相同
    dist_unique = len(set(epsilon_dist))
    dir_unique = len(set(epsilon_dir))
    energy_unique = len(set(epsilon_energy))
    
    print(f"epsilon_distance: {dist_unique}个不同值 (变异系数: {np.std(epsilon_dist)/np.mean(epsilon_dist):.4f})")
    print(f"epsilon_direction: {dir_unique}个不同值 (变异系数: {np.std(epsilon_dir)/np.mean(epsilon_dir):.4f})")
    print(f"epsilon_energy: {energy_unique}个不同值 (变异系数: {np.std(epsilon_energy)/np.mean(epsilon_energy):.4f})")
    
    # 3. v_star_0向量的分布
    print("\n【v_star_0 最优向量分布】")
    v_c = np.array(epm_params['v_star_0_C'])
    v_a = np.array(epm_params['v_star_0_A'])
    v_p = np.array(epm_params['v_star_0_P'])
    
    print(f"C分量: 均值{np.mean(v_c):.4f}, 标准差{np.std(v_c):.4f}, 变异系数{np.std(v_c)/np.mean(v_c):.4f}")
    print(f"A分量: 均值{np.mean(v_a):.4f}, 标准差{np.std(v_a):.4f}, 变异系数{np.std(v_a)/np.mean(v_a):.4f}")
    print(f"P分量: 均值{np.mean(v_p):.4f}, 标准差{np.std(v_p):.4f}, 变异系数{np.std(v_p)/np.mean(v_p):.4f}")
    
    # 4. 分析v_star_0与主导轴的关系
    print("\n【v_star_0与主导轴的关系】")
    
    # 重新加载数据以获取主导轴信息
    from analyze_correlations import determine_dominant_axis
    
    axis_v_star = {'C': [], 'A': [], 'P': []}
    
    for item in iedr_data:
        if 'P_0' in item and 'epm' in item and item.get('status') == 'success':
            p_0 = item['P_0']
            axis = determine_dominant_axis(p_0['C'], p_0['A'], p_0['P'])
            v_star = item['epm'].get('v_star_0', [0, 0, 0])
            axis_v_star[axis].append(v_star)
    
    for axis in ['C', 'A', 'P']:
        if len(axis_v_star[axis]) > 0:
            vectors = np.array(axis_v_star[axis])
            avg_vector = np.mean(vectors, axis=0)
            print(f"{axis}轴主导案例的平均v_star_0: [{avg_vector[0]:.4f}, {avg_vector[1]:.4f}, {avg_vector[2]:.4f}]")
    
    # 5. 评估是否应该作为抽样维度
    print("\n" + "=" * 70)
    print("【是否应该将EPM参数作为抽样维度？】")
    print("=" * 70)
    
    # 判断标准
    cv_threshold = 0.15  # 变异系数阈值
    unique_threshold = 20  # 唯一值数量阈值
    
    recommendations = []
    
    # Alpha
    if len(unique_alphas) == 1:
        print("\n❌ Alpha参数:")
        print(f"   - 所有案例的alpha值相同 (alpha={list(unique_alphas)[0]})")
        print("   - 结论: **不应该**作为抽样维度（无区分度）")
    else:
        alpha_cv = np.std(alpha_values) / np.mean(alpha_values)
        if alpha_cv > cv_threshold:
            print("\n✅ Alpha参数:")
            print(f"   - 变异系数{alpha_cv:.4f} > {cv_threshold}")
            print("   - 结论: **可以考虑**作为抽样维度")
            recommendations.append("alpha")
    
    # Epsilon参数
    epsilon_cvs = {
        'epsilon_distance': np.std(epsilon_dist) / np.mean(epsilon_dist),
        'epsilon_direction': np.std(epsilon_dir) / np.mean(epsilon_dir),
        'epsilon_energy': np.std(epsilon_energy) / np.mean(epsilon_energy)
    }
    
    print("\n❓ Epsilon参数:")
    for param, cv in epsilon_cvs.items():
        if cv < 0.01:
            print(f"   - {param}: 变异系数{cv:.4f} < 0.01 (几乎无变化)")
        else:
            print(f"   - {param}: 变异系数{cv:.4f}")
    
    if all(cv < 0.01 for cv in epsilon_cvs.values()):
        print("   - 结论: **不建议**作为抽样维度（变化太小，可能是固定参数）")
    else:
        print("   - 结论: 需要结合业务语义判断")
    
    # v_star_0
    v_star_cvs = {
        'v_star_0_C': np.std(v_c) / np.mean(v_c),
        'v_star_0_A': np.std(v_a) / np.mean(v_a),
        'v_star_0_P': np.std(v_p) / np.mean(v_p)
    }
    
    print("\n✅ v_star_0向量:")
    for component, cv in v_star_cvs.items():
        print(f"   - {component}: 变异系数{cv:.4f}")
    
    if any(cv > cv_threshold for cv in v_star_cvs.values()):
        print("   - 结论: **值得考虑**作为抽样维度")
        print("   - v_star_0反映了初始最优共情向量，不同案例可能需要不同的共情策略")
        recommendations.append("v_star_0_balance")
    
    # 最终建议
    print("\n" + "=" * 70)
    print("【最终建议】")
    print("=" * 70)
    
    if len(recommendations) == 0:
        print("\n❌ **不建议**将EPM参数作为抽样维度")
        print("   原因:")
        print("   - EPM参数的变异性较低或为固定值")
        print("   - 无法提供有效的区分度")
        print("\n✅ **建议**保持当前三维抽样策略:")
        print("   - 维度1: C-A-P轴均衡")
        print("   - 维度2: 难度分布")
        print("   - 维度3: 情境多样性")
    else:
        print("\n✅ **可以考虑**将以下EPM参数作为抽样维度:")
        for rec in recommendations:
            print(f"   - {rec}")
        
        if 'v_star_0_balance' in recommendations:
            print("\n💡 **具体建议 - v_star_0均衡**:")
            print("   可以定义一个新的维度：")
            print("   - v_star_0主导方向: 哪个分量最大（C_dominant, A_dominant, P_dominant）")
            print("   - 这反映了案例的'理想共情策略'偏向")
            print("   - 可以确保测试集覆盖不同的共情策略需求")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    analyze_epm_parameters()

