#!/usr/bin/env python3
"""
可视化测试库情景分布标签

分析 classification_results.json 中的标签分布，生成统计图表
"""

import json
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC', 'Heiti TC']
matplotlib.rcParams['axes.unicode_minus'] = False

def load_classification_data(filepath):
    """加载分类数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def parse_labels(data):
    """解析标签，分离情景类型和情感类型"""
    scenarios = []
    emotions = []
    scenario_emotion_pairs = []
    
    for item in data:
        labels = item['labels']
        parts = labels.split(',')
        
        if len(parts) >= 1:
            scenario = parts[0].strip()
            scenarios.append(scenario)
        
        if len(parts) >= 2:
            emotion = parts[1].strip()
            emotions.append(emotion)
            scenario_emotion_pairs.append((scenario, emotion))
    
    return scenarios, emotions, scenario_emotion_pairs

def extract_main_categories(labels):
    """提取主类别（去掉子类别）"""
    main_categories = []
    for label in labels:
        if '-' in label:
            main_cat = label.split('-')[0]
            main_categories.append(main_cat)
        else:
            main_categories.append(label)
    return main_categories

def create_distribution_charts(scenarios, emotions, output_dir):
    """创建分布图表"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. 情景类型分布（主类别）
    scenario_main = extract_main_categories(scenarios)
    scenario_counts = Counter(scenario_main)
    
    plt.figure(figsize=(12, 6))
    categories = list(scenario_counts.keys())
    counts = list(scenario_counts.values())
    colors = plt.cm.Set3(range(len(categories)))
    
    plt.bar(categories, counts, color=colors, edgecolor='black', alpha=0.8)
    plt.xlabel('情景类型', fontsize=12, fontweight='bold')
    plt.ylabel('案例数量', fontsize=12, fontweight='bold')
    plt.title('测试库情景类型分布（主类别）', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # 添加数值标签
    for i, (cat, count) in enumerate(zip(categories, counts)):
        plt.text(i, count + 0.5, str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scenario_main_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ 已保存：{output_dir / 'scenario_main_distribution.png'}")
    plt.close()
    
    # 2. 情景类型分布（详细子类别）
    scenario_counts_detailed = Counter(scenarios)
    top_scenarios = scenario_counts_detailed.most_common(15)  # 只显示前15个
    
    plt.figure(figsize=(14, 8))
    categories_detailed = [item[0] for item in top_scenarios]
    counts_detailed = [item[1] for item in top_scenarios]
    colors_detailed = plt.cm.tab20(range(len(categories_detailed)))
    
    plt.barh(categories_detailed, counts_detailed, color=colors_detailed, edgecolor='black', alpha=0.8)
    plt.xlabel('案例数量', fontsize=12, fontweight='bold')
    plt.ylabel('情景类型（详细）', fontsize=12, fontweight='bold')
    plt.title('测试库情景类型分布（TOP 15 详细类别）', fontsize=14, fontweight='bold')
    plt.grid(axis='x', alpha=0.3)
    
    # 添加数值标签
    for i, (cat, count) in enumerate(zip(categories_detailed, counts_detailed)):
        plt.text(count + 0.5, i, str(count), ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scenario_detailed_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ 已保存：{output_dir / 'scenario_detailed_distribution.png'}")
    plt.close()
    
    # 3. 情感类型分布（主类别）
    emotion_main = extract_main_categories(emotions)
    emotion_counts = Counter(emotion_main)
    
    plt.figure(figsize=(10, 6))
    categories_emotion = list(emotion_counts.keys())
    counts_emotion = list(emotion_counts.values())
    colors_emotion = ['#FF6B6B' if '负向' in cat else '#4ECDC4' if '正向' in cat else '#95E1D3' 
                      for cat in categories_emotion]
    
    plt.bar(categories_emotion, counts_emotion, color=colors_emotion, edgecolor='black', alpha=0.8)
    plt.xlabel('情感类型', fontsize=12, fontweight='bold')
    plt.ylabel('案例数量', fontsize=12, fontweight='bold')
    plt.title('测试库情感类型分布', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    
    # 添加数值标签
    for i, (cat, count) in enumerate(zip(categories_emotion, counts_emotion)):
        plt.text(i, count + 0.5, str(count), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'emotion_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ 已保存：{output_dir / 'emotion_distribution.png'}")
    plt.close()
    
    # 4. 情感类型详细分布
    emotion_counts_detailed = Counter(emotions)
    
    # 分离正向和负向情感
    positive_emotions = {k: v for k, v in emotion_counts_detailed.items() if '正向情感' in k}
    negative_emotions = {k: v for k, v in emotion_counts_detailed.items() if '负向情感' in k}
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 正向情感
    if positive_emotions:
        pos_labels = [k.replace('正向情感-', '') for k in positive_emotions.keys()]
        pos_counts = list(positive_emotions.values())
        ax1.barh(pos_labels, pos_counts, color='#4ECDC4', edgecolor='black', alpha=0.8)
        ax1.set_xlabel('案例数量', fontsize=11, fontweight='bold')
        ax1.set_title('正向情感分布', fontsize=12, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        for i, count in enumerate(pos_counts):
            ax1.text(count + 0.3, i, str(count), ha='left', va='center', fontweight='bold')
    
    # 负向情感
    if negative_emotions:
        neg_labels = [k.replace('负向情感-', '') for k in negative_emotions.keys()]
        neg_counts = list(negative_emotions.values())
        ax2.barh(neg_labels, neg_counts, color='#FF6B6B', edgecolor='black', alpha=0.8)
        ax2.set_xlabel('案例数量', fontsize=11, fontweight='bold')
        ax2.set_title('负向情感分布', fontsize=12, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        for i, count in enumerate(neg_counts):
            ax2.text(count + 0.3, i, str(count), ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'emotion_detailed_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ 已保存：{output_dir / 'emotion_detailed_distribution.png'}")
    plt.close()
    
    # 5. 饼图：情景主类别占比
    plt.figure(figsize=(10, 10))
    colors_pie = plt.cm.Set3(range(len(scenario_counts)))
    
    def autopct_format(values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return f'{pct:.1f}%\n({val}个)' if pct > 3 else ''
        return my_format
    
    plt.pie(scenario_counts.values(), 
            labels=scenario_counts.keys(), 
            colors=colors_pie,
            autopct=autopct_format(list(scenario_counts.values())),
            startangle=90,
            textprops={'fontsize': 10, 'fontweight': 'bold'})
    plt.title('测试库情景类型占比', fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'scenario_pie_chart.png', dpi=300, bbox_inches='tight')
    print(f"✅ 已保存：{output_dir / 'scenario_pie_chart.png'}")
    plt.close()

def print_statistics(scenarios, emotions, data):
    """打印统计信息"""
    print("\n" + "="*70)
    print("📊 测试库标签分布统计")
    print("="*70)
    
    print(f"\n总案例数：{len(data)}")
    
    # 情景主类别统计
    scenario_main = extract_main_categories(scenarios)
    scenario_main_counts = Counter(scenario_main)
    print(f"\n📌 情景主类别分布（{len(scenario_main_counts)}个类别）：")
    for cat, count in sorted(scenario_main_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(data) * 100
        print(f"   {cat}: {count}个 ({percentage:.1f}%)")
    
    # 情感主类别统计
    emotion_main = extract_main_categories(emotions)
    emotion_main_counts = Counter(emotion_main)
    print(f"\n😊 情感主类别分布：")
    for cat, count in sorted(emotion_main_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(data) * 100
        print(f"   {cat}: {count}个 ({percentage:.1f}%)")
    
    # 详细情景类型统计
    scenario_counts = Counter(scenarios)
    print(f"\n🎯 情景详细类型分布（TOP 10）：")
    for cat, count in scenario_counts.most_common(10):
        percentage = count / len(data) * 100
        print(f"   {cat}: {count}个 ({percentage:.1f}%)")
    
    # 详细情感类型统计
    emotion_counts = Counter(emotions)
    print(f"\n💭 情感详细类型分布（TOP 10）：")
    for cat, count in emotion_counts.most_common(10):
        percentage = count / len(data) * 100
        print(f"   {cat}: {count}个 ({percentage:.1f}%)")
    
    print("\n" + "="*70)

def main():
    """主函数"""
    # 文件路径
    classification_file = Path("Benchmark/topics/data/classification_results.json")
    output_dir = Path("results/scenario_analysis")
    
    print("🚀 开始分析测试库标签分布...")
    
    # 加载数据
    print(f"\n📂 加载数据：{classification_file}")
    data = load_classification_data(classification_file)
    print(f"✅ 已加载 {len(data)} 个测试案例")
    
    # 解析标签
    print("\n🔍 解析标签...")
    scenarios, emotions, pairs = parse_labels(data)
    print(f"✅ 已解析 {len(scenarios)} 个情景标签，{len(emotions)} 个情感标签")
    
    # 打印统计信息
    print_statistics(scenarios, emotions, data)
    
    # 创建可视化图表
    print(f"\n📊 生成可视化图表...")
    create_distribution_charts(scenarios, emotions, output_dir)
    
    print(f"\n✅ 分析完成！所有图表已保存到：{output_dir}")
    print("\n生成的图表：")
    print("   1. scenario_main_distribution.png - 情景主类别分布")
    print("   2. scenario_detailed_distribution.png - 情景详细类别分布（TOP 15）")
    print("   3. scenario_pie_chart.png - 情景类别占比饼图")
    print("   4. emotion_distribution.png - 情感主类别分布")
    print("   5. emotion_detailed_distribution.png - 情感详细分布（正向/负向）")

if __name__ == "__main__":
    main()

