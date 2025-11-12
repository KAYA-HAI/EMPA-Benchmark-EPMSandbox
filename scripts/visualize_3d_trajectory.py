#!/usr/bin/env python3
"""
3D共情轨迹可视化

实现四种可视化方案：
- 方案二：多案例轨迹对比图
- 方案三：起点-终点散点聚类图  
- 方案四：轨迹密度热力图
- 方案五：轴向投影分解图
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
            
        # 提取关键信息
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
            trajectory = data['epj']['trajectory']
            P_0 = data['epj']['P_0_initial_deficit']
            P_final = data['epj']['P_final_position']
            
            # 如果是字符串，则需要eval
            if isinstance(P_0, str):
                P_0 = eval(P_0)
            if isinstance(P_final, str):
                P_final = eval(P_final)
            
            # 提取所有轨迹点
            trajectory_points = []
            for point in trajectory:
                P_t = point['P_t']
                trajectory_points.append(P_t)
            
            all_data.append({
                'script_id': script_id,
                'total_turns': total_turns,
                'status': status,
                'P_0': P_0,
                'P_final': P_final,
                'trajectory': trajectory_points
            })
    
    return all_data

def draw_epsilon_sphere(ax, radius=1.0, alpha=0.1):
    """绘制epsilon目标球"""
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 20)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='green', alpha=alpha, edgecolor='none')

def plot_scheme2_multi_trajectory(all_data, output_path):
    """方案二：多案例轨迹对比图"""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 颜色映射
    color_map = {
        'success': ('#4ECDC4', 'o', '正常完成'),
        'max_turns': ('#FFE66D', 's', '达到最大轮次'),
        'failure': ('#FF6B6B', '^', 'EPM失败')
    }
    
    # 绘制epsilon球
    draw_epsilon_sphere(ax, radius=1.0, alpha=0.15)
    
    # 绘制原点
    ax.scatter([0], [0], [0], c='black', s=100, marker='*', label='原点(0,0,0)', zorder=10)
    
    # 按状态分组绘制
    for status_key, (color, marker, label) in color_map.items():
        status_data = [d for d in all_data if d['status'] == status_key]
        
        if not status_data:
            continue
        
        # 绘制起点
        P_0_list = [d['P_0'] for d in status_data]
        if P_0_list:
            C_0 = [p[0] for p in P_0_list]
            A_0 = [p[1] for p in P_0_list]
            P_0_val = [p[2] for p in P_0_list]
            ax.scatter(C_0, A_0, P_0_val, c=color, s=50, marker=marker, 
                      alpha=0.6, edgecolors='black', linewidths=0.5)
        
        # 绘制轨迹箭头（从起点到终点）
        for d in status_data:
            P_0 = d['P_0']
            P_final = d['P_final']
            
            # 线条粗细与轮次成正比
            linewidth = min(0.5 + d['total_turns'] / 20, 3.0)
            
            ax.plot([P_0[0], P_final[0]], 
                   [P_0[1], P_final[1]], 
                   [P_0[2], P_final[2]], 
                   color=color, linewidth=linewidth, alpha=0.5)
            
            # 终点标记
            ax.scatter([P_final[0]], [P_final[1]], [P_final[2]], 
                      c=color, s=80, marker='*', alpha=0.8, 
                      edgecolors='black', linewidths=0.5)
    
    # 添加图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=color, linewidth=2, label=f'{label} ({len([d for d in all_data if d["status"] == status])}个)')
        for status, (color, _, label) in color_map.items()
    ]
    legend_elements.append(Line2D([0], [0], marker='*', color='w', 
                                  markerfacecolor='black', markersize=10, label='原点'))
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    # 设置坐标轴
    ax.set_xlabel('认知轴 (C)', fontsize=11, fontweight='bold')
    ax.set_ylabel('情感轴 (A)', fontsize=11, fontweight='bold')
    ax.set_zlabel('动机轴 (P)', fontsize=11, fontweight='bold')
    ax.set_title('方案二：多案例共情轨迹对比图（起点→终点）', fontsize=13, fontweight='bold', pad=20)
    
    # 设置视角
    ax.view_init(elev=20, azim=45)
    
    # 添加网格
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存方案二：{output_path}")
    plt.close()

def plot_scheme3_start_end_scatter(all_data, output_path):
    """方案三：起点-终点散点聚类图"""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 绘制epsilon球
    draw_epsilon_sphere(ax, radius=1.0, alpha=0.15)
    
    # 绘制原点
    ax.scatter([0], [0], [0], c='black', s=150, marker='*', label='原点(0,0,0)', zorder=10)
    
    # 所有起点（蓝色）
    P_0_list = [d['P_0'] for d in all_data]
    C_0 = [p[0] for p in P_0_list]
    A_0 = [p[1] for p in P_0_list]
    P_0_val = [p[2] for p in P_0_list]
    ax.scatter(C_0, A_0, P_0_val, c='#3498db', s=100, marker='o', 
              alpha=0.7, edgecolors='black', linewidths=1, label='初始位置 P₀')
    
    # 所有终点（红色）
    P_final_list = [d['P_final'] for d in all_data]
    C_final = [p[0] for p in P_final_list]
    A_final = [p[1] for p in P_final_list]
    P_final_val = [p[2] for p in P_final_list]
    ax.scatter(C_final, A_final, P_final_val, c='#e74c3c', s=100, marker='s', 
              alpha=0.7, edgecolors='black', linewidths=1, label='最终位置 P_final')
    
    # 绘制箭头连接起点和终点
    for d in all_data:
        P_0 = d['P_0']
        P_final = d['P_final']
        
        # 根据状态选择箭头颜色
        if d['status'] == 'success':
            arrow_color = '#2ecc71'
            alpha_val = 0.4
        elif d['status'] == 'max_turns':
            arrow_color = '#f39c12'
            alpha_val = 0.5
        else:
            arrow_color = '#e74c3c'
            alpha_val = 0.6
        
        ax.plot([P_0[0], P_final[0]], 
               [P_0[1], P_final[1]], 
               [P_0[2], P_final[2]], 
               color=arrow_color, linewidth=1, alpha=alpha_val, linestyle='--')
    
    ax.legend(loc='upper left', fontsize=11)
    ax.set_xlabel('认知轴 (C)', fontsize=11, fontweight='bold')
    ax.set_ylabel('情感轴 (A)', fontsize=11, fontweight='bold')
    ax.set_zlabel('动机轴 (P)', fontsize=11, fontweight='bold')
    ax.set_title('方案三：起点-终点散点聚类图（30个案例）', fontsize=13, fontweight='bold', pad=20)
    ax.view_init(elev=20, azim=45)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存方案三：{output_path}")
    plt.close()

def plot_scheme4_density_heatmap(all_data, output_path):
    """方案四：轨迹密度热力图"""
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # 收集所有轨迹点
    all_points = []
    for d in all_data:
        all_points.extend(d['trajectory'])
    
    C_all = [p[0] for p in all_points]
    A_all = [p[1] for p in all_points]
    P_all = [p[2] for p in all_points]
    
    # 创建3D直方图（密度统计）
    # 定义空间范围
    C_range = (min(C_all) - 2, max(C_all) + 2)
    A_range = (min(A_all) - 2, max(A_all) + 2)
    P_range = (min(P_all) - 2, max(P_all) + 2)
    
    # 创建3D直方图
    hist, edges = np.histogramdd(
        np.array([C_all, A_all, P_all]).T,
        bins=(10, 10, 10),
        range=[C_range, A_range, P_range]
    )
    
    # 找到非零的bin
    C_edges, A_edges, P_edges = edges
    C_centers = (C_edges[:-1] + C_edges[1:]) / 2
    A_centers = (A_edges[:-1] + A_edges[1:]) / 2
    P_centers = (P_edges[:-1] + P_edges[1:]) / 2
    
    # 绘制密度点
    for i in range(len(C_centers)):
        for j in range(len(A_centers)):
            for k in range(len(P_centers)):
                count = hist[i, j, k]
                if count > 0:
                    # 颜色和大小与密度成正比
                    size = min(20 + count * 10, 200)
                    alpha = min(0.3 + count * 0.05, 0.9)
                    color = plt.cm.YlOrRd(count / hist.max())
                    
                    ax.scatter([C_centers[i]], [A_centers[j]], [P_centers[k]], 
                             c=[color], s=size, alpha=alpha, edgecolors='none')
    
    # 绘制epsilon球
    draw_epsilon_sphere(ax, radius=1.0, alpha=0.1)
    
    # 绘制原点
    ax.scatter([0], [0], [0], c='black', s=150, marker='*', label='原点', zorder=10)
    
    # 添加颜色条
    sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=plt.Normalize(vmin=0, vmax=hist.max()))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.5, aspect=10)
    cbar.set_label('轨迹点密度', fontsize=10, fontweight='bold')
    
    ax.legend(loc='upper left', fontsize=11)
    ax.set_xlabel('认知轴 (C)', fontsize=11, fontweight='bold')
    ax.set_ylabel('情感轴 (A)', fontsize=11, fontweight='bold')
    ax.set_zlabel('动机轴 (P)', fontsize=11, fontweight='bold')
    ax.set_title('方案四：轨迹密度热力图（空间分布）', fontsize=13, fontweight='bold', pad=20)
    ax.view_init(elev=20, azim=45)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存方案四：{output_path}")
    plt.close()

def plot_scheme5_axis_projections(all_data, output_path):
    """方案五：轴向投影分解图"""
    fig = plt.figure(figsize=(18, 6))
    
    # 颜色映射
    color_map = {
        'success': '#4ECDC4',
        'max_turns': '#FFE66D',
        'failure': '#FF6B6B'
    }
    
    # 子图1: C-A平面
    ax1 = fig.add_subplot(131)
    for d in all_data:
        color = color_map[d['status']]
        P_0 = d['P_0']
        P_final = d['P_final']
        
        # 绘制轨迹
        ax1.plot([P_0[0], P_final[0]], [P_0[1], P_final[1]], 
                color=color, alpha=0.4, linewidth=1)
        
        # 起点和终点
        ax1.scatter([P_0[0]], [P_0[1]], c=color, s=30, marker='o', alpha=0.6, edgecolors='black', linewidths=0.5)
        ax1.scatter([P_final[0]], [P_final[1]], c=color, s=50, marker='*', alpha=0.8, edgecolors='black', linewidths=0.5)
    
    # epsilon圆（在C-A平面的投影）
    theta = np.linspace(0, 2*np.pi, 100)
    ax1.plot(np.cos(theta), np.sin(theta), 'g--', alpha=0.3, linewidth=2, label='epsilon球投影')
    ax1.scatter([0], [0], c='black', s=100, marker='*', label='原点', zorder=10)
    
    ax1.set_xlabel('认知轴 (C)', fontsize=10, fontweight='bold')
    ax1.set_ylabel('情感轴 (A)', fontsize=10, fontweight='bold')
    ax1.set_title('C-A平面投影', fontsize=11, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', fontsize=8)
    ax1.set_aspect('equal', adjustable='box')
    
    # 子图2: C-P平面
    ax2 = fig.add_subplot(132)
    for d in all_data:
        color = color_map[d['status']]
        P_0 = d['P_0']
        P_final = d['P_final']
        
        ax2.plot([P_0[0], P_final[0]], [P_0[2], P_final[2]], 
                color=color, alpha=0.4, linewidth=1)
        ax2.scatter([P_0[0]], [P_0[2]], c=color, s=30, marker='o', alpha=0.6, edgecolors='black', linewidths=0.5)
        ax2.scatter([P_final[0]], [P_final[2]], c=color, s=50, marker='*', alpha=0.8, edgecolors='black', linewidths=0.5)
    
    ax2.plot(np.cos(theta), np.sin(theta), 'g--', alpha=0.3, linewidth=2, label='epsilon球投影')
    ax2.scatter([0], [0], c='black', s=100, marker='*', label='原点', zorder=10)
    
    ax2.set_xlabel('认知轴 (C)', fontsize=10, fontweight='bold')
    ax2.set_ylabel('动机轴 (P)', fontsize=10, fontweight='bold')
    ax2.set_title('C-P平面投影', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', fontsize=8)
    ax2.set_aspect('equal', adjustable='box')
    
    # 子图3: A-P平面
    ax3 = fig.add_subplot(133)
    for d in all_data:
        color = color_map[d['status']]
        P_0 = d['P_0']
        P_final = d['P_final']
        
        ax3.plot([P_0[1], P_final[1]], [P_0[2], P_final[2]], 
                color=color, alpha=0.4, linewidth=1)
        ax3.scatter([P_0[1]], [P_0[2]], c=color, s=30, marker='o', alpha=0.6, edgecolors='black', linewidths=0.5)
        ax3.scatter([P_final[1]], [P_final[2]], c=color, s=50, marker='*', alpha=0.8, edgecolors='black', linewidths=0.5)
    
    ax3.plot(np.cos(theta), np.sin(theta), 'g--', alpha=0.3, linewidth=2, label='epsilon球投影')
    ax3.scatter([0], [0], c='black', s=100, marker='*', label='原点', zorder=10)
    
    ax3.set_xlabel('情感轴 (A)', fontsize=10, fontweight='bold')
    ax3.set_ylabel('动机轴 (P)', fontsize=10, fontweight='bold')
    ax3.set_title('A-P平面投影', fontsize=11, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    ax3.legend(loc='best', fontsize=8)
    ax3.set_aspect('equal', adjustable='box')
    
    # 添加总标题
    fig.suptitle('方案五：轴向投影分解图（三个平面视图）', fontsize=13, fontweight='bold')
    
    # 添加颜色图例
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#4ECDC4', label='正常完成'),
        Patch(facecolor='#FFE66D', label='达到最大轮次'),
        Patch(facecolor='#FF6B6B', label='EPM失败')
    ]
    fig.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 0.96), 
              ncol=3, fontsize=10, frameon=True)
    
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存方案五：{output_path}")
    plt.close()

def print_trajectory_statistics(all_data):
    """打印轨迹统计信息"""
    print("\n" + "="*70)
    print("📊 3D轨迹统计分析")
    print("="*70)
    
    # 基本统计
    print(f"\n总案例数: {len(all_data)}个")
    success_count = len([d for d in all_data if d['status'] == 'success'])
    max_turns_count = len([d for d in all_data if d['status'] == 'max_turns'])
    failure_count = len([d for d in all_data if d['status'] == 'failure'])
    
    print(f"  ✅ 正常完成: {success_count}个 ({success_count/len(all_data)*100:.1f}%)")
    print(f"  ⚠️ 达到最大轮次: {max_turns_count}个 ({max_turns_count/len(all_data)*100:.1f}%)")
    print(f"  ❌ EPM失败: {failure_count}个 ({failure_count/len(all_data)*100:.1f}%)")
    
    # 空间统计
    print(f"\n📍 空间分布统计:")
    
    # 初始位置范围
    C_0_list = [d['P_0'][0] for d in all_data]
    A_0_list = [d['P_0'][1] for d in all_data]
    P_0_list = [d['P_0'][2] for d in all_data]
    
    print(f"  初始位置 P₀ 范围:")
    print(f"    C轴: [{min(C_0_list)}, {max(C_0_list)}]")
    print(f"    A轴: [{min(A_0_list)}, {max(A_0_list)}]")
    print(f"    P轴: [{min(P_0_list)}, {max(P_0_list)}]")
    
    # 最终位置范围
    C_final_list = [d['P_final'][0] for d in all_data]
    A_final_list = [d['P_final'][1] for d in all_data]
    P_final_list = [d['P_final'][2] for d in all_data]
    
    print(f"\n  最终位置 P_final 范围:")
    print(f"    C轴: [{min(C_final_list)}, {max(C_final_list)}]")
    print(f"    A轴: [{min(A_final_list)}, {max(A_final_list)}]")
    print(f"    P轴: [{min(P_final_list)}, {max(P_final_list)}]")
    
    # 计算平均迁移距离
    distances = []
    for d in all_data:
        P_0 = np.array(d['P_0'])
        P_final = np.array(d['P_final'])
        dist = np.linalg.norm(P_final - P_0)
        distances.append(dist)
    
    print(f"\n📏 迁移距离统计:")
    print(f"  平均迁移距离: {np.mean(distances):.2f}")
    print(f"  最大迁移距离: {max(distances):.2f}")
    print(f"  最小迁移距离: {min(distances):.2f}")
    
    # 各轴的平均进展
    C_progress = [d['P_final'][0] - d['P_0'][0] for d in all_data]
    A_progress = [d['P_final'][1] - d['P_0'][1] for d in all_data]
    P_progress = [d['P_final'][2] - d['P_0'][2] for d in all_data]
    
    print(f"\n📈 各轴平均进展:")
    print(f"  C轴: {np.mean(C_progress):+.2f} (正向进展案例: {len([p for p in C_progress if p > 0])}个)")
    print(f"  A轴: {np.mean(A_progress):+.2f} (正向进展案例: {len([p for p in A_progress if p > 0])}个)")
    print(f"  P轴: {np.mean(P_progress):+.2f} (正向进展案例: {len([p for p in P_progress if p > 0])}个)")
    
    print("\n" + "="*70)

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_visualizations"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 开始生成3D轨迹可视化...")
    
    # 加载数据
    print(f"\n📂 加载轨迹数据...")
    all_data = load_all_trajectories(results_dir)
    print(f"✅ 已加载 {len(all_data)} 个案例的轨迹数据")
    
    # 打印统计信息
    print_trajectory_statistics(all_data)
    
    # 生成各个方案的可视化
    print(f"\n📊 生成可视化图表...")
    
    # 方案二
    plot_scheme2_multi_trajectory(all_data, output_dir / "scheme2_multi_trajectory.png")
    
    # 方案三
    plot_scheme3_start_end_scatter(all_data, output_dir / "scheme3_start_end_scatter.png")
    
    # 方案四
    plot_scheme4_density_heatmap(all_data, output_dir / "scheme4_density_heatmap.png")
    
    # 方案五
    plot_scheme5_axis_projections(all_data, output_dir / "scheme5_axis_projections.png")
    
    print(f"\n✅ 所有可视化图表已生成完成！")
    print(f"📁 保存位置: {output_dir}")
    print(f"\n生成的图表:")
    print(f"  1. scheme2_multi_trajectory.png - 多案例轨迹对比图")
    print(f"  2. scheme3_start_end_scatter.png - 起点-终点散点聚类图")
    print(f"  3. scheme4_density_heatmap.png - 轨迹密度热力图")
    print(f"  4. scheme5_axis_projections.png - 轴向投影分解图")

if __name__ == "__main__":
    main()

