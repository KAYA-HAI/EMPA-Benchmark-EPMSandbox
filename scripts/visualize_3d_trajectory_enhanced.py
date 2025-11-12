#!/usr/bin/env python3
"""
增强版3D轨迹可视化 - 借鉴3D高斯拟合的可视化方法

核心改进：
1. 明确标记起点和终点（大小、颜色、标签）
2. 绘制坐标平面（x=0, y=0, z=0）来清晰展示象限
3. 使用渐变色表示轨迹方向（从起点到终点）
4. 使用管状轨迹（tube plot）使路径更立体
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.colors import LinearSegmentedColormap
from scipy.interpolate import splprep, splev
from pathlib import Path

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
matplotlib.rcParams['axes.unicode_minus'] = False

def load_full_trajectories(results_dir):
    """加载所有案例的完整轨迹数据"""
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
            trajectory = data['epj']['trajectory']
            
            positions = []
            for point in trajectory:
                P_t = point['P_t']
                if isinstance(P_t, str):
                    P_t = eval(P_t)
                positions.append(P_t)
            
            if len(positions) > 1:
                all_data.append({
                    'script_id': script_id,
                    'total_turns': total_turns,
                    'status': status,
                    'positions': np.array(positions),
                    'P_0': positions[0],
                    'P_final': positions[-1]
                })
    
    return all_data

def smooth_trajectory(positions, smoothing_factor=1.0):
    """使用B样条曲线平滑轨迹"""
    if len(positions) < 4:
        return positions
    
    x, y, z = positions[:, 0], positions[:, 1], positions[:, 2]
    
    try:
        tck, u = splprep([x, y, z], s=smoothing_factor, k=min(3, len(positions)-1))
        u_fine = np.linspace(0, 1, len(positions) * 3)
        x_smooth, y_smooth, z_smooth = splev(u_fine, tck)
        return np.column_stack([x_smooth, y_smooth, z_smooth])
    except:
        return positions

def draw_coordinate_planes(ax, size=30, alpha=0.15):
    """绘制三个坐标平面来划分象限"""
    grid_size = 2
    
    # XY平面 (z=0)
    xx, yy = np.meshgrid(np.linspace(-size, size, grid_size), 
                         np.linspace(-size, size, grid_size))
    zz = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=alpha, color='lightblue', 
                   edgecolor='blue', linewidth=0.5, shade=False)
    
    # XZ平面 (y=0)
    xx, zz = np.meshgrid(np.linspace(-size, size, grid_size), 
                         np.linspace(-size, size, grid_size))
    yy = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=alpha, color='lightgreen', 
                   edgecolor='green', linewidth=0.5, shade=False)
    
    # YZ平面 (x=0)
    yy, zz = np.meshgrid(np.linspace(-size, size, grid_size), 
                         np.linspace(-size, size, grid_size))
    xx = np.zeros_like(yy)
    ax.plot_surface(xx, yy, zz, alpha=alpha, color='lightyellow', 
                   edgecolor='orange', linewidth=0.5, shade=False)

def plot_trajectory_with_gradient(ax, positions, status='success', alpha=0.7):
    """
    绘制带渐变色的轨迹（从起点到终点颜色变化）
    
    参数:
        positions: 轨迹点数组
        status: 'success' 或 'failure'
        alpha: 透明度
    """
    # 定义颜色
    if status == 'success':
        color_start = '#95a5a6'  # 灰色（起点）
        color_end = '#27ae60'    # 绿色（终点）
    else:
        color_start = '#95a5a6'  # 灰色（起点）
        color_end = '#e74c3c'    # 红色（终点）
    
    # 创建线段集合，每段有不同颜色
    points = positions.reshape(-1, 1, 3)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # 创建颜色渐变
    n_segments = len(segments)
    colors = []
    for i in range(n_segments):
        t = i / n_segments
        # 线性插值颜色
        r1, g1, b1 = int(color_start[1:3], 16), int(color_start[3:5], 16), int(color_start[5:7], 16)
        r2, g2, b2 = int(color_end[1:3], 16), int(color_end[3:5], 16), int(color_end[5:7], 16)
        
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        
        colors.append(f'#{r:02x}{g:02x}{b:02x}')
    
    # 绘制渐变色线段
    for i, segment in enumerate(segments):
        ax.plot(segment[:, 0], segment[:, 1], segment[:, 2],
               color=colors[i], linewidth=2.5, alpha=alpha)

def plot_enhanced_trajectories(all_data, output_path, use_smooth=False):
    """
    增强版轨迹可视化
    
    参数:
        use_smooth: 是否使用平滑轨迹
    """
    fig = plt.figure(figsize=(22, 18))
    ax = fig.add_subplot(111, projection='3d')
    
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    # 1. 绘制坐标平面
    draw_coordinate_planes(ax, size=30, alpha=0.15)
    
    # 2. 绘制坐标轴线（加强版）
    axis_limit = 30
    # 正半轴（实线）
    ax.plot([0, axis_limit], [0, 0], [0, 0], 'r-', linewidth=2.5, alpha=0.4, label='C轴')
    ax.plot([0, 0], [0, axis_limit], [0, 0], 'g-', linewidth=2.5, alpha=0.4, label='A轴')
    ax.plot([0, 0], [0, 0], [0, axis_limit], 'b-', linewidth=2.5, alpha=0.4, label='P轴')
    # 负半轴（虚线）
    ax.plot([-axis_limit, 0], [0, 0], [0, 0], 'r--', linewidth=2, alpha=0.4)
    ax.plot([0, 0], [-axis_limit, 0], [0, 0], 'g--', linewidth=2, alpha=0.4)
    ax.plot([0, 0], [0, 0], [-axis_limit, 0], 'b--', linewidth=2, alpha=0.4)
    
    # 3. 绘制成功轨迹
    for d in success_data:
        positions = d['positions']
        if use_smooth:
            positions = smooth_trajectory(positions, smoothing_factor=1.5)
        
        # 绘制轨迹（渐变色）
        plot_trajectory_with_gradient(ax, positions, status='success', alpha=0.6)
        
        # 标记起点（灰色圆点，带黑色边框）
        ax.scatter([d['P_0'][0]], [d['P_0'][1]], [d['P_0'][2]],
                  c='#7f8c8d', s=200, marker='o', alpha=0.8, 
                  edgecolors='black', linewidths=2, zorder=10, label='_nolegend_')
        
        # 标记终点（绿色三角形，带深绿边框）
        ax.scatter([d['P_final'][0]], [d['P_final'][1]], [d['P_final'][2]],
                  c='#27ae60', s=250, marker='^', alpha=0.95, 
                  edgecolors='darkgreen', linewidths=2.5, zorder=11, label='_nolegend_')
    
    # 4. 绘制失败轨迹
    for d in failure_data:
        positions = d['positions']
        if use_smooth:
            positions = smooth_trajectory(positions, smoothing_factor=1.5)
        
        # 绘制轨迹（渐变色）
        plot_trajectory_with_gradient(ax, positions, status='failure', alpha=0.8)
        
        # 标记起点（灰色圆点）
        ax.scatter([d['P_0'][0]], [d['P_0'][1]], [d['P_0'][2]],
                  c='#7f8c8d', s=200, marker='o', alpha=0.8, 
                  edgecolors='black', linewidths=2, zorder=10, label='_nolegend_')
        
        # 标记终点（红色叉号，带深红边框）
        ax.scatter([d['P_final'][0]], [d['P_final'][1]], [d['P_final'][2]],
                  c='#e74c3c', s=300, marker='X', alpha=0.95, 
                  edgecolors='darkred', linewidths=3, zorder=11, label='_nolegend_')
    
    # 5. 绘制原点（目标，超大金色星星）
    ax.scatter([0], [0], [0], c='gold', s=800, marker='*', 
              edgecolors='orange', linewidths=5, zorder=100,
              label='目标：原点(0,0,0)')
    
    # 添加原点文本标注
    ax.text(0, 0, 0, '  ★ 目标\n  (0,0,0)', fontsize=12, fontweight='bold',
           color='darkred', ha='left', va='bottom', zorder=101)
    
    # 6. 坐标轴设置
    ax.set_xlabel('认知轴 (C)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_ylabel('情感轴 (A)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_zlabel('动机轴 (P)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    
    title_suffix = '（平滑拟合）' if use_smooth else '（真实轨迹）'
    ax.set_title(f'增强版3D轨迹可视化{title_suffix}\n起点→终点渐变色 | 坐标平面划分象限', 
                fontsize=18, fontweight='bold', pad=25)
    
    # 7. 设置视角和范围
    ax.view_init(elev=25, azim=225)
    max_range = 30
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    # 反转坐标轴（让原点在右上角）
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()
    
    ax.grid(True, alpha=0.25, linestyle='--')
    
    # 8. 图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', 
              markersize=20, markeredgecolor='orange', markeredgewidth=2,
              label='目标：原点(0,0,0)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#7f8c8d', 
              markersize=12, markeredgecolor='black', markeredgewidth=1.5,
              label='起点（灰色圆点）'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='#27ae60', 
              markersize=12, markeredgecolor='darkgreen', markeredgewidth=1.5,
              label=f'成功终点（绿色三角，{len(success_data)}条）'),
        Line2D([0], [0], marker='X', color='w', markerfacecolor='#e74c3c', 
              markersize=12, markeredgecolor='darkred', markeredgewidth=1.5,
              label=f'失败终点（红色叉号，{len(failure_data)}条）'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=13, 
             framealpha=0.95, edgecolor='black')
    
    # 添加说明文字
    explanation = (
        '可视化说明：\n'
        '• 坐标平面：蓝色(z=0)、绿色(y=0)、黄色(x=0)\n'
        '• 轨迹颜色：灰色→绿色(成功) / 灰色→红色(失败)\n'
        '• 八个象限由三个平面划分\n'
        '• 目标：所有轨迹汇聚到原点(0,0,0)'
    )
    
    fig.text(0.02, 0.02, explanation, fontsize=11, 
            verticalalignment='bottom', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存增强版可视化：{output_path}")
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_visualizations_enhanced"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 生成增强版3D轨迹可视化...")
    print("改进要点:")
    print("  1. 明确标记起点和终点（不同形状、颜色、大小）")
    print("  2. 绘制坐标平面划分象限")
    print("  3. 使用渐变色表示轨迹方向\n")
    
    # 加载数据
    all_data = load_full_trajectories(results_dir)
    print(f"✅ 已加载 {len(all_data)} 个案例\n")
    
    success_count = len([d for d in all_data if d['status'] == 'success'])
    failure_count = len(all_data) - success_count
    print(f"📊 成功: {success_count}, 失败: {failure_count}\n")
    
    # 生成两个版本
    print("📊 生成可视化图表...\n")
    
    # 版本1: 真实轨迹
    plot_enhanced_trajectories(all_data, output_dir / "enhanced_real_paths.png", 
                               use_smooth=False)
    
    # 版本2: 平滑轨迹
    plot_enhanced_trajectories(all_data, output_dir / "enhanced_smooth_paths.png", 
                               use_smooth=True)
    
    print(f"\n✅ 增强版可视化已生成！")
    print(f"📁 保存位置: {output_dir}\n")
    print("生成的图表:")
    print("  1. enhanced_real_paths.png - 真实轨迹（起终点清晰+象限平面）")
    print("  2. enhanced_smooth_paths.png - 平滑轨迹（起终点清晰+象限平面）")

if __name__ == "__main__":
    main()

