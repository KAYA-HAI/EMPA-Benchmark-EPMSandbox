#!/usr/bin/env python3
"""
分析轴分布、难度分布、情境分布之间的关联性
"""

import json
import math
from collections import defaultdict
from typing import Dict, List

def calculate_euclidean_distance(c: float, a: float, p: float) -> float:
    return math.sqrt(c**2 + a**2 + p**2)

def determine_dominant_axis(c: float, a: float, p: float) -> str:
    abs_c, abs_a, abs_p = abs(c), abs(a), abs(p)
    max_deficit = max(abs_c, abs_a, abs_p)
    if abs_c == max_deficit:
        return 'C'
    elif abs_a == max_deficit:
        return 'A'
    else:
        return 'P'

def determine_difficulty(total_deficit: float) -> str:
    if total_deficit < 28:
        return '较易'
    elif total_deficit < 32:
        return '中等'
    elif total_deficit < 36:
        return '困难'
    else:
        return '极难'

def extract_primary_category(labels: str) -> str:
    if not labels:
        return '未分类'
    parts = labels.split(',')
    if len(parts) > 0:
        category = parts[0].split('-')[0]
        return category
    return '未分类'

def load_and_prepare_data():
    """加载并准备数据"""
    # 读取IEDR结果
    with open('/Users/shiya/Desktop/Benchmark-test/results/iedr_batch_results.json', 'r', encoding='utf-8') as f:
        iedr_data = json.load(f)
    
    # 读取分类结果
    with open('/Users/shiya/Desktop/Benchmark-test/Benchmark/topics/data/classification_results.json', 'r', encoding='utf-8') as f:
        classification_data = json.load(f)
    
    classification_dict = {item['script_id']: item['labels'] for item in classification_data}
    
    cases = []
    for item in iedr_data:
        if 'P_0' in item and item.get('status') == 'success':
            p_0 = item['P_0']
            c_deficit = p_0.get('C', 0)
            a_deficit = p_0.get('A', 0)
            p_deficit = p_0.get('P', 0)
            total_deficit = p_0.get('total', 0)
            
            if total_deficit == 0:
                total_deficit = calculate_euclidean_distance(c_deficit, a_deficit, p_deficit)
            
            dominant_axis = determine_dominant_axis(c_deficit, a_deficit, p_deficit)
            difficulty = determine_difficulty(total_deficit)
            labels = classification_dict.get(item['script_id'], '')
            category = extract_primary_category(labels)
            
            cases.append({
                'script_id': item['script_id'],
                'dominant_axis': dominant_axis,
                'difficulty': difficulty,
                'category': category,
                'total_deficit': total_deficit
            })
    
    return cases

def analyze_axis_difficulty_correlation(cases: List[Dict]):
    """分析轴与难度的关联"""
    print("=" * 60)
    print("【维度1 × 维度2】轴分布 vs 难度分布的关联性分析")
    print("=" * 60)
    
    # 统计每个轴的难度分布
    axis_difficulty = defaultdict(lambda: defaultdict(int))
    axis_total = defaultdict(int)
    
    for case in cases:
        axis = case['dominant_axis']
        diff = case['difficulty']
        axis_difficulty[axis][diff] += 1
        axis_total[axis] += 1
    
    print("\n各轴的难度分布：\n")
    
    difficulty_order = ['较易', '中等', '困难', '极难']
    
    # 打印表头
    print(f"{'轴':<5}", end='')
    for diff in difficulty_order:
        print(f"{diff:>8}", end='')
    print(f"{'总计':>8}{'平均难度':>12}")
    print("-" * 60)
    
    # 计算全局难度分布（作为基准）
    global_difficulty = defaultdict(int)
    for case in cases:
        global_difficulty[case['difficulty']] += 1
    
    print(f"{'全局':<5}", end='')
    for diff in difficulty_order:
        count = global_difficulty[diff]
        pct = count / len(cases) * 100
        print(f"{count:>4}({pct:>4.1f}%)", end='')
    avg_global = sum(case['total_deficit'] for case in cases) / len(cases)
    print(f"{len(cases):>8}{avg_global:>12.2f}")
    print("-" * 60)
    
    # 打印每个轴的分布
    axis_avg_difficulty = {}
    for axis in ['C', 'A', 'P']:
        print(f"{axis+'轴':<5}", end='')
        total = axis_total[axis]
        axis_cases = [c for c in cases if c['dominant_axis'] == axis]
        avg_diff = sum(c['total_deficit'] for c in axis_cases) / len(axis_cases) if axis_cases else 0
        axis_avg_difficulty[axis] = avg_diff
        
        for diff in difficulty_order:
            count = axis_difficulty[axis][diff]
            pct = count / total * 100 if total > 0 else 0
            print(f"{count:>4}({pct:>4.1f}%)", end='')
        print(f"{total:>8}{avg_diff:>12.2f}")
    
    print("\n⚠️  关联性评估：")
    print(f"  - C轴平均难度: {axis_avg_difficulty['C']:.2f} (偏{'低' if axis_avg_difficulty['C'] < avg_global else '高'} {abs(axis_avg_difficulty['C'] - avg_global):.2f})")
    print(f"  - A轴平均难度: {axis_avg_difficulty['A']:.2f} (偏{'低' if axis_avg_difficulty['A'] < avg_global else '高'} {abs(axis_avg_difficulty['A'] - avg_global):.2f})")
    print(f"  - P轴平均难度: {axis_avg_difficulty['P']:.2f} (偏{'低' if axis_avg_difficulty['P'] < avg_global else '高'} {abs(axis_avg_difficulty['P'] - avg_global):.2f})")
    
    # 判断关联强度
    max_deviation = max(abs(axis_avg_difficulty[axis] - avg_global) for axis in ['C', 'A', 'P'])
    if max_deviation > 2:
        print(f"\n  🔴 **强关联警告**: 最大偏差 {max_deviation:.2f} > 2，轴与难度存在显著关联！")
        print("     这意味着强制按轴1:1:1抽样会导致难度分布偏离目标。")
    elif max_deviation > 1:
        print(f"\n  🟡 **中度关联**: 最大偏差 {max_deviation:.2f} > 1，存在一定关联。")
    else:
        print(f"\n  ✅ **弱关联**: 最大偏差 {max_deviation:.2f} < 1，关联性较弱。")

def analyze_axis_category_correlation(cases: List[Dict]):
    """分析轴与情境的关联"""
    print("\n\n" + "=" * 60)
    print("【维度1 × 维度3】轴分布 vs 情境分布的关联性分析")
    print("=" * 60)
    
    # 统计每个轴的情境分布
    axis_category = defaultdict(lambda: defaultdict(int))
    category_total = defaultdict(int)
    
    for case in cases:
        axis = case['dominant_axis']
        cat = case['category']
        axis_category[axis][cat] += 1
        category_total[cat] += 1
    
    print("\n各情境在三轴的分布：\n")
    print(f"{'情境':<12} {'总数':>6}  {'C轴':>12}  {'A轴':>12}  {'P轴':>12}")
    print("-" * 60)
    
    # 按总数排序
    sorted_categories = sorted(category_total.items(), key=lambda x: x[1], reverse=True)
    
    max_imbalance = 0
    imbalanced_categories = []
    
    for cat, total in sorted_categories:
        c_count = axis_category['C'][cat]
        a_count = axis_category['A'][cat]
        p_count = axis_category['P'][cat]
        
        c_pct = c_count / total * 100
        a_pct = a_count / total * 100
        p_pct = p_count / total * 100
        
        print(f"{cat:<12} {total:>6}  {c_count:>4}({c_pct:>4.1f}%)  {a_count:>4}({a_pct:>4.1f}%)  {p_count:>4}({p_pct:>4.1f}%)", end='')
        
        # 计算不平衡度（最大比例 - 最小比例）
        imbalance = max(c_pct, a_pct, p_pct) - min(c_pct, a_pct, p_pct)
        max_imbalance = max(max_imbalance, imbalance)
        
        if imbalance > 50:
            dominant = 'C' if c_pct == max(c_pct, a_pct, p_pct) else ('A' if a_pct == max(c_pct, a_pct, p_pct) else 'P')
            print(f"  ⚠️  {dominant}轴主导")
            imbalanced_categories.append((cat, dominant, imbalance))
        else:
            print()
    
    print("\n⚠️  关联性评估：")
    if max_imbalance > 60:
        print(f"  🔴 **强关联警告**: 最大不平衡度 {max_imbalance:.1f}% > 60%")
        print(f"     以下情境存在严重的轴偏向：")
        for cat, dominant, imb in imbalanced_categories:
            print(f"       - {cat}: {dominant}轴主导 (不平衡度{imb:.1f}%)")
        print("     这意味着强制按轴1:1:1抽样会导致某些情境被过度/不足代表。")
    elif max_imbalance > 40:
        print(f"  🟡 **中度关联**: 最大不平衡度 {max_imbalance:.1f}% > 40%")
        print(f"     部分情境存在轴偏向，但影响可控。")
    else:
        print(f"  ✅ **弱关联**: 最大不平衡度 {max_imbalance:.1f}% < 40%，关联性较弱。")

def analyze_difficulty_category_correlation(cases: List[Dict]):
    """分析难度与情境的关联"""
    print("\n\n" + "=" * 60)
    print("【维度2 × 维度3】难度分布 vs 情境分布的关联性分析")
    print("=" * 60)
    
    # 统计每个情境的难度分布
    category_difficulty = defaultdict(lambda: defaultdict(int))
    category_total = defaultdict(int)
    
    for case in cases:
        cat = case['category']
        diff = case['difficulty']
        category_difficulty[cat][diff] += 1
        category_total[cat] += 1
    
    print("\n各情境的难度分布：\n")
    
    difficulty_order = ['较易', '中等', '困难', '极难']
    print(f"{'情境':<12} {'总数':>6}  ", end='')
    for diff in difficulty_order:
        print(f"{diff:>10}", end='')
    print(f"{'平均难度':>10}")
    print("-" * 70)
    
    # 全局平均难度
    avg_global = sum(case['total_deficit'] for case in cases) / len(cases)
    
    # 按总数排序
    sorted_categories = sorted(category_total.items(), key=lambda x: x[1], reverse=True)
    
    max_deviation = 0
    
    for cat, total in sorted_categories:
        print(f"{cat:<12} {total:>6}  ", end='')
        
        cat_cases = [c for c in cases if c['category'] == cat]
        avg_diff = sum(c['total_deficit'] for c in cat_cases) / len(cat_cases) if cat_cases else 0
        
        deviation = abs(avg_diff - avg_global)
        max_deviation = max(max_deviation, deviation)
        
        for diff in difficulty_order:
            count = category_difficulty[cat][diff]
            pct = count / total * 100 if total > 0 else 0
            print(f"{count:>3}({pct:>4.1f}%)", end='')
        
        print(f"{avg_diff:>10.2f}", end='')
        if deviation > 2:
            print(f"  ⚠️  偏{'高' if avg_diff > avg_global else '低'}{deviation:.1f}")
        else:
            print()
    
    print("\n⚠️  关联性评估：")
    if max_deviation > 3:
        print(f"  🔴 **强关联警告**: 最大难度偏差 {max_deviation:.2f} > 3")
        print("     某些情境天然更难/更容易，强制难度配额可能导致情境分布失真。")
    elif max_deviation > 2:
        print(f"  🟡 **中度关联**: 最大难度偏差 {max_deviation:.2f} > 2")
    else:
        print(f"  ✅ **弱关联**: 最大难度偏差 {max_deviation:.2f} < 2，关联性较弱。")

def analyze_sampling_impact():
    """分析分层抽样的影响"""
    print("\n\n" + "=" * 60)
    print("【抽样策略评估】")
    print("=" * 60)
    
    print("\n当前抽样策略：")
    print("  1️⃣  第一优先级：轴均衡 (C:A:P = 1:1:1) - 强制配额")
    print("  2️⃣  第二优先级：难度分布 (较易20%:中等40%:困难30%:极难10%) - 嵌套在轴内")
    print("  3️⃣  第三优先级：情境多样性 - 软约束优化")
    
    print("\n⚠️  存在的问题：")
    print("  - 如果轴与难度强关联 → 难度分布会偏离目标")
    print("  - 如果轴与情境强关联 → 情境分布会失真")
    print("  - 如果难度与情境强关联 → 可能无法同时满足两个配额")
    
    print("\n💡 替代方案：")
    print("  【方案A】保持当前策略")
    print("    - 优点：保证轴均衡（最重要的评估维度）")
    print("    - 缺点：其他维度可能失真")
    print("    - 适用：当轴均衡是首要目标时")
    
    print("\n  【方案B】多目标优化抽样")
    print("    - 同时优化三个维度的KL散度")
    print("    - 优点：整体最优")
    print("    - 缺点：实现复杂，可能无法保证任何一个维度的严格配额")
    
    print("\n  【方案C】分块随机抽样")
    print("    - 先按轴×难度×情境创建27个（3×3×3）单元格")
    print("    - 从每个单元格按比例抽取")
    print("    - 优点：最小化关联性影响")
    print("    - 缺点：某些单元格可能为空")

def main():
    print("\n" + "=" * 60)
    print("三维分层抽样的关联性分析")
    print("=" * 60)
    
    cases = load_and_prepare_data()
    print(f"\n✅ 已加载 {len(cases)} 个案例")
    
    # 分析三组关联性
    analyze_axis_difficulty_correlation(cases)
    analyze_axis_category_correlation(cases)
    analyze_difficulty_category_correlation(cases)
    
    # 评估抽样策略
    analyze_sampling_impact()
    
    print("\n" + "=" * 60)
    print("✅ 分析完成")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()

