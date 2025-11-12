#!/usr/bin/env python3
"""
IEDR批量评估结果统计分析

分析100个剧本的IEDR评估结果，检查测试案例的分布是否有偏好
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter
from typing import Dict, List

# 配置
RESULT_FILE = Path("results/iedr_batch_results.json")

# 维度名称映射
DIMENSION_NAMES = {
    "C.1": "C.1 处境复杂性",
    "C.2": "C.2 深度",
    "C.3": "C.3 认知优先级",
    "A.1": "A.1 情绪强度",
    "A.2": "A.2 情绪可及性",
    "A.3": "A.3 情感优先级",
    "P.1": "P.1 初始能动性",
    "P.2": "P.2 价值关联度",
    "P.3": "P.3 动机优先级"
}

AXIS_NAMES = {
    "C": "C轴 (认知共情)",
    "A": "A轴 (情感共情)",
    "P": "P轴 (动机共情)"
}


def load_results():
    """加载评估结果"""
    with open(RESULT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_indicators(data: List[Dict]) -> Dict:
    """分析各指标的得分分布"""
    indicators = ["C.1", "C.2", "C.3", "A.1", "A.2", "A.3", "P.1", "P.2", "P.3"]
    analysis = {}
    
    for ind in indicators:
        scores = [item['iedr'][ind] for item in data if item['status'] == 'success']
        analysis[ind] = {
            'scores': scores,
            'distribution': Counter(scores),
            'mean': np.mean(scores),
            'std': np.std(scores),
            'median': np.median(scores),
            'min': min(scores),
            'max': max(scores)
        }
    
    return analysis


def analyze_axes(data: List[Dict]) -> Dict:
    """分析三个轴的赤字分布"""
    axes = ["C", "A", "P"]
    analysis = {}
    
    for axis in axes:
        deficits = [item['P_0'][axis] for item in data if item['status'] == 'success']
        analysis[axis] = {
            'deficits': deficits,
            'mean': np.mean(deficits),
            'std': np.std(deficits),
            'median': np.median(deficits),
            'min': min(deficits),
            'max': max(deficits)
        }
    
    return analysis


def analyze_total_deficit(data: List[Dict]) -> Dict:
    """分析总赤字分布"""
    totals = [item['P_0']['total'] for item in data if item['status'] == 'success']
    
    return {
        'totals': totals,
        'mean': np.mean(totals),
        'std': np.std(totals),
        'median': np.median(totals),
        'min': min(totals),
        'max': max(totals)
    }


def print_summary(data: List[Dict]):
    """打印统计摘要"""
    print("=" * 80)
    print("📊 EPJ-IEDR 批量评估结果统计分析")
    print("=" * 80)
    
    # 基本信息
    success_count = sum(1 for item in data if item['status'] == 'success')
    print(f"\n✅ 评估完成: {success_count}/{len(data)} 个剧本")
    print(f"成功率: {success_count/len(data)*100:.1f}%")
    
    # 1. 各指标得分分布
    print("\n" + "=" * 80)
    print("1️⃣  各指标得分分布统计")
    print("=" * 80)
    
    ind_analysis = analyze_indicators(data)
    
    print(f"\n{'指标':<20} {'均值':<8} {'中位数':<8} {'标准差':<8} {'分布 [0/1/2/3]'}")
    print("-" * 80)
    
    for ind in ["C.1", "C.2", "C.3", "A.1", "A.2", "A.3", "P.1", "P.2", "P.3"]:
        stats = ind_analysis[ind]
        dist = stats['distribution']
        dist_str = f"[{dist.get(0,0)}/{dist.get(1,0)}/{dist.get(2,0)}/{dist.get(3,0)}]"
        print(f"{DIMENSION_NAMES[ind]:<20} {stats['mean']:<8.2f} {stats['median']:<8.1f} "
              f"{stats['std']:<8.2f} {dist_str}")
    
    # 2. 三轴赤字分布
    print("\n" + "=" * 80)
    print("2️⃣  三轴赤字分布统计 (P_0向量)")
    print("=" * 80)
    
    axis_analysis = analyze_axes(data)
    
    print(f"\n{'轴':<20} {'均值':<10} {'中位数':<10} {'标准差':<10} {'范围'}")
    print("-" * 80)
    
    for axis in ["C", "A", "P"]:
        stats = axis_analysis[axis]
        range_str = f"[{stats['min']:.0f}, {stats['max']:.0f}]"
        print(f"{AXIS_NAMES[axis]:<20} {stats['mean']:<10.2f} {stats['median']:<10.1f} "
              f"{stats['std']:<10.2f} {range_str}")
    
    # 3. 总赤字分布
    print("\n" + "=" * 80)
    print("3️⃣  总赤字分布统计")
    print("=" * 80)
    
    total_analysis = analyze_total_deficit(data)
    
    print(f"\n均值: {total_analysis['mean']:.2f}")
    print(f"中位数: {total_analysis['median']:.1f}")
    print(f"标准差: {total_analysis['std']:.2f}")
    print(f"范围: [{total_analysis['min']:.0f}, {total_analysis['max']:.0f}]")
    
    # 4. 分布分析
    print("\n" + "=" * 80)
    print("4️⃣  分布特征分析")
    print("=" * 80)
    
    # 找出偏高/偏低的指标
    print("\n🔺 得分偏高的指标 (均值 > 2.0):")
    high_indicators = [(ind, stats['mean']) for ind, stats in ind_analysis.items() if stats['mean'] > 2.0]
    if high_indicators:
        for ind, mean in sorted(high_indicators, key=lambda x: x[1], reverse=True):
            print(f"  • {DIMENSION_NAMES[ind]}: {mean:.2f}")
    else:
        print("  （无）")
    
    print("\n🔻 得分偏低的指标 (均值 < 1.0):")
    low_indicators = [(ind, stats['mean']) for ind, stats in ind_analysis.items() if stats['mean'] < 1.0]
    if low_indicators:
        for ind, mean in sorted(low_indicators, key=lambda x: x[1]):
            print(f"  • {DIMENSION_NAMES[ind]}: {mean:.2f}")
    else:
        print("  （无）")
    
    # 5. 特殊案例识别
    print("\n" + "=" * 80)
    print("5️⃣  特殊案例识别")
    print("=" * 80)
    
    # 最低赤字案例
    min_deficit_item = min(data, key=lambda x: x['P_0']['total'] if x['status'] == 'success' else float('inf'))
    print(f"\n📉 最低赤字案例: {min_deficit_item['script_id']}")
    print(f"   总赤字: {min_deficit_item['P_0']['total']}")
    print(f"   P_0: C={min_deficit_item['P_0']['C']}, A={min_deficit_item['P_0']['A']}, P={min_deficit_item['P_0']['P']}")
    
    # 最高赤字案例
    max_deficit_item = max(data, key=lambda x: x['P_0']['total'] if x['status'] == 'success' else float('-inf'))
    print(f"\n📈 最高赤字案例: {max_deficit_item['script_id']}")
    print(f"   总赤字: {max_deficit_item['P_0']['total']}")
    print(f"   P_0: C={max_deficit_item['P_0']['C']}, A={max_deficit_item['P_0']['A']}, P={max_deficit_item['P_0']['P']}")
    
    # C轴主导案例
    c_dominant = [item for item in data if item['status'] == 'success' and 
                  abs(item['P_0']['C']) > abs(item['P_0']['A']) and 
                  abs(item['P_0']['C']) > abs(item['P_0']['P'])]
    print(f"\n🧠 C轴主导案例: {len(c_dominant)} 个 ({len(c_dominant)/success_count*100:.1f}%)")
    
    # A轴主导案例
    a_dominant = [item for item in data if item['status'] == 'success' and 
                  abs(item['P_0']['A']) > abs(item['P_0']['C']) and 
                  abs(item['P_0']['A']) > abs(item['P_0']['P'])]
    print(f"❤️  A轴主导案例: {len(a_dominant)} 个 ({len(a_dominant)/success_count*100:.1f}%)")
    
    # P轴主导案例
    p_dominant = [item for item in data if item['status'] == 'success' and 
                  abs(item['P_0']['P']) > abs(item['P_0']['C']) and 
                  abs(item['P_0']['P']) > abs(item['P_0']['A'])]
    print(f"💪 P轴主导案例: {len(p_dominant)} 个 ({len(p_dominant)/success_count*100:.1f}%)")
    
    # 6. 偏好检测
    print("\n" + "=" * 80)
    print("6️⃣  案例库偏好检测")
    print("=" * 80)
    
    print("\n🔍 检测标准:")
    print("  • 均值 > 2.0 → 该维度普遍偏高")
    print("  • 均值 < 1.0 → 该维度普遍偏低")
    print("  • 标准差 < 0.5 → 分布过于集中")
    print("  • 某级别占比 > 70% → 分布严重不均")
    
    print("\n⚠️  潜在偏好问题:")
    
    has_bias = False
    
    # 检查均值偏差
    for ind, stats in ind_analysis.items():
        if stats['mean'] > 2.0:
            print(f"  ⚡ {DIMENSION_NAMES[ind]}: 均值过高 ({stats['mean']:.2f})")
            has_bias = True
        elif stats['mean'] < 1.0:
            print(f"  ⚡ {DIMENSION_NAMES[ind]}: 均值过低 ({stats['mean']:.2f})")
            has_bias = True
    
    # 检查分布集中度
    for ind, stats in ind_analysis.items():
        if stats['std'] < 0.5:
            print(f"  ⚡ {DIMENSION_NAMES[ind]}: 分布过于集中 (标准差={stats['std']:.2f})")
            has_bias = True
    
    # 检查单一级别占比
    for ind, stats in ind_analysis.items():
        dist = stats['distribution']
        max_level = max(dist, key=dist.get)
        max_ratio = dist[max_level] / len(stats['scores'])
        if max_ratio > 0.7:
            print(f"  ⚡ {DIMENSION_NAMES[ind]}: 级别{max_level}占比过高 ({max_ratio*100:.1f}%)")
            has_bias = True
    
    if not has_bias:
        print("  ✅ 未检测到明显偏好，案例分布相对均衡")
    
    print("\n" + "=" * 80)
    print("📊 分析完成")
    print("=" * 80)


def main():
    """主函数"""
    data = load_results()
    print_summary(data)


if __name__ == "__main__":
    main()

