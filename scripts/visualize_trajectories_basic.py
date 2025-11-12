#!/usr/bin/env python3
"""
最基础的轨迹可视化

就做一件事：把每个script的trajectory中的P_t点画出来并连线
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from scipy.interpolate import make_interp_spline

# 配置matplotlib为专业科研风格（与clustered图保持一致）
matplotlib.rcParams.update({
    # 中文字体设置
    'font.sans-serif': ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC'],
    'axes.unicode_minus': False,
    
    # 专业配色和样式
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'axes.edgecolor': '#cccccc',
    'axes.linewidth': 1.2,
    'axes.grid': True,
    'grid.color': '#e0e0e0',
    'grid.linestyle': '-',
    'grid.linewidth': 0.6,
    'grid.alpha': 0.15,
    
    # 字体和标签样式
    'axes.labelcolor': '#555555',
    'axes.labelweight': 'normal',
    'axes.labelsize': 11,
    'xtick.color': '#555555',
    'ytick.color': '#555555',
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    
    # 图例样式
    'legend.frameon': True,
    'legend.framealpha': 0.9,
    'legend.facecolor': 'white',
    'legend.edgecolor': '#cccccc',
    'legend.fancybox': False,
    'legend.shadow': False,
    
    # 线条样式
    'lines.linewidth': 1.5,
    'lines.antialiased': True,
    'lines.solid_capstyle': 'round',
    'lines.solid_joinstyle': 'round',
})

def load_all_trajectories(results_dir):
    """加载所有script的轨迹和EPM参数"""
    results_dir = Path(results_dir)
    all_trajectories = []
    v_star_0_list = []
    epsilon_list = []
    
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
        
        # 提取轨迹点和EPM参数
        if 'epj' in data and 'trajectory' in data['epj']:
            trajectory = data['epj']['trajectory']
            points = np.array([point['P_t'] for point in trajectory])
            
            # 提取v*_0和epsilon_direction（从第一个点）
            if len(trajectory) > 0 and 'epm' in trajectory[0]:
                epm_data = trajectory[0]['epm']
                if 'v_star_0' in epm_data:
                    v_star_0_list.append(epm_data['v_star_0'])
                if 'epsilon_direction' in epm_data:
                    epsilon_list.append(epm_data['epsilon_direction'])
            
            all_trajectories.append({
                'script_id': script_id,
                'points': points,
                'status': status,
                'total_turns': total_turns
            })
    
    # 计算平均v*_0和epsilon（用于可视化）
    avg_v_star_0 = None
    avg_epsilon = 3.0  # 默认值
    
    if v_star_0_list:
        avg_v_star_0 = np.mean(v_star_0_list, axis=0)
        avg_v_star_0 = avg_v_star_0 / np.linalg.norm(avg_v_star_0)  # 归一化
    
    if epsilon_list:
        avg_epsilon = np.mean(epsilon_list)
    
    return all_trajectories, avg_v_star_0, avg_epsilon

def smooth_trajectory(points, num_points=100):
    """使用B-spline平滑轨迹"""
    if len(points) < 4:
        # 点太少，直接返回原始点
        return points
    
    try:
        # 参数化：使用累积距离
        distances = np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1))
        cumulative_distances = np.concatenate([[0], np.cumsum(distances)])
        
        # 归一化到[0, 1]
        if cumulative_distances[-1] > 0:
            t = cumulative_distances / cumulative_distances[-1]
        else:
            return points
        
        # B-spline插值（k=3表示三次样条）
        t_smooth = np.linspace(0, 1, num_points)
        
        # 对每个维度分别插值
        k = min(3, len(points) - 1)  # 样条阶数不能超过点数-1
        spline_x = make_interp_spline(t, points[:, 0], k=k)
        spline_y = make_interp_spline(t, points[:, 1], k=k)
        spline_z = make_interp_spline(t, points[:, 2], k=k)
        
        smooth_points = np.column_stack([
            spline_x(t_smooth),
            spline_y(t_smooth),
            spline_z(t_smooth)
        ])
        
        return smooth_points
    except:
        # 如果插值失败，返回原始点
        return points

def plot_all_trajectories(trajectories, output_path, v_star_0=None, epsilon=3.0):
    """画出所有轨迹（现代简约风格）"""
    fig = plt.figure(figsize=(20, 14), facecolor='white')
    ax = fig.add_subplot(111, projection='3d', facecolor='white')
    
    # 专业配色方案（降低饱和度的柔和色调）
    success_color = '#6baed6'  # 柔和蓝色（降低饱和度）
    failure_color = '#fb6a4a'  # 柔和红色（降低饱和度）
    
    # 起点和终点使用高对比度颜色（强调）
    start_color = '#08519c'    # 深蓝色（起点）
    success_end_color = '#238b45'  # 深绿色（成功终点）
    failure_end_color = '#a50f15'  # 深红色（失败终点）
    target_color = '#ffd700'   # 金色（目标区域）
    
    # 分类
    success_trajs = [t for t in trajectories if t['status'] == 'success']
    failure_trajs = [t for t in trajectories if t['status'] != 'success']
    
    # 画失败的轨迹（柔和红色，在底层）
    for traj in failure_trajs:
        points = traj['points']
        
        # 画平滑路径（降低饱和度和透明度）
        smooth_points = smooth_trajectory(points, num_points=100)
        ax.plot(smooth_points[:, 0], smooth_points[:, 1], smooth_points[:, 2],
               color=failure_color, linewidth=1.8, alpha=0.25, zorder=5,
               solid_capstyle='round', solid_joinstyle='round')
        
        # 画每一轮的实际点（更小，更透明）
        ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                  c=failure_color, s=18, marker='o', alpha=0.35, zorder=10, 
                  edgecolors='white', linewidths=0.6)
        
        # 标记起点（强调，使用深色）
        ax.scatter([points[0, 0]], [points[0, 1]], [points[0, 2]],
                  c=start_color, s=180, marker='o', alpha=0.95, zorder=25, 
                  edgecolors='white', linewidths=3.0)
        # 标记终点（强调，使用深红色）
        ax.scatter([points[-1, 0]], [points[-1, 1]], [points[-1, 2]],
                  c=failure_end_color, s=250, marker='X', alpha=0.95, zorder=25, 
                  edgecolors='white', linewidths=3.0)
    
    # 画成功的轨迹（柔和蓝色，在上层）
    for traj in success_trajs:
        points = traj['points']
        
        # 画平滑路径（降低饱和度和透明度）
        smooth_points = smooth_trajectory(points, num_points=100)
        ax.plot(smooth_points[:, 0], smooth_points[:, 1], smooth_points[:, 2],
               color=success_color, linewidth=1.8, alpha=0.28, zorder=8,
               solid_capstyle='round', solid_joinstyle='round')
        
        # 画每一轮的实际点（更透明）
        ax.scatter(points[:, 0], points[:, 1], points[:, 2],
                  c=success_color, s=18, marker='o', alpha=0.4, zorder=12, 
                  edgecolors='white', linewidths=0.6)
        
        # 标记起点（强调，使用深色）
        ax.scatter([points[0, 0]], [points[0, 1]], [points[0, 2]],
                  c=start_color, s=180, marker='o', alpha=0.95, zorder=28, 
                  edgecolors='white', linewidths=3.0)
        # 标记终点（强调，使用深绿色）
        ax.scatter([points[-1, 0]], [points[-1, 1]], [points[-1, 2]],
                  c=success_end_color, s=250, marker='^', alpha=0.95, zorder=28, 
                  edgecolors='white', linewidths=3.0)
    
    # 标记原点（空心圆 + 实心点）
    ax.scatter([0], [0], [0], c='none', s=300, marker='o', 
              edgecolors='#333333', linewidths=2.5, zorder=99, alpha=0.9)
    ax.scatter([0], [0], [0], c='#333333', s=80, marker='o', 
              edgecolors='none', zorder=100, alpha=0.95)
    
    # 坐标轴参考线（专业风格，更细腻）
    axis_limit = 35
    ax.plot([0, axis_limit], [0, 0], [0, 0], color='#d62728', linewidth=2.0, alpha=0.35)
    ax.plot([0, 0], [0, axis_limit], [0, 0], color='#2ca02c', linewidth=2.0, alpha=0.35)
    ax.plot([0, 0], [0, 0], [0, axis_limit], color='#1f77b4', linewidth=2.0, alpha=0.35)
    ax.plot([-axis_limit, 0], [0, 0], [0, 0], color='#d62728', linewidth=1.5, alpha=0.25, linestyle='--')
    ax.plot([0, 0], [-axis_limit, 0], [0, 0], color='#2ca02c', linewidth=1.5, alpha=0.25, linestyle='--')
    ax.plot([0, 0], [0, 0], [-axis_limit, 0], color='#1f77b4', linewidth=1.5, alpha=0.25, linestyle='--')
    
    # 设置坐标轴标签（专业风格）
    ax.set_xlabel('认知轴 Cognitive (C)\n← 赤字 Deficit | 充足 Sufficient →', 
                  fontsize=12, fontweight='normal', labelpad=18, color='#555555')
    ax.set_ylabel('情感轴 Affective (A)\n← 赤字 Deficit | 充足 Sufficient →', 
                  fontsize=12, fontweight='normal', labelpad=18, color='#555555')
    ax.set_zlabel('动机轴 Proactive (P)\n← 赤字 Deficit | 充足 Sufficient →', 
                  fontsize=12, fontweight='normal', labelpad=28, color='#555555')
    
    # 设置刻度标签（专业风格）
    ax.tick_params(axis='x', labelsize=9, pad=6, colors='#555555')
    ax.tick_params(axis='y', labelsize=9, pad=6, colors='#555555')
    ax.tick_params(axis='z', labelsize=9, pad=6, colors='#555555')
    
    # 标题（专业风格）
    ax.set_title(f'共情轨迹可视化\n所有{len(trajectories)}个案例的完整轨迹', 
                fontsize=16, fontweight='600', pad=28, color='#333333')
    
    # 设置视角和范围
    ax.view_init(elev=25, azim=225)
    ax.set_xlim([-axis_limit, axis_limit])
    ax.set_ylim([-axis_limit, axis_limit])
    ax.set_zlim([-axis_limit, axis_limit])
    
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()
    
    # 网格和背景（专业风格，更干净）
    ax.grid(True, alpha=0.15, linestyle='-', linewidth=0.6, color='#e0e0e0')
    
    # 设置背景面板
    ax.xaxis.pane.fill = True
    ax.yaxis.pane.fill = True
    ax.zaxis.pane.fill = True
    ax.xaxis.pane.set_facecolor('#fafafa')
    ax.yaxis.pane.set_facecolor('#fafafa')
    ax.zaxis.pane.set_facecolor('#fafafa')
    ax.xaxis.pane.set_alpha(0.8)
    ax.yaxis.pane.set_alpha(0.8)
    ax.zaxis.pane.set_alpha(0.8)
    
    # 设置坐标轴线条颜色
    ax.xaxis.line.set_color('#cccccc')
    ax.yaxis.line.set_color('#cccccc')
    ax.zaxis.line.set_color('#cccccc')
    
    # 图例（专业风格）
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=success_color, linewidth=2.5, alpha=0.6,
               label=f'成功路径 ({len(success_trajs)}条, {len(success_trajs)/len(trajectories)*100:.1f}%)'),
        Line2D([0], [0], color=failure_color, linewidth=2.5, alpha=0.6,
               label=f'失败路径 ({len(failure_trajs)}条, {len(failure_trajs)/len(trajectories)*100:.1f}%)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor=start_color, 
               markersize=10, label='起点（深蓝）', markeredgecolor='white', markeredgewidth=2),
        Line2D([0], [0], marker='^', color='w', markerfacecolor=success_end_color, 
               markersize=11, label='成功终点（深绿）', markeredgecolor='white', markeredgewidth=2),
        Line2D([0], [0], marker='X', color='w', markerfacecolor=failure_end_color, 
               markersize=11, label='失败终点（深红）', markeredgecolor='white', markeredgewidth=2),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#333333', 
               markersize=9, label='目标原点 (0,0,0)', markeredgecolor='#333333', 
               markeredgewidth=1.5, alpha=0.9),
    ]
    legend = ax.legend(handles=legend_elements, loc='upper left', fontsize=10, 
                      framealpha=0.9, edgecolor='#cccccc', fancybox=False, 
                      shadow=False, frameon=True, facecolor='white', 
                      borderpad=1.0, labelspacing=0.6, handlelength=2.0)
    
    # 说明框（专业简约风格）
    info_text = (
        f'样本数据\n'
        f'  总案例数: N = {len(trajectories)}\n'
        f'  成功案例: {len(success_trajs)} ({len(success_trajs)/len(trajectories)*100:.1f}%)\n'
        f'  失败案例: {len(failure_trajs)} ({len(failure_trajs)/len(trajectories)*100:.1f}%)\n'
        f'\n'
        f'可视化方法\n'
        f'  路径平滑: B-spline插值\n'
        f'  采样点数: 100点/轨迹\n'
        f'  路径透明度: 降低以突出端点\n'
        f'\n'
        f'关键标记\n'
        f'  深蓝圆点: 起点（初始赤字）\n'
        f'  深绿三角: 成功终点（达标）\n'
        f'  深红叉号: 失败终点（未达标）\n'
        f'  深灰靶心: 目标原点（零赤字）\n'
        f'\n'
        f'EPM核心概念\n'
        f'  目标: 共情赤字 → 0\n'
        f'  终点越接近原点 = 修复越成功'
    )
    
    fig.text(0.94, 0.96, info_text, fontsize=9, 
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                     edgecolor='#cccccc', alpha=0.95, linewidth=1.2),
            transform=fig.transFigure, color='#555555', linespacing=1.5)
    
    # 使用subplots_adjust精确控制布局
    plt.subplots_adjust(left=0.10, right=0.90, top=0.94, bottom=0.08)
    plt.savefig(output_path, dpi=300)
    print(f"✅ 已保存轨迹图：{output_path}")
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_trajectories_basic"
    output_dir.mkdir(exist_ok=True)
    
    print("🎨 绘制平滑轨迹可视化...")
    print("  • 读取trajectory中每一轮的P_t点")
    print("  • 使用B-spline平滑插值连接点")
    print("  • 标记原点（理想目标）\n")
    
    # 加载所有轨迹和EPM参数
    trajectories, v_star_0, epsilon = load_all_trajectories(results_dir)
    print(f"✅ 已加载 {len(trajectories)} 个案例\n")
    
    # 画图
    print("🎨 绘制轨迹中...\n")
    plot_all_trajectories(trajectories, output_dir / "all_trajectories.png", v_star_0, epsilon)
    
    print(f"\n✅ 完成！")
    print(f"📁 保存位置: {output_dir}")

if __name__ == "__main__":
    main()

