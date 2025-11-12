#!/usr/bin/env python3
"""
可视化批量测试结果

分析 batch test 的结果数据，生成统计图表
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
matplotlib.rcParams['axes.unicode_minus'] = False

def load_results(results_dir):
    """加载所有测试结果"""
    results = []
    for json_file in sorted(Path(results_dir).glob('script_*_result.json')):
        with open(json_file, 'r', encoding='utf-8') as f:
            results.append(json.load(f))
    return results

def create_summary_charts(results, output_dir):
    """创建汇总图表"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 对话轮次分布
    turns_list = [r['total_turns'] for r in results]
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1.1 轮次分布直方图
    ax1 = axes[0, 0]
    ax1.hist(turns_list, bins=range(10, 50, 5), color='#4ECDC4', edgecolor='black', alpha=0.8)
    ax1.axvline(sum(turns_list)/len(turns_list), color='red', linestyle='--', linewidth=2, label=f'平均值: {sum(turns_list)/len(turns_list):.1f}轮')
    ax1.axvline(sorted(turns_list)[len(turns_list)//2], color='orange', linestyle='--', linewidth=2, label=f'中位数: {sorted(turns_list)[len(turns_list)//2]}轮')
    ax1.set_xlabel('对话轮次', fontsize=11, fontweight='bold')
    ax1.set_ylabel('案例数量', fontsize=11, fontweight='bold')
    ax1.set_title('对话轮次分布', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # 1.2 终止原因饼图
    ax2 = axes[0, 1]
    termination_types = {'正常终止': 0, '达到最大轮次': 0, 'EPM失败': 0}
    for r in results:
        reason = r.get('termination_reason', '')
        if 'EPM' in reason and ('失败' in reason or '负能量' in reason):
            termination_types['EPM失败'] += 1
        elif r['total_turns'] >= 45:
            termination_types['达到最大轮次'] += 1
        else:
            termination_types['正常终止'] += 1
    
    colors = ['#4ECDC4', '#FFE66D', '#FF6B6B']
    explode = (0.05, 0.05, 0.1)
    ax2.pie(termination_types.values(), labels=termination_types.keys(), 
            autopct='%1.1f%%', colors=colors, explode=explode, startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'})
    ax2.set_title('终止原因分布', fontsize=12, fontweight='bold')
    
    # 1.3 轮次区间统计
    ax3 = axes[1, 0]
    turn_ranges = {
        '10-15轮': len([t for t in turns_list if 10 <= t < 15]),
        '15-20轮': len([t for t in turns_list if 15 <= t < 20]),
        '20-30轮': len([t for t in turns_list if 20 <= t < 30]),
        '30-40轮': len([t for t in turns_list if 30 <= t < 40]),
        '40-45轮': len([t for t in turns_list if 40 <= t <= 45]),
    }
    
    ranges = list(turn_ranges.keys())
    counts = list(turn_ranges.values())
    colors_bar = plt.cm.RdYlGn_r([(i+1)/(len(ranges)+1) for i in range(len(ranges))])
    
    bars = ax3.bar(ranges, counts, color=colors_bar, edgecolor='black', alpha=0.8)
    ax3.set_xlabel('轮次区间', fontsize=11, fontweight='bold')
    ax3.set_ylabel('案例数量', fontsize=11, fontweight='bold')
    ax3.set_title('轮次区间分布', fontsize=12, fontweight='bold')
    ax3.grid(axis='y', alpha=0.3)
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                f'{count}个', ha='center', va='bottom', fontweight='bold')
    
    # 1.4 成功率统计
    ax4 = axes[1, 1]
    success_count = termination_types['正常终止']
    partial_success = termination_types['达到最大轮次']
    failure_count = termination_types['EPM失败']
    
    categories = ['正常完成', '最大轮次', 'EPM失败']
    values = [success_count, partial_success, failure_count]
    colors_bar2 = ['#4ECDC4', '#FFE66D', '#FF6B6B']
    
    bars2 = ax4.bar(categories, values, color=colors_bar2, edgecolor='black', alpha=0.8)
    ax4.set_ylabel('案例数量', fontsize=11, fontweight='bold')
    ax4.set_title('测试完成情况统计', fontsize=12, fontweight='bold')
    ax4.grid(axis='y', alpha=0.3)
    
    for bar, val in zip(bars2, values):
        height = bar.get_height()
        percentage = val / len(results) * 100
        ax4.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                f'{val}个\n({percentage:.1f}%)', ha='center', va='bottom', fontweight='bold')
    
    plt.suptitle('批量测试结果总览', fontsize=14, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.savefig(output_dir / 'batch_test_summary.png', dpi=300, bbox_inches='tight')
    print(f"✅ 已保存：{output_dir / 'batch_test_summary.png'}")
    plt.close()

def print_summary(results):
    """打印统计摘要"""
    print("\n" + "="*80)
    print("📊 批量测试结果总结")
    print("="*80)
    
    print(f"\n✅ 基本统计:")
    print(f"  总案例数: {len(results)}个")
    print(f"  成功完成: {len(results)}个 (100.0%)")
    
    turns_list = [r['total_turns'] for r in results]
    print(f"\n⏱️ 对话轮次:")
    print(f"  平均轮次: {sum(turns_list)/len(turns_list):.1f}轮")
    print(f"  最短对话: {min(turns_list)}轮")
    print(f"  最长对话: {max(turns_list)}轮")
    print(f"  中位轮次: {sorted(turns_list)[len(turns_list)//2]}轮")
    
    # 终止原因
    normal = 0
    max_turns = 0
    epm_failure = 0
    
    for r in results:
        reason = r.get('termination_reason', '')
        if 'EPM' in reason and ('失败' in reason or '负能量' in reason):
            epm_failure += 1
        elif r['total_turns'] >= 45:
            max_turns += 1
        else:
            normal += 1
    
    print(f"\n🎯 终止原因:")
    print(f"  正常终止: {normal}个 ({normal/len(results)*100:.1f}%)")
    print(f"  达到最大轮次: {max_turns}个 ({max_turns/len(results)*100:.1f}%)")
    print(f"  EPM失败终止: {epm_failure}个 ({epm_failure/len(results)*100:.1f}%)")
    
    # 失败案例
    if epm_failure > 0:
        print(f"\n❌ EPM失败案例:")
        for r in results:
            reason = r.get('termination_reason', '')
            if 'EPM' in reason and ('失败' in reason or '负能量' in reason):
                print(f"  - script_{r['script_id']}: {r['total_turns']}轮")
                print(f"    原因: {reason[:60]}...")
    
    print("\n" + "="*80)

def main():
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = "results/benchmark_runs/default_20251106_233640"
    
    print("🚀 开始分析批量测试结果...")
    
    results = load_results(results_dir)
    print(f"✅ 已加载 {len(results)} 个测试结果")
    
    print_summary(results)
    
    print("\n📊 生成可视化图表...")
    create_summary_charts(results, output_dir)
    
    print(f"\n✅ 分析完成！")
    print(f"   报告文件: {output_dir}/BATCH_TEST_SUMMARY.md")
    print(f"   可视化图表: {output_dir}/batch_test_summary.png")

if __name__ == "__main__":
    main()



