#!/usr/bin/env python3
"""
简化版3D共情轨迹可视化

核心理念：原点(0,0,0)是共情的理想终点
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
matplotlib.rcParams['axes.unicode_minus'] = False

def load_all_trajectories(results_dir):
    """加载所有案例的轨迹数据"""
    results_dir = Path(results_dir)
    all_data = []
    
    for json_file in sorted(results_dir.glob('script_*_result.json')):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        script_id = data['script_id']
        total_turns = data['total_turns']
        termination_reason = data.get('termination_reason', '')
        
        # 判断终止类型
        if 'EPM' in termination_reason and ('失败' in termination_reason or '负能量' in termination_reason):
            status = 'failure'
        elif total_turns >= 45:
            status = 'max_turns'
        else:
            status = 'success'
        
        # 提取轨迹
        if 'epj' in data and 'trajectory' in data['epj']:
            P_0 = data['epj']['P_0_initial_deficit']
            P_final = data['epj']['P_final_position']
            
            if isinstance(P_0, str):
                P_0 = eval(P_0)
            if isinstance(P_final, str):
                P_final = eval(P_final)
            
            all_data.append({
                'script_id': script_id,
                'total_turns': total_turns,
                'status': status,
                'P_0': P_0,
                'P_final': P_final
            })
    
    return all_data

def draw_target_sphere(ax, radius=1.0):
    """绘制目标球（强调原点是终点）"""
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 20)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='gold', alpha=0.2, edgecolor='orange', linewidth=0.5)

def plot_simple_overview(all_data, output_path):
    """简化版：整体概览图 - 强调原点是终点"""
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. 绘制目标球
    draw_target_sphere(ax, radius=1.0)
    
    # 2. 超大原点标记 - 视觉焦点
    ax.scatter([0], [0], [0], c='red', s=500, marker='*', 
              edgecolors='darkred', linewidths=3, 
              label='🎯 理想终点：原点(0,0,0)', zorder=100)
    
    # 3. 添加原点说明文字
    ax.text(0, 0, 5, '🎯 共情目标\n原点(0,0,0)', 
           fontsize=14, fontweight='bold', color='red',
           ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
    
    # 4. 绘制所有起点（浅灰色，不抢眼）
    P_0_list = [d['P_0'] for d in all_data]
    C_0 = [p[0] for p in P_0_list]
    A_0 = [p[1] for p in P_0_list]
    P_0_val = [p[2] for p in P_0_list]
    ax.scatter(C_0, A_0, P_0_val, c='lightgray', s=80, marker='o', 
              alpha=0.5, edgecolors='gray', linewidths=1, label='初始位置 P₀')
    
    # 5. 绘制轨迹箭头 - 统一的简洁风格
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    # 成功案例：蓝色箭头
    for d in success_data:
        P_0 = d['P_0']
        P_final = d['P_final']
        ax.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], [P_0[2], P_final[2]], 
               color='#3498db', linewidth=1.5, alpha=0.6, linestyle='-')
        ax.scatter([P_final[0]], [P_final[1]], [P_final[2]], 
                  c='#3498db', s=60, marker='o', alpha=0.8, edgecolors='navy', linewidths=1)
    
    # 失败案例：红色箭头（更醒目）
    for d in failure_data:
        P_0 = d['P_0']
        P_final = d['P_final']
        ax.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], [P_0[2], P_final[2]], 
               color='#e74c3c', linewidth=2, alpha=0.8, linestyle='--')
        ax.scatter([P_final[0]], [P_final[1]], [P_final[2]], 
                  c='#e74c3c', s=80, marker='X', alpha=0.9, edgecolors='darkred', linewidths=2)
    
    # 6. 添加理想路径示意（从某个典型起点到原点的虚线）
    typical_start = [-15, -20, -15]  # 典型起始位置
    ax.plot([typical_start[0], 0], [typical_start[1], 0], [typical_start[2], 0],
           color='green', linewidth=3, linestyle=':', alpha=0.6, label='理想路径示意')
    
    # 图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='red', 
              markersize=15, label='🎯 理想终点(0,0,0)'),
        Line2D([0], [0], color='#3498db', linewidth=2, 
              label=f'成功轨迹 ({len(success_data)}个)'),
        Line2D([0], [0], color='#e74c3c', linewidth=2, linestyle='--',
              label=f'未达标轨迹 ({len(failure_data)}个)'),
        Line2D([0], [0], color='green', linewidth=3, linestyle=':', 
              label='理想路径'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=12, framealpha=0.9)
    
    # 坐标轴
    ax.set_xlabel('认知轴 (C)', fontsize=13, fontweight='bold')
    ax.set_ylabel('情感轴 (A)', fontsize=13, fontweight='bold')
    ax.set_zlabel('动机轴 (P)', fontsize=13, fontweight='bold')
    ax.set_title('共情轨迹3D可视化：从起点到终点（原点）', fontsize=15, fontweight='bold', pad=20)
    
    # 添加说明文字
    fig.text(0.5, 0.02, '核心理念：原点(0,0,0)代表共情赤字完全消除的理想状态，是所有对话的终极目标', 
            ha='center', fontsize=12, style='italic', 
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    ax.view_init(elev=20, azim=45)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存简化版整体概览图：{output_path}")
    plt.close()

def plot_success_vs_failure(all_data, output_path):
    """对比图：成功 vs 失败轨迹"""
    fig = plt.figure(figsize=(18, 7))
    
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    # 左图：成功案例
    ax1 = fig.add_subplot(121, projection='3d')
    draw_target_sphere(ax1, radius=1.0)
    ax1.scatter([0], [0], [0], c='red', s=400, marker='*', 
               edgecolors='darkred', linewidths=3, zorder=100)
    
    for d in success_data:
        P_0 = d['P_0']
        P_final = d['P_final']
        ax1.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], [P_0[2], P_final[2]], 
                color='#2ecc71', linewidth=1.5, alpha=0.6)
        ax1.scatter([P_0[0]], [P_0[1]], [P_0[2]], c='lightgray', s=50, alpha=0.6)
        ax1.scatter([P_final[0]], [P_final[1]], [P_final[2]], 
                   c='#2ecc71', s=60, marker='o', alpha=0.8, edgecolors='darkgreen', linewidths=1)
    
    ax1.set_xlabel('C', fontsize=11, fontweight='bold')
    ax1.set_ylabel('A', fontsize=11, fontweight='bold')
    ax1.set_zlabel('P', fontsize=11, fontweight='bold')
    ax1.set_title(f'✅ 成功案例 ({len(success_data)}个)\n轨迹收敛到原点附近', 
                 fontsize=13, fontweight='bold', color='green')
    ax1.view_init(elev=20, azim=45)
    ax1.grid(True, alpha=0.3)
    
    # 右图：失败案例
    ax2 = fig.add_subplot(122, projection='3d')
    draw_target_sphere(ax2, radius=1.0)
    ax2.scatter([0], [0], [0], c='red', s=400, marker='*', 
               edgecolors='darkred', linewidths=3, zorder=100)
    
    for d in failure_data:
        P_0 = d['P_0']
        P_final = d['P_final']
        ax2.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], [P_0[2], P_final[2]], 
                color='#e74c3c', linewidth=2, alpha=0.8, linestyle='--')
        ax2.scatter([P_0[0]], [P_0[1]], [P_0[2]], c='lightgray', s=50, alpha=0.6)
        ax2.scatter([P_final[0]], [P_final[1]], [P_final[2]], 
                   c='#e74c3c', s=80, marker='X', alpha=0.9, edgecolors='darkred', linewidths=2)
    
    ax2.set_xlabel('C', fontsize=11, fontweight='bold')
    ax2.set_ylabel('A', fontsize=11, fontweight='bold')
    ax2.set_zlabel('P', fontsize=11, fontweight='bold')
    ax2.set_title(f'❌ 未达标案例 ({len(failure_data)}个)\n未能到达原点', 
                 fontsize=13, fontweight='bold', color='red')
    ax2.view_init(elev=20, azim=45)
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle('成功 vs 失败：对比原点收敛性', fontsize=15, fontweight='bold')
    fig.text(0.5, 0.02, '🎯 原点(0,0,0)是理想终点 | 成功案例收敛到原点，失败案例偏离原点', 
            ha='center', fontsize=11, style='italic',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存成功vs失败对比图：{output_path}")
    plt.close()

def plot_distance_to_origin(all_data, output_path):
    """距离分析：到原点的距离变化"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # 计算距离
    initial_distances = []
    final_distances = []
    distance_reductions = []
    case_labels = []
    colors = []
    
    for d in all_data:
        P_0 = np.array(d['P_0'])
        P_final = np.array(d['P_final'])
        
        dist_0 = np.linalg.norm(P_0)
        dist_final = np.linalg.norm(P_final)
        reduction = dist_0 - dist_final
        
        initial_distances.append(dist_0)
        final_distances.append(dist_final)
        distance_reductions.append(reduction)
        case_labels.append(d['script_id'])
        
        if d['status'] == 'success':
            colors.append('#2ecc71')
        else:
            colors.append('#e74c3c')
    
    # 左图：初始距离 vs 最终距离
    ax1 = axes[0]
    scatter = ax1.scatter(initial_distances, final_distances, 
                         c=colors, s=100, alpha=0.7, edgecolors='black', linewidths=1)
    
    # 添加对角线（y=x）
    max_dist = max(max(initial_distances), max(final_distances))
    ax1.plot([0, max_dist], [0, max_dist], 'k--', alpha=0.3, linewidth=1, label='无进展线(y=x)')
    
    # 添加目标区域（原点附近）
    ax1.axhspan(0, 1, alpha=0.2, color='green', label='目标区域(距离<1)')
    ax1.axhline(y=1, color='green', linestyle=':', linewidth=2, alpha=0.5)
    
    ax1.set_xlabel('初始距离（到原点）', fontsize=12, fontweight='bold')
    ax1.set_ylabel('最终距离（到原点）', fontsize=12, fontweight='bold')
    ax1.set_title('到原点的距离变化\n（对角线下方=成功接近原点）', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 右图：距离缩减量
    ax2 = axes[1]
    indices = np.arange(len(distance_reductions))
    bars = ax2.bar(indices, distance_reductions, color=colors, alpha=0.7, edgecolor='black', linewidth=1)
    
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
    ax2.set_xlabel('案例编号', fontsize=12, fontweight='bold')
    ax2.set_ylabel('距离缩减量（正值=接近原点）', fontsize=12, fontweight='bold')
    ax2.set_title('各案例到原点的距离改善\n（正值=成功接近，负值=远离）', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 添加平均线
    avg_reduction = np.mean(distance_reductions)
    ax2.axhline(y=avg_reduction, color='blue', linestyle='--', linewidth=2, 
               label=f'平均缩减: {avg_reduction:.1f}', alpha=0.7)
    ax2.legend(fontsize=10)
    
    fig.suptitle('核心指标：到原点(理想终点)的距离分析', fontsize=15, fontweight='bold')
    fig.text(0.5, 0.02, '🎯 目标：最终距离应尽可能接近0（原点）', 
            ha='center', fontsize=11, style='italic',
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存距离分析图：{output_path}")
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_visualizations_simple"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 生成简化版3D轨迹可视化...")
    print("核心理念：原点(0,0,0)是共情的理想终点\n")
    
    # 加载数据
    all_data = load_all_trajectories(results_dir)
    print(f"✅ 已加载 {len(all_data)} 个案例\n")
    
    # 生成三张核心图表
    print("📊 生成可视化图表...\n")
    
    # 图1：整体概览（强调原点）
    plot_simple_overview(all_data, output_dir / "overview_simple.png")
    
    # 图2：成功vs失败对比
    plot_success_vs_failure(all_data, output_dir / "success_vs_failure.png")
    
    # 图3：距离分析
    plot_distance_to_origin(all_data, output_dir / "distance_analysis.png")
    
    print(f"\n✅ 所有简化版可视化图表已生成！")
    print(f"📁 保存位置: {output_dir}\n")
    print("生成的图表:")
    print("  1. overview_simple.png - 整体概览（强调原点是终点）")
    print("  2. success_vs_failure.png - 成功vs失败对比")
    print("  3. distance_analysis.png - 到原点的距离分析")

if __name__ == "__main__":
    main()

