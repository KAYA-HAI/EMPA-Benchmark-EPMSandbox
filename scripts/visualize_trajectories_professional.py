#!/usr/bin/env python3
"""
专业级3D轨迹可视化
探索多种增强空间感的技术
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path
from scipy.interpolate import make_interp_spline
from matplotlib import cm
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# 配置matplotlib
matplotlib.rcParams.update({
    'font.sans-serif': ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC'],
    'axes.unicode_minus': False,
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'lines.antialiased': True,
})

def load_all_trajectories(results_dir):
    """加载所有script的轨迹"""
    results_dir = Path(results_dir)
    all_trajectories = []
    
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
        
        # 提取轨迹点
        if 'epj' in data and 'trajectory' in data['epj']:
            trajectory = data['epj']['trajectory']
            points = np.array([point['P_t'] for point in trajectory])
            
            all_trajectories.append({
                'script_id': script_id,
                'points': points,
                'status': status,
                'total_turns': total_turns
            })
    
    return all_trajectories

def smooth_trajectory(points, num_points=100):
    """使用B-spline平滑轨迹"""
    if len(points) < 4:
        return points
    
    try:
        distances = np.sqrt(np.sum(np.diff(points, axis=0)**2, axis=1))
        cumulative_distances = np.concatenate([[0], np.cumsum(distances)])
        
        if cumulative_distances[-1] > 0:
            t = cumulative_distances / cumulative_distances[-1]
        else:
            return points
        
        t_smooth = np.linspace(0, 1, num_points)
        k = min(3, len(points) - 1)
        
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
        return points

def add_reference_planes(ax, axis_limit):
    """添加半透明参考平面"""
    # XY平面 (z=0)
    xx, yy = np.meshgrid(
        np.linspace(-axis_limit, axis_limit, 10),
        np.linspace(-axis_limit, axis_limit, 10)
    )
    zz = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=0.08, color='gray', 
                   linewidth=0, antialiased=True, zorder=0)
    
    # XZ平面 (y=0)
    xx, zz = np.meshgrid(
        np.linspace(-axis_limit, axis_limit, 10),
        np.linspace(-axis_limit, axis_limit, 10)
    )
    yy = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=0.08, color='gray', 
                   linewidth=0, antialiased=True, zorder=0)
    
    # YZ平面 (x=0)
    yy, zz = np.meshgrid(
        np.linspace(-axis_limit, axis_limit, 10),
        np.linspace(-axis_limit, axis_limit, 10)
    )
    xx = np.zeros_like(yy)
    ax.plot_surface(xx, yy, zz, alpha=0.08, color='gray', 
                   linewidth=0, antialiased=True, zorder=0)

def plot_with_depth_encoding(ax, points, color, is_success, axis_limit):
    """绘制带深度编码的轨迹"""
    smooth_points = smooth_trajectory(points, num_points=100)
    
    # 计算深度因子（基于相机视角）
    # 视角：elev=25, azim=225
    # 距离观察者越近的点应该越粗越明显
    view_angle_rad = np.radians(225)
    view_elev_rad = np.radians(25)
    
    # 简化的深度计算：基于到观察者的近似距离
    # 观察者大致在 (负x, 负y, 正z) 方向
    view_direction = np.array([
        -np.cos(view_elev_rad) * np.sin(view_angle_rad),
        -np.cos(view_elev_rad) * np.cos(view_angle_rad),
        np.sin(view_elev_rad)
    ])
    
    # 计算每个点到视线的投影（深度）
    depths = np.dot(smooth_points, view_direction)
    depth_min, depth_max = depths.min(), depths.max()
    
    if depth_max > depth_min:
        depth_factors = (depths - depth_min) / (depth_max - depth_min)
    else:
        depth_factors = np.ones_like(depths)
    
    # 绘制分段线条，线宽随深度变化
    for i in range(len(smooth_points) - 1):
        # 线宽：远处细(0.5)，近处粗(3.5)
        lw = 0.5 + depth_factors[i] * 3.0
        # 透明度：远处淡(0.15)，近处浓(0.45)
        alpha = 0.15 + depth_factors[i] * 0.30
        
        ax.plot(smooth_points[i:i+2, 0], 
               smooth_points[i:i+2, 1], 
               smooth_points[i:i+2, 2],
               color=color, linewidth=lw, alpha=alpha, 
               solid_capstyle='round', zorder=5)
    
    # 原始点也根据深度调整
    point_depths = np.dot(points, view_direction)
    if depth_max > depth_min:
        point_depth_factors = (point_depths - depth_min) / (depth_max - depth_min)
    else:
        point_depth_factors = np.ones(len(points))
    
    for i, (point, df) in enumerate(zip(points, point_depth_factors)):
        size = 8 + df * 20  # 8-28
        alpha = 0.2 + df * 0.35  # 0.2-0.55
        ax.scatter([point[0]], [point[1]], [point[2]],
                  c=[color], s=size, marker='o', alpha=alpha, 
                  edgecolors='white', linewidths=0.4, zorder=10)

def plot_focused_visualization(trajectories, output_path):
    """方案1: 聚焦式可视化 - 高亮代表性轨迹"""
    fig = plt.figure(figsize=(22, 16), facecolor='white')
    ax = fig.add_subplot(111, projection='3d', facecolor='white')
    
    axis_limit = 35
    
    # 分类
    success_trajs = [t for t in trajectories if t['status'] == 'success']
    failure_trajs = [t for t in trajectories if t['status'] != 'success']
    
    # 添加参考平面
    add_reference_planes(ax, axis_limit)
    
    # 1. 背景轨迹（非聚焦）- 半透明灰色
    print(f"  绘制背景轨迹...")
    for traj in success_trajs[2:]:  # 除了前2条
        points = traj['points']
        smooth_points = smooth_trajectory(points, num_points=100)
        ax.plot(smooth_points[:, 0], smooth_points[:, 1], smooth_points[:, 2],
               color='#cccccc', linewidth=0.8, alpha=0.12, zorder=3)
    
    for traj in failure_trajs[3:]:  # 除了前3条
        points = traj['points']
        smooth_points = smooth_trajectory(points, num_points=100)
        ax.plot(smooth_points[:, 0], smooth_points[:, 1], smooth_points[:, 2],
               color='#cccccc', linewidth=0.8, alpha=0.12, zorder=3)
    
    # 2. 聚焦轨迹 - 高亮显示（带深度编码）
    print(f"  绘制聚焦轨迹（深度编码）...")
    
    # 选择2条成功轨迹高亮
    for i, traj in enumerate(success_trajs[:2]):
        points = traj['points']
        color = '#1f77b4' if i == 0 else '#4A90E2'
        plot_with_depth_encoding(ax, points, color, True, axis_limit)
        
        # 标记起点和终点
        ax.scatter([points[0, 0]], [points[0, 1]], [points[0, 2]],
                  c='#08519c', s=250, marker='o', alpha=0.95, zorder=30,
                  edgecolors='white', linewidths=3.5, label=f'成功案例{i+1}起点' if i == 0 else '')
        ax.scatter([points[-1, 0]], [points[-1, 1]], [points[-1, 2]],
                  c='#238b45', s=320, marker='^', alpha=0.95, zorder=30,
                  edgecolors='white', linewidths=3.5, label=f'成功案例{i+1}终点' if i == 0 else '')
    
    # 选择3条失败轨迹高亮
    for i, traj in enumerate(failure_trajs[:3]):
        points = traj['points']
        colors_list = ['#d62728', '#E24A4A', '#ff7f0e']
        color = colors_list[i]
        plot_with_depth_encoding(ax, points, color, False, axis_limit)
        
        # 标记起点和终点
        ax.scatter([points[0, 0]], [points[0, 1]], [points[0, 2]],
                  c='#08519c', s=250, marker='o', alpha=0.95, zorder=30,
                  edgecolors='white', linewidths=3.5)
        ax.scatter([points[-1, 0]], [points[-1, 1]], [points[-1, 2]],
                  c='#a50f15', s=320, marker='X', alpha=0.95, zorder=30,
                  edgecolors='white', linewidths=3.5, label=f'失败案例{i+1}终点' if i == 0 else '')
    
    # 标记原点
    ax.scatter([0], [0], [0], c='none', s=400, marker='o', 
              edgecolors='#333333', linewidths=3.0, zorder=99, alpha=0.9)
    ax.scatter([0], [0], [0], c='#333333', s=100, marker='o', 
              edgecolors='none', zorder=100, alpha=0.95)
    
    # 坐标轴参考线
    ax.plot([0, axis_limit], [0, 0], [0, 0], color='#d62728', linewidth=2.5, alpha=0.4)
    ax.plot([0, 0], [0, axis_limit], [0, 0], color='#2ca02c', linewidth=2.5, alpha=0.4)
    ax.plot([0, 0], [0, 0], [0, axis_limit], color='#1f77b4', linewidth=2.5, alpha=0.4)
    ax.plot([-axis_limit, 0], [0, 0], [0, 0], color='#d62728', linewidth=1.8, alpha=0.3, linestyle='--')
    ax.plot([0, 0], [-axis_limit, 0], [0, 0], color='#2ca02c', linewidth=1.8, alpha=0.3, linestyle='--')
    ax.plot([0, 0], [0, 0], [-axis_limit, 0], color='#1f77b4', linewidth=1.8, alpha=0.3, linestyle='--')
    
    # 坐标轴设置
    ax.set_xlabel('认知轴 Cognitive (C)\n← 赤字 | 充足 →', 
                  fontsize=13, fontweight='bold', labelpad=22, color='#333333')
    ax.set_ylabel('情感轴 Affective (A)\n← 赤字 | 充足 →', 
                  fontsize=13, fontweight='bold', labelpad=22, color='#333333')
    ax.set_zlabel('动机轴 Proactive (P)\n← 赤字 | 充足 →', 
                  fontsize=13, fontweight='bold', labelpad=32, color='#333333')
    
    ax.set_title('专业3D轨迹可视化 | 方案1: 聚焦式 + 深度编码\n2条成功案例 + 3条失败案例高亮', 
                fontsize=17, fontweight='bold', pad=32, color='#222222')
    
    ax.view_init(elev=25, azim=225)
    ax.set_xlim([-axis_limit, axis_limit])
    ax.set_ylim([-axis_limit, axis_limit])
    ax.set_zlim([-axis_limit, axis_limit])
    
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()
    
    # 网格和背景
    ax.grid(True, alpha=0.2, linestyle='-', linewidth=0.8, color='#cccccc')
    ax.xaxis.pane.fill = True
    ax.yaxis.pane.fill = True
    ax.zaxis.pane.fill = True
    ax.xaxis.pane.set_facecolor('#f8f8f8')
    ax.yaxis.pane.set_facecolor('#f8f8f8')
    ax.zaxis.pane.set_facecolor('#f8f8f8')
    ax.xaxis.pane.set_alpha(0.9)
    ax.yaxis.pane.set_alpha(0.9)
    ax.zaxis.pane.set_alpha(0.9)
    
    # 说明框
    info_text = (
        f'可视化策略\n'
        f'  聚焦高亮: 5条代表性轨迹\n'
        f'    • 2条成功案例（蓝色）\n'
        f'    • 3条失败案例（红/橙色）\n'
        f'  背景轨迹: {len(trajectories)-5}条（灰色半透明）\n'
        f'\n'
        f'深度编码技术\n'
        f'  线宽: 0.5~3.5（远→近）\n'
        f'  透明度: 0.15~0.45（远→近）\n'
        f'  点大小: 8~28（远→近）\n'
        f'\n'
        f'空间参考\n'
        f'  半透明坐标平面（XY/XZ/YZ）\n'
        f'  增强坐标轴线\n'
        f'  目标原点标记\n'
        f'\n'
        f'核心理念\n'
        f'  减少视觉噪音，突出关键路径\n'
        f'  深度编码增强空间感知\n'
        f'  参考平面辅助定位'
    )
    
    fig.text(0.94, 0.97, info_text, fontsize=9, 
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=1.0', facecolor='#fffef8', 
                     edgecolor='#999999', alpha=0.95, linewidth=1.5),
            transform=fig.transFigure, color='#333333', linespacing=1.6)
    
    plt.subplots_adjust(left=0.08, right=0.92, top=0.94, bottom=0.06)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.3)
    print(f"✅ 已保存: {output_path}")
    plt.close()

def plot_multiview_layout(trajectories, output_path):
    """方案2: 多视角布局 - 3D主图 + 三个2D投影"""
    fig = plt.figure(figsize=(24, 20), facecolor='white')
    
    axis_limit = 35
    
    # 分类
    success_trajs = [t for t in trajectories if t['status'] == 'success']
    failure_trajs = [t for t in trajectories if t['status'] != 'success']
    
    # 选择代表性轨迹
    focus_success = success_trajs[:2]
    focus_failure = failure_trajs[:3]
    
    # ========== 1. 主3D图（左上，大） ==========
    ax_3d = fig.add_subplot(2, 2, 1, projection='3d', facecolor='white')
    
    print(f"  绘制主3D图...")
    add_reference_planes(ax_3d, axis_limit)
    
    # 背景轨迹
    for traj in success_trajs[2:]:
        points = traj['points']
        smooth_points = smooth_trajectory(points, num_points=100)
        ax_3d.plot(smooth_points[:, 0], smooth_points[:, 1], smooth_points[:, 2],
                  color='#cccccc', linewidth=0.6, alpha=0.1, zorder=2)
    
    for traj in failure_trajs[3:]:
        points = traj['points']
        smooth_points = smooth_trajectory(points, num_points=100)
        ax_3d.plot(smooth_points[:, 0], smooth_points[:, 1], smooth_points[:, 2],
                  color='#cccccc', linewidth=0.6, alpha=0.1, zorder=2)
    
    # 聚焦轨迹
    for traj in focus_success:
        plot_with_depth_encoding(ax_3d, traj['points'], '#1f77b4', True, axis_limit)
    for i, traj in enumerate(focus_failure):
        colors = ['#d62728', '#E24A4A', '#ff7f0e']
        plot_with_depth_encoding(ax_3d, traj['points'], colors[i], False, axis_limit)
    
    # 原点
    ax_3d.scatter([0], [0], [0], c='gold', s=500, marker='*', 
                 edgecolors='orange', linewidths=3, zorder=100, alpha=0.9)
    
    ax_3d.set_xlabel('认知 (C)', fontsize=11, labelpad=15)
    ax_3d.set_ylabel('情感 (A)', fontsize=11, labelpad=15)
    ax_3d.set_zlabel('动机 (P)', fontsize=11, labelpad=20)
    ax_3d.set_title('主视图: 3D空间全景', fontsize=14, fontweight='bold', pad=20)
    ax_3d.view_init(elev=25, azim=225)
    ax_3d.set_xlim([-axis_limit, axis_limit])
    ax_3d.set_ylim([-axis_limit, axis_limit])
    ax_3d.set_zlim([-axis_limit, axis_limit])
    ax_3d.invert_xaxis()
    ax_3d.invert_yaxis()
    ax_3d.invert_zaxis()
    ax_3d.grid(True, alpha=0.15)
    
    # ========== 2. XY平面投影（右上）==========
    ax_xy = fig.add_subplot(2, 2, 2, facecolor='white')
    
    print(f"  绘制XY投影...")
    for traj in focus_success:
        points = traj['points']
        ax_xy.plot(points[:, 0], points[:, 1], color='#1f77b4', 
                  linewidth=2.0, alpha=0.6, marker='o', markersize=3)
    for i, traj in enumerate(focus_failure):
        points = traj['points']
        colors = ['#d62728', '#E24A4A', '#ff7f0e']
        ax_xy.plot(points[:, 0], points[:, 1], color=colors[i], 
                  linewidth=2.0, alpha=0.6, marker='o', markersize=3)
    
    ax_xy.scatter([0], [0], c='gold', s=300, marker='*', 
                 edgecolors='orange', linewidths=2, zorder=100)
    ax_xy.axhline(0, color='gray', linewidth=1, linestyle='--', alpha=0.5)
    ax_xy.axvline(0, color='gray', linewidth=1, linestyle='--', alpha=0.5)
    ax_xy.set_xlabel('认知轴 (C)', fontsize=11, fontweight='bold')
    ax_xy.set_ylabel('情感轴 (A)', fontsize=11, fontweight='bold')
    ax_xy.set_title('XY平面投影 (俯视图)', fontsize=13, fontweight='bold', pad=15)
    ax_xy.set_xlim([-axis_limit, axis_limit])
    ax_xy.set_ylim([-axis_limit, axis_limit])
    ax_xy.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_xy.set_aspect('equal')
    ax_xy.invert_xaxis()
    ax_xy.invert_yaxis()
    
    # ========== 3. XZ平面投影（左下）==========
    ax_xz = fig.add_subplot(2, 2, 3, facecolor='white')
    
    print(f"  绘制XZ投影...")
    for traj in focus_success:
        points = traj['points']
        ax_xz.plot(points[:, 0], points[:, 2], color='#1f77b4', 
                  linewidth=2.0, alpha=0.6, marker='o', markersize=3)
    for i, traj in enumerate(focus_failure):
        points = traj['points']
        colors = ['#d62728', '#E24A4A', '#ff7f0e']
        ax_xz.plot(points[:, 0], points[:, 2], color=colors[i], 
                  linewidth=2.0, alpha=0.6, marker='o', markersize=3)
    
    ax_xz.scatter([0], [0], c='gold', s=300, marker='*', 
                 edgecolors='orange', linewidths=2, zorder=100)
    ax_xz.axhline(0, color='gray', linewidth=1, linestyle='--', alpha=0.5)
    ax_xz.axvline(0, color='gray', linewidth=1, linestyle='--', alpha=0.5)
    ax_xz.set_xlabel('认知轴 (C)', fontsize=11, fontweight='bold')
    ax_xz.set_ylabel('动机轴 (P)', fontsize=11, fontweight='bold')
    ax_xz.set_title('XZ平面投影 (侧视图)', fontsize=13, fontweight='bold', pad=15)
    ax_xz.set_xlim([-axis_limit, axis_limit])
    ax_xz.set_ylim([-axis_limit, axis_limit])
    ax_xz.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_xz.set_aspect('equal')
    ax_xz.invert_xaxis()
    ax_xz.invert_yaxis()
    
    # ========== 4. YZ平面投影（右下）==========
    ax_yz = fig.add_subplot(2, 2, 4, facecolor='white')
    
    print(f"  绘制YZ投影...")
    for traj in focus_success:
        points = traj['points']
        ax_yz.plot(points[:, 1], points[:, 2], color='#1f77b4', 
                  linewidth=2.0, alpha=0.6, marker='o', markersize=3, label='成功案例')
    for i, traj in enumerate(focus_failure):
        points = traj['points']
        colors = ['#d62728', '#E24A4A', '#ff7f0e']
        ax_yz.plot(points[:, 1], points[:, 2], color=colors[i], 
                  linewidth=2.0, alpha=0.6, marker='o', markersize=3, 
                  label=f'失败案例{i+1}' if i == 0 else '')
    
    ax_yz.scatter([0], [0], c='gold', s=300, marker='*', 
                 edgecolors='orange', linewidths=2, zorder=100, label='目标原点')
    ax_yz.axhline(0, color='gray', linewidth=1, linestyle='--', alpha=0.5)
    ax_yz.axvline(0, color='gray', linewidth=1, linestyle='--', alpha=0.5)
    ax_yz.set_xlabel('情感轴 (A)', fontsize=11, fontweight='bold')
    ax_yz.set_ylabel('动机轴 (P)', fontsize=11, fontweight='bold')
    ax_yz.set_title('YZ平面投影 (正视图)', fontsize=13, fontweight='bold', pad=15)
    ax_yz.set_xlim([-axis_limit, axis_limit])
    ax_yz.set_ylim([-axis_limit, axis_limit])
    ax_yz.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_yz.set_aspect('equal')
    ax_yz.legend(loc='upper right', fontsize=9, framealpha=0.9)
    ax_yz.invert_xaxis()
    ax_yz.invert_yaxis()
    
    # 总标题
    fig.suptitle('专业3D轨迹可视化 | 方案2: 多视角布局\n主3D图 + 三个正交投影', 
                fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.3)
    print(f"✅ 已保存: {output_path}")
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_trajectories_professional"
    output_dir.mkdir(exist_ok=True)
    
    print("🎨 专业级3D轨迹可视化\n")
    
    # 加载数据
    trajectories = load_all_trajectories(results_dir)
    print(f"✅ 已加载 {len(trajectories)} 个案例\n")
    
    # 方案1: 聚焦式可视化
    print("📊 方案1: 聚焦式 + 深度编码")
    plot_focused_visualization(trajectories, output_dir / "focused_depth_encoding.png")
    print()
    
    # 方案2: 多视角布局
    print("📊 方案2: 多视角布局（3D + 三个2D投影）")
    plot_multiview_layout(trajectories, output_dir / "multiview_layout.png")
    print()
    
    print(f"\n✅ 完成！所有图片已保存到:")
    print(f"📁 {output_dir}")
    print("\n💡 对比两种方案:")
    print("   • 方案1: 聚焦式，强调深度感，减少视觉噪音")
    print("   • 方案2: 多视角，全面展示空间关系")

if __name__ == "__main__":
    main()


