#!/usr/bin/env python3
"""
优化版3D共情轨迹可视化 - 强调象限概念

核心设计：
1. 原点在右上角（目标位置）
2. 起点在左下角（赤字区）
3. 清晰的象限划分
4. 路径像2D坐标系一样容易判断
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
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
        
        if 'EPM' in termination_reason and ('失败' in termination_reason or '负能量' in termination_reason):
            status = 'failure'
        elif total_turns >= 45:
            status = 'max_turns'
        else:
            status = 'success'
        
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

def draw_coordinate_planes(ax, size=30):
    """绘制坐标平面（过原点），帮助理解象限"""
    # C-A平面（P=0）
    xx, yy = np.meshgrid(np.linspace(-size, size, 2), np.linspace(-size, size, 2))
    zz = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=0.05, color='lightblue', edgecolor='none')
    
    # C-P平面（A=0）
    xx, zz = np.meshgrid(np.linspace(-size, size, 2), np.linspace(-size, size, 2))
    yy = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=0.05, color='lightgreen', edgecolor='none')
    
    # A-P平面（C=0）
    yy, zz = np.meshgrid(np.linspace(-size, size, 2), np.linspace(-size, size, 2))
    xx = np.zeros_like(yy)
    ax.plot_surface(xx, yy, zz, alpha=0.05, color='lightyellow', edgecolor='none')

def draw_octants_labels(ax):
    """标注八个象限（3D空间的八卦限）"""
    offset = 25
    
    # 第I卦限（全正）- 目标区域
    ax.text(offset, offset, offset, 'I\n目标区', fontsize=11, fontweight='bold', 
           color='green', ha='center',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7))
    
    # 第VIII卦限（全负）- 起点区域
    ax.text(-offset, -offset, -offset, 'VIII\n起点区', fontsize=11, fontweight='bold', 
           color='red', ha='center',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))
    
    # 其他关键象限
    ax.text(-offset, -offset, offset, 'IV', fontsize=9, color='gray', ha='center', alpha=0.6)
    ax.text(offset, offset, -offset, 'V', fontsize=9, color='gray', ha='center', alpha=0.6)
    ax.text(-offset, offset, offset, 'II', fontsize=9, color='gray', ha='center', alpha=0.6)
    ax.text(offset, -offset, offset, 'III', fontsize=9, color='gray', ha='center', alpha=0.6)

def draw_target_sphere(ax, radius=1.0):
    """绘制目标球"""
    u = np.linspace(0, 2 * np.pi, 20)
    v = np.linspace(0, np.pi, 15)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='gold', alpha=0.3, edgecolor='orange', linewidth=0.5)

def plot_overview_optimized(all_data, output_path):
    """优化版整体概览图 - 强调象限和路径"""
    fig = plt.figure(figsize=(18, 14))
    ax = fig.add_subplot(111, projection='3d')
    
    # 1. 绘制坐标平面（帮助理解象限）
    draw_coordinate_planes(ax, size=30)
    
    # 2. 绘制坐标轴线（加粗）
    axis_limit = 30
    ax.plot([0, axis_limit], [0, 0], [0, 0], 'k-', linewidth=2, alpha=0.3)
    ax.plot([0, 0], [0, axis_limit], [0, 0], 'k-', linewidth=2, alpha=0.3)
    ax.plot([0, 0], [0, 0], [0, axis_limit], 'k-', linewidth=2, alpha=0.3)
    ax.plot([-axis_limit, 0], [0, 0], [0, 0], 'k--', linewidth=1.5, alpha=0.3)
    ax.plot([0, 0], [-axis_limit, 0], [0, 0], 'k--', linewidth=1.5, alpha=0.3)
    ax.plot([0, 0], [0, 0], [-axis_limit, 0], 'k--', linewidth=1.5, alpha=0.3)
    
    # 3. 标注象限
    draw_octants_labels(ax)
    
    # 4. 绘制目标球
    draw_target_sphere(ax, radius=1.0)
    
    # 5. 超大原点标记
    ax.scatter([0], [0], [0], c='red', s=600, marker='*', 
              edgecolors='darkred', linewidths=4, zorder=100,
              label='目标：原点(0,0,0)')
    
    # 6. 绘制起点区域标记（左下角的聚集区）
    P_0_list = [d['P_0'] for d in all_data]
    C_0 = [p[0] for p in P_0_list]
    A_0 = [p[1] for p in P_0_list]
    P_0_val = [p[2] for p in P_0_list]
    
    # 计算起点的中心位置
    C_0_center = np.mean(C_0)
    A_0_center = np.mean(A_0)
    P_0_center = np.mean(P_0_val)
    
    # 起点区域标注
    ax.scatter(C_0, A_0, P_0_val, c='#95a5a6', s=100, marker='o', 
              alpha=0.4, edgecolors='gray', linewidths=1, label='起点区域（赤字）')
    
    # 7. 绘制轨迹 - 清晰的路径
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    # 成功轨迹：渐变色从灰到绿
    for i, d in enumerate(success_data):
        P_0 = d['P_0']
        P_final = d['P_final']
        
        # 使用渐变色表示轨迹
        ax.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], [P_0[2], P_final[2]], 
               color='#27ae60', linewidth=2.5, alpha=0.7, linestyle='-', zorder=5)
        
        # 终点标记
        ax.scatter([P_final[0]], [P_final[1]], [P_final[2]], 
                  c='#27ae60', s=80, marker='o', alpha=0.9, 
                  edgecolors='darkgreen', linewidths=1.5, zorder=6)
    
    # 失败轨迹：红色虚线，更粗
    for d in failure_data:
        P_0 = d['P_0']
        P_final = d['P_final']
        
        ax.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], [P_0[2], P_final[2]], 
               color='#e74c3c', linewidth=3, alpha=0.9, linestyle='--', zorder=7)
        
        # 终点标记
        ax.scatter([P_final[0]], [P_final[1]], [P_final[2]], 
                  c='#e74c3c', s=120, marker='X', alpha=0.95, 
                  edgecolors='darkred', linewidths=2, zorder=8)
    
    # 8. 添加理想路径示意（从起点中心到原点）
    ax.plot([C_0_center, 0], [A_0_center, 0], [P_0_center, 0],
           color='blue', linewidth=4, linestyle=':', alpha=0.6, 
           label='理想路径', zorder=4)
    
    # 9. 添加方向箭头指示
    arrow_props = dict(arrowstyle='->', lw=3, color='blue', alpha=0.6)
    
    # 图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='red', 
              markersize=18, label='目标：原点(0,0,0)'),
        Line2D([0], [0], color='#27ae60', linewidth=3, 
              label=f'成功轨迹 ({len(success_data)}条)'),
        Line2D([0], [0], color='#e74c3c', linewidth=3, linestyle='--',
              label=f'失败轨迹 ({len(failure_data)}条)'),
        Line2D([0], [0], color='blue', linewidth=3, linestyle=':', 
              label='理想路径方向'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=13, 
             framealpha=0.95, edgecolor='black', fancybox=True)
    
    # 坐标轴设置
    ax.set_xlabel('认知轴 (C)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_ylabel('情感轴 (A)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_zlabel('动机轴 (P)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    
    # 标题
    ax.set_title('共情轨迹3D空间可视化：从赤字区到目标点\n（八卦限空间，原点是唯一终点）', 
                fontsize=16, fontweight='bold', pad=25)
    
    # 设置视角：让原点在右上角，起点在左下角
    ax.view_init(elev=25, azim=225)  # azim=225让原点视觉上在右上
    
    # 设置坐标轴范围，确保原点突出
    max_range = 30
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    # ⭐ 关键：反转三个轴，让原点成为轴的终点（汇聚点）
    ax.invert_xaxis()  # C轴指向原点
    ax.invert_yaxis()  # A轴指向原点
    ax.invert_zaxis()  # P轴指向原点
    
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 添加说明文字
    explanation = (
        '空间结构：\n'
        '• I卦限（全正，右上）= 目标区域：共情充足\n'
        '• VIII卦限（全负，左下）= 起点区域：共情赤字\n'
        '• 成功 = 从VIII卦限出发，穿过坐标平面，到达原点(0,0,0)\n'
        '• 失败 = 未能到达原点，停留在其他卦限'
    )
    
    fig.text(0.02, 0.02, explanation, fontsize=11, 
            verticalalignment='bottom', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存优化版概览图：{output_path}")
    plt.close()

def plot_quadrant_view_2d(all_data, output_path):
    """2D象限视图对比（辅助理解）"""
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    # C-A平面
    ax1 = axes[0]
    for d in success_data:
        P_0, P_final = d['P_0'], d['P_final']
        ax1.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], 
                color='#27ae60', linewidth=2, alpha=0.6)
        ax1.scatter([P_0[0]], [P_0[1]], c='gray', s=50, alpha=0.5)
        ax1.scatter([P_final[0]], [P_final[1]], c='#27ae60', s=60, marker='o')
    
    for d in failure_data:
        P_0, P_final = d['P_0'], d['P_final']
        ax1.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], 
                color='#e74c3c', linewidth=2.5, alpha=0.8, linestyle='--')
        ax1.scatter([P_0[0]], [P_0[1]], c='gray', s=50, alpha=0.5)
        ax1.scatter([P_final[0]], [P_final[1]], c='#e74c3c', s=80, marker='X')
    
    ax1.scatter([0], [0], c='red', s=300, marker='*', edgecolors='darkred', linewidths=2, zorder=10)
    ax1.axhline(0, color='black', linewidth=1.5, alpha=0.3)
    ax1.axvline(0, color='black', linewidth=1.5, alpha=0.3)
    ax1.set_xlabel('认知轴 (C)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('情感轴 (A)', fontsize=12, fontweight='bold')
    ax1.set_title('C-A平面投影\n（象限清晰可见）', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_aspect('equal', adjustable='box')
    
    # 标注象限
    ax1.text(15, 15, 'I\n(C+,A+)', fontsize=10, ha='center', color='green', fontweight='bold')
    ax1.text(-15, 15, 'II\n(C-,A+)', fontsize=10, ha='center', color='gray')
    ax1.text(-15, -15, 'III\n(C-,A-)', fontsize=10, ha='center', color='red', fontweight='bold')
    ax1.text(15, -15, 'IV\n(C+,A-)', fontsize=10, ha='center', color='gray')
    
    # C-P平面
    ax2 = axes[1]
    for d in success_data:
        P_0, P_final = d['P_0'], d['P_final']
        ax2.plot([P_0[0], P_final[0]], [P_0[2], P_final[2]], 
                color='#27ae60', linewidth=2, alpha=0.6)
        ax2.scatter([P_0[0]], [P_0[2]], c='gray', s=50, alpha=0.5)
        ax2.scatter([P_final[0]], [P_final[2]], c='#27ae60', s=60, marker='o')
    
    for d in failure_data:
        P_0, P_final = d['P_0'], d['P_final']
        ax2.plot([P_0[0], P_final[0]], [P_0[2], P_final[2]], 
                color='#e74c3c', linewidth=2.5, alpha=0.8, linestyle='--')
        ax2.scatter([P_0[0]], [P_0[2]], c='gray', s=50, alpha=0.5)
        ax2.scatter([P_final[0]], [P_final[2]], c='#e74c3c', s=80, marker='X')
    
    ax2.scatter([0], [0], c='red', s=300, marker='*', edgecolors='darkred', linewidths=2, zorder=10)
    ax2.axhline(0, color='black', linewidth=1.5, alpha=0.3)
    ax2.axvline(0, color='black', linewidth=1.5, alpha=0.3)
    ax2.set_xlabel('认知轴 (C)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('动机轴 (P)', fontsize=12, fontweight='bold')
    ax2.set_title('C-P平面投影\n（象限清晰可见）', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_aspect('equal', adjustable='box')
    
    ax2.text(15, 15, 'I\n(C+,P+)', fontsize=10, ha='center', color='green', fontweight='bold')
    ax2.text(-15, 15, 'II\n(C-,P+)', fontsize=10, ha='center', color='gray')
    ax2.text(-15, -15, 'III\n(C-,P-)', fontsize=10, ha='center', color='red', fontweight='bold')
    ax2.text(15, -15, 'IV\n(C+,P-)', fontsize=10, ha='center', color='gray')
    
    # A-P平面
    ax3 = axes[2]
    for d in success_data:
        P_0, P_final = d['P_0'], d['P_final']
        ax3.plot([P_0[1], P_final[1]], [P_0[2], P_final[2]], 
                color='#27ae60', linewidth=2, alpha=0.6)
        ax3.scatter([P_0[1]], [P_0[2]], c='gray', s=50, alpha=0.5)
        ax3.scatter([P_final[1]], [P_final[2]], c='#27ae60', s=60, marker='o')
    
    for d in failure_data:
        P_0, P_final = d['P_0'], d['P_final']
        ax3.plot([P_0[1], P_final[1]], [P_0[2], P_final[2]], 
                color='#e74c3c', linewidth=2.5, alpha=0.8, linestyle='--')
        ax3.scatter([P_0[1]], [P_0[2]], c='gray', s=50, alpha=0.5)
        ax3.scatter([P_final[1]], [P_final[2]], c='#e74c3c', s=80, marker='X')
    
    ax3.scatter([0], [0], c='red', s=300, marker='*', edgecolors='darkred', linewidths=2, zorder=10)
    ax3.axhline(0, color='black', linewidth=1.5, alpha=0.3)
    ax3.axvline(0, color='black', linewidth=1.5, alpha=0.3)
    ax3.set_xlabel('情感轴 (A)', fontsize=12, fontweight='bold')
    ax3.set_ylabel('动机轴 (P)', fontsize=12, fontweight='bold')
    ax3.set_title('A-P平面投影\n（象限清晰可见）', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.set_aspect('equal', adjustable='box')
    
    ax3.text(15, 15, 'I\n(A+,P+)', fontsize=10, ha='center', color='green', fontweight='bold')
    ax3.text(-15, 15, 'II\n(A-,P+)', fontsize=10, ha='center', color='gray')
    ax3.text(-15, -15, 'III\n(A-,P-)', fontsize=10, ha='center', color='red', fontweight='bold')
    ax3.text(15, -15, 'IV\n(A+,P-)', fontsize=10, ha='center', color='gray')
    
    fig.suptitle('三个平面的象限视图：观察轨迹穿越象限的过程', fontsize=15, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存2D象限视图：{output_path}")
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_visualizations_optimized"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 生成优化版3D轨迹可视化...")
    print("核心优化：象限概念清晰，原点在右上，起点在左下\n")
    
    # 加载数据
    all_data = load_all_trajectories(results_dir)
    print(f"✅ 已加载 {len(all_data)} 个案例\n")
    
    # 生成优化版图表
    print("📊 生成可视化图表...\n")
    
    # 主图：优化版概览
    plot_overview_optimized(all_data, output_dir / "overview_optimized.png")
    
    # 辅助图：2D象限视图
    plot_quadrant_view_2d(all_data, output_dir / "quadrant_view_2d.png")
    
    print(f"\n✅ 优化版可视化图表已生成！")
    print(f"📁 保存位置: {output_dir}\n")
    print("生成的图表:")
    print("  1. overview_optimized.png - 优化版3D概览（象限清晰）")
    print("  2. quadrant_view_2d.png - 2D象限视图（三个平面）")

if __name__ == "__main__":
    main()

