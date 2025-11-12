#!/usr/bin/env python3
"""
完整轨迹路径可视化 - 显示真实路径 vs 拟合曲线

方案1: 显示每个对话的真实完整路径（逐点连接）
方案2: 对轨迹点进行平滑拟合（B样条曲线）
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splprep, splev
from pathlib import Path

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
matplotlib.rcParams['axes.unicode_minus'] = False

def load_full_trajectories(results_dir):
    """加载所有案例的完整轨迹数据（包含所有中间点）"""
    results_dir = Path(results_dir)
    all_data = []
    
    for json_file in sorted(results_dir.glob('script_*_result.json')):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        script_id = data['script_id']
        total_turns = data['total_turns']
        termination_reason = data.get('termination_reason', '')
        
        # 判断成功/失败
        if 'EPM' in termination_reason and ('失败' in termination_reason or '负能量' in termination_reason):
            status = 'failure'
        elif total_turns >= 45:
            status = 'max_turns'
        else:
            status = 'success'
        
        # 提取完整轨迹
        if 'epj' in data and 'trajectory' in data['epj']:
            trajectory = data['epj']['trajectory']
            
            # 提取所有位置点
            positions = []
            for point in trajectory:
                P_t = point['P_t']
                if isinstance(P_t, str):
                    P_t = eval(P_t)
                positions.append(P_t)
            
            if len(positions) > 1:  # 至少需要2个点
                all_data.append({
                    'script_id': script_id,
                    'total_turns': total_turns,
                    'status': status,
                    'positions': np.array(positions),  # shape: (n_points, 3)
                    'P_0': positions[0],
                    'P_final': positions[-1]
                })
    
    return all_data

def smooth_trajectory(positions, smoothing_factor=0.5):
    """
    使用B样条曲线对轨迹进行平滑拟合
    
    参数:
        positions: (n, 3) 数组，原始轨迹点
        smoothing_factor: 平滑因子，0=完全不平滑，越大越平滑
    """
    if len(positions) < 4:  # 样条插值至少需要4个点
        return positions
    
    # 转置以适应splprep的输入格式
    x = positions[:, 0]
    y = positions[:, 1]
    z = positions[:, 2]
    
    try:
        # 参数化曲线拟合
        tck, u = splprep([x, y, z], s=smoothing_factor, k=min(3, len(positions)-1))
        
        # 生成更密集的点以获得平滑曲线
        u_fine = np.linspace(0, 1, len(positions) * 5)
        x_smooth, y_smooth, z_smooth = splev(u_fine, tck)
        
        return np.column_stack([x_smooth, y_smooth, z_smooth])
    except:
        # 如果拟合失败，返回原始轨迹
        return positions

def plot_scheme1_real_paths(all_data, output_path):
    """方案1: 显示真实的完整路径（逐点连接）"""
    fig = plt.figure(figsize=(20, 16))
    ax = fig.add_subplot(111, projection='3d')
    
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    # 绘制成功轨迹
    for i, d in enumerate(success_data):
        positions = d['positions']
        
        # 绘制路径
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
               color='#27ae60', linewidth=2, alpha=0.6, linestyle='-')
        
        # 标记起点和终点
        ax.scatter([positions[0, 0]], [positions[0, 1]], [positions[0, 2]],
                  c='gray', s=80, marker='o', alpha=0.5, zorder=5)
        ax.scatter([positions[-1, 0]], [positions[-1, 1]], [positions[-1, 2]],
                  c='#27ae60', s=100, marker='o', alpha=0.9, 
                  edgecolors='darkgreen', linewidths=1.5, zorder=6)
    
    # 绘制失败轨迹
    for d in failure_data:
        positions = d['positions']
        
        # 绘制路径
        ax.plot(positions[:, 0], positions[:, 1], positions[:, 2],
               color='#e74c3c', linewidth=2.5, alpha=0.8, linestyle='--')
        
        # 标记起点和终点
        ax.scatter([positions[0, 0]], [positions[0, 1]], [positions[0, 2]],
                  c='gray', s=80, marker='o', alpha=0.5, zorder=5)
        ax.scatter([positions[-1, 0]], [positions[-1, 1]], [positions[-1, 2]],
                  c='#e74c3c', s=120, marker='X', alpha=0.95, 
                  edgecolors='darkred', linewidths=2, zorder=8)
    
    # 绘制原点（目标）
    ax.scatter([0], [0], [0], c='red', s=600, marker='*', 
              edgecolors='darkred', linewidths=4, zorder=100,
              label='目标：原点(0,0,0)')
    
    # 坐标轴设置
    ax.set_xlabel('认知轴 (C)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_ylabel('情感轴 (A)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_zlabel('动机轴 (P)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    
    ax.set_title('方案1：真实完整路径（逐点连接）\n每条路径显示对话的实际轨迹', 
                fontsize=18, fontweight='bold', pad=25)
    
    # 设置视角和范围
    ax.view_init(elev=25, azim=225)
    max_range = 30
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    # 反转坐标轴
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()
    
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='red', 
              markersize=18, label='目标：原点(0,0,0)'),
        Line2D([0], [0], color='#27ae60', linewidth=3, 
              label=f'成功轨迹 ({len(success_data)}条)'),
        Line2D([0], [0], color='#e74c3c', linewidth=3, linestyle='--',
              label=f'失败轨迹 ({len(failure_data)}条)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=13)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存方案1（真实路径）：{output_path}")
    plt.close()

def plot_scheme2_smooth_paths(all_data, output_path):
    """方案2: 显示平滑拟合后的路径"""
    fig = plt.figure(figsize=(20, 16))
    ax = fig.add_subplot(111, projection='3d')
    
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    # 绘制成功轨迹（平滑版）
    for i, d in enumerate(success_data):
        positions = d['positions']
        smooth_pos = smooth_trajectory(positions, smoothing_factor=1.0)
        
        # 绘制平滑路径
        ax.plot(smooth_pos[:, 0], smooth_pos[:, 1], smooth_pos[:, 2],
               color='#27ae60', linewidth=2.5, alpha=0.7, linestyle='-')
        
        # 标记起点和终点
        ax.scatter([positions[0, 0]], [positions[0, 1]], [positions[0, 2]],
                  c='gray', s=80, marker='o', alpha=0.5, zorder=5)
        ax.scatter([positions[-1, 0]], [positions[-1, 1]], [positions[-1, 2]],
                  c='#27ae60', s=100, marker='o', alpha=0.9, 
                  edgecolors='darkgreen', linewidths=1.5, zorder=6)
    
    # 绘制失败轨迹（平滑版）
    for d in failure_data:
        positions = d['positions']
        smooth_pos = smooth_trajectory(positions, smoothing_factor=1.0)
        
        # 绘制平滑路径
        ax.plot(smooth_pos[:, 0], smooth_pos[:, 1], smooth_pos[:, 2],
               color='#e74c3c', linewidth=3, alpha=0.85, linestyle='-')
        
        # 标记起点和终点
        ax.scatter([positions[0, 0]], [positions[0, 1]], [positions[0, 2]],
                  c='gray', s=80, marker='o', alpha=0.5, zorder=5)
        ax.scatter([positions[-1, 0]], [positions[-1, 1]], [positions[-1, 2]],
                  c='#e74c3c', s=120, marker='X', alpha=0.95, 
                  edgecolors='darkred', linewidths=2, zorder=8)
    
    # 绘制原点（目标）
    ax.scatter([0], [0], [0], c='red', s=600, marker='*', 
              edgecolors='darkred', linewidths=4, zorder=100,
              label='目标：原点(0,0,0)')
    
    # 坐标轴设置
    ax.set_xlabel('认知轴 (C)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_ylabel('情感轴 (A)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_zlabel('动机轴 (P)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    
    ax.set_title('方案2：平滑拟合路径（B样条曲线）\n通过曲线拟合展示轨迹趋势', 
                fontsize=18, fontweight='bold', pad=25)
    
    # 设置视角和范围
    ax.view_init(elev=25, azim=225)
    max_range = 30
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    # 反转坐标轴
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()
    
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 图例
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='*', color='w', markerfacecolor='red', 
              markersize=18, label='目标：原点(0,0,0)'),
        Line2D([0], [0], color='#27ae60', linewidth=3, 
              label=f'成功轨迹 ({len(success_data)}条)'),
        Line2D([0], [0], color='#e74c3c', linewidth=3,
              label=f'失败轨迹 ({len(failure_data)}条)'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=13)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存方案2（平滑路径）：{output_path}")
    plt.close()

def plot_comparison(all_data, output_path):
    """对比图：真实路径 vs 平滑路径（选取几个代表性案例）"""
    # 选择3个成功案例和2个失败案例作为示例
    success_samples = [d for d in all_data if d['status'] == 'success'][:3]
    failure_samples = [d for d in all_data if d['status'] != 'success'][:2]
    samples = success_samples + failure_samples
    
    fig = plt.figure(figsize=(24, 10))
    
    # 左图：真实路径
    ax1 = fig.add_subplot(121, projection='3d')
    
    for d in samples:
        positions = d['positions']
        color = '#27ae60' if d['status'] == 'success' else '#e74c3c'
        linestyle = '-' if d['status'] == 'success' else '--'
        
        ax1.plot(positions[:, 0], positions[:, 1], positions[:, 2],
                color=color, linewidth=2.5, alpha=0.7, linestyle=linestyle)
        
        ax1.scatter([positions[0, 0]], [positions[0, 1]], [positions[0, 2]],
                   c='gray', s=100, marker='o', alpha=0.6)
        ax1.scatter([positions[-1, 0]], [positions[-1, 1]], [positions[-1, 2]],
                   c=color, s=120, marker='o' if d['status'] == 'success' else 'X', 
                   alpha=0.9, edgecolors='black', linewidths=1.5)
    
    ax1.scatter([0], [0], [0], c='red', s=600, marker='*', 
               edgecolors='darkred', linewidths=4, zorder=100)
    
    ax1.set_xlabel('认知轴 (C)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('情感轴 (A)', fontsize=12, fontweight='bold')
    ax1.set_zlabel('动机轴 (P)', fontsize=12, fontweight='bold')
    ax1.set_title('真实路径（逐点连接）', fontsize=16, fontweight='bold', pad=20)
    
    ax1.view_init(elev=25, azim=225)
    ax1.set_xlim([-30, 30])
    ax1.set_ylim([-30, 30])
    ax1.set_zlim([-30, 30])
    ax1.invert_xaxis()
    ax1.invert_yaxis()
    ax1.invert_zaxis()
    ax1.grid(True, alpha=0.3)
    
    # 右图：平滑路径
    ax2 = fig.add_subplot(122, projection='3d')
    
    for d in samples:
        positions = d['positions']
        smooth_pos = smooth_trajectory(positions, smoothing_factor=1.0)
        color = '#27ae60' if d['status'] == 'success' else '#e74c3c'
        linestyle = '-' if d['status'] == 'success' else '--'
        
        ax2.plot(smooth_pos[:, 0], smooth_pos[:, 1], smooth_pos[:, 2],
                color=color, linewidth=2.5, alpha=0.7, linestyle=linestyle)
        
        ax2.scatter([positions[0, 0]], [positions[0, 1]], [positions[0, 2]],
                   c='gray', s=100, marker='o', alpha=0.6)
        ax2.scatter([positions[-1, 0]], [positions[-1, 1]], [positions[-1, 2]],
                   c=color, s=120, marker='o' if d['status'] == 'success' else 'X', 
                   alpha=0.9, edgecolors='black', linewidths=1.5)
    
    ax2.scatter([0], [0], [0], c='red', s=600, marker='*', 
               edgecolors='darkred', linewidths=4, zorder=100)
    
    ax2.set_xlabel('认知轴 (C)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('情感轴 (A)', fontsize=12, fontweight='bold')
    ax2.set_zlabel('动机轴 (P)', fontsize=12, fontweight='bold')
    ax2.set_title('平滑拟合路径（B样条）', fontsize=16, fontweight='bold', pad=20)
    
    ax2.view_init(elev=25, azim=225)
    ax2.set_xlim([-30, 30])
    ax2.set_ylim([-30, 30])
    ax2.set_zlim([-30, 30])
    ax2.invert_xaxis()
    ax2.invert_yaxis()
    ax2.invert_zaxis()
    ax2.grid(True, alpha=0.3)
    
    fig.suptitle(f'方案对比：真实路径 vs 平滑拟合（示例：{len(samples)}个案例）', 
                fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存对比图：{output_path}")
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_visualizations_full_path"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 生成完整轨迹路径可视化...")
    print("方案1: 真实路径（逐点连接）")
    print("方案2: 平滑拟合路径（B样条曲线）\n")
    
    # 加载完整轨迹数据
    all_data = load_full_trajectories(results_dir)
    print(f"✅ 已加载 {len(all_data)} 个案例的完整轨迹\n")
    
    # 统计信息
    success_count = len([d for d in all_data if d['status'] == 'success'])
    failure_count = len(all_data) - success_count
    print(f"📊 成功案例: {success_count}, 失败案例: {failure_count}\n")
    
    # 生成可视化
    print("📊 生成可视化图表...\n")
    
    # 方案1: 真实路径
    plot_scheme1_real_paths(all_data, output_dir / "scheme1_real_paths.png")
    
    # 方案2: 平滑路径
    plot_scheme2_smooth_paths(all_data, output_dir / "scheme2_smooth_paths.png")
    
    # 对比图
    plot_comparison(all_data, output_dir / "comparison_real_vs_smooth.png")
    
    print(f"\n✅ 完整轨迹可视化已生成！")
    print(f"📁 保存位置: {output_dir}\n")
    print("生成的图表:")
    print("  1. scheme1_real_paths.png - 方案1：真实完整路径")
    print("  2. scheme2_smooth_paths.png - 方案2：平滑拟合路径")
    print("  3. comparison_real_vs_smooth.png - 对比图（示例案例）")

if __name__ == "__main__":
    main()


