#!/usr/bin/env python3
"""
统计策略路径可视化 - 拟合计算策略路径和影响范围

核心思路：
1. 将所有成功轨迹插值到相同长度
2. 计算平均路径（策略路径的中心线）
3. 计算标准差（影响范围）
4. 用半透明管道表示策略路径的置信区间
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import splprep, splev, interp1d
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

def normalize_trajectory_length(trajectories, n_points=100):
    """
    将所有轨迹插值到相同长度
    
    参数:
        trajectories: 轨迹列表，每个是 (n, 3) 数组
        n_points: 插值后的点数
    
    返回:
        normalized_trajectories: (n_trajectories, n_points, 3) 数组
    """
    normalized = []
    
    for traj in trajectories:
        if len(traj) < 2:
            continue
        
        # 计算累积弧长参数
        distances = np.sqrt(np.sum(np.diff(traj, axis=0)**2, axis=1))
        cum_distances = np.concatenate([[0], np.cumsum(distances)])
        cum_distances = cum_distances / cum_distances[-1]  # 归一化到 [0, 1]
        
        # 对每个维度进行插值
        new_params = np.linspace(0, 1, n_points)
        
        interp_x = interp1d(cum_distances, traj[:, 0], kind='linear')
        interp_y = interp1d(cum_distances, traj[:, 1], kind='linear')
        interp_z = interp1d(cum_distances, traj[:, 2], kind='linear')
        
        new_traj = np.column_stack([
            interp_x(new_params),
            interp_y(new_params),
            interp_z(new_params)
        ])
        
        normalized.append(new_traj)
    
    return np.array(normalized)

def compute_strategy_path(trajectories):
    """
    计算策略路径（平均路径）和影响范围（标准差）
    
    参数:
        trajectories: (n_trajectories, n_points, 3) 数组
    
    返回:
        mean_path: (n_points, 3) 平均路径
        std_path: (n_points, 3) 标准差
    """
    mean_path = np.mean(trajectories, axis=0)
    std_path = np.std(trajectories, axis=0)
    
    return mean_path, std_path

def draw_coordinate_planes(ax, size=30, alpha=0.12):
    """绘制坐标平面"""
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

def draw_tube(ax, path, radius, color='green', alpha=0.3, n_sides=8):
    """
    绘制管状包络（表示影响范围）
    
    参数:
        path: (n_points, 3) 路径点
        radius: (n_points, 3) 每个点的半径（用标准差）
        color: 管道颜色
        alpha: 透明度
        n_sides: 管道的边数
    """
    n_points = len(path)
    
    # 为路径的每一段生成圆形截面
    for i in range(n_points - 1):
        p1, p2 = path[i], path[i + 1]
        r1, r2 = np.mean(radius[i]), np.mean(radius[i + 1])
        
        # 计算方向向量
        direction = p2 - p1
        length = np.linalg.norm(direction)
        
        if length < 1e-6:
            continue
        
        direction = direction / length
        
        # 找到垂直于方向的两个向量
        if abs(direction[0]) < 0.9:
            perpendicular1 = np.cross(direction, [1, 0, 0])
        else:
            perpendicular1 = np.cross(direction, [0, 1, 0])
        
        perpendicular1 = perpendicular1 / np.linalg.norm(perpendicular1)
        perpendicular2 = np.cross(direction, perpendicular1)
        perpendicular2 = perpendicular2 / np.linalg.norm(perpendicular2)
        
        # 生成圆形截面
        theta = np.linspace(0, 2*np.pi, n_sides)
        
        # 两端的圆形截面
        circle1 = np.array([p1 + r1 * (np.cos(t) * perpendicular1 + np.sin(t) * perpendicular2) 
                           for t in theta])
        circle2 = np.array([p2 + r2 * (np.cos(t) * perpendicular1 + np.sin(t) * perpendicular2) 
                           for t in theta])
        
        # 绘制管段
        for j in range(n_sides):
            next_j = (j + 1) % n_sides
            
            # 四边形面片
            verts = [circle1[j], circle1[next_j], circle2[next_j], circle2[j]]
            
            # 转换为绘图格式
            xs = [v[0] for v in verts] + [verts[0][0]]
            ys = [v[1] for v in verts] + [verts[0][1]]
            zs = [v[2] for v in verts] + [verts[0][2]]
            
            ax.plot(xs, ys, zs, color=color, alpha=alpha*0.5, linewidth=0.5)

def draw_confidence_ellipsoid(ax, path, std, color='green', alpha=0.2, stride=5):
    """
    绘制置信椭球（在路径的关键点上）
    
    参数:
        path: (n_points, 3) 路径点
        std: (n_points, 3) 标准差
        stride: 每隔多少个点绘制一个椭球
    """
    from matplotlib.patches import FancyBboxPatch
    
    for i in range(0, len(path), stride):
        center = path[i]
        radii = std[i] * 1.5  # 1.5倍标准差约等于90%置信区间
        
        # 绘制半透明椭球（简化为三个正交的圆）
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 15)
        
        # XY平面圆（z方向的椭球截面）
        x = center[0] + radii[0] * np.outer(np.cos(u), np.sin(v))
        y = center[1] + radii[1] * np.outer(np.sin(u), np.sin(v))
        z = center[2] + radii[2] * np.outer(np.ones(np.size(u)), np.cos(v))
        
        ax.plot_surface(x, y, z, color=color, alpha=alpha*0.5, 
                       edgecolor='none', shade=False)

def plot_statistical_strategy(all_data, output_path):
    """
    绘制统计策略路径图
    """
    fig = plt.figure(figsize=(24, 18))
    ax = fig.add_subplot(111, projection='3d')
    
    # 分离成功和失败轨迹
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    # 1. 绘制坐标平面
    draw_coordinate_planes(ax, size=30, alpha=0.12)
    
    # 2. 绘制坐标轴
    axis_limit = 30
    ax.plot([0, axis_limit], [0, 0], [0, 0], 'r-', linewidth=2.5, alpha=0.4)
    ax.plot([0, 0], [0, axis_limit], [0, 0], 'g-', linewidth=2.5, alpha=0.4)
    ax.plot([0, 0], [0, 0], [0, axis_limit], 'b-', linewidth=2.5, alpha=0.4)
    ax.plot([-axis_limit, 0], [0, 0], [0, 0], 'r--', linewidth=2, alpha=0.4)
    ax.plot([0, 0], [-axis_limit, 0], [0, 0], 'g--', linewidth=2, alpha=0.4)
    ax.plot([0, 0], [0, 0], [-axis_limit, 0], 'b--', linewidth=2, alpha=0.4)
    
    # 3. 处理成功轨迹
    if len(success_data) > 0:
        success_trajectories = [d['positions'] for d in success_data]
        
        # 归一化长度
        normalized_success = normalize_trajectory_length(success_trajectories, n_points=50)
        
        # 计算策略路径和标准差
        mean_path_success, std_path_success = compute_strategy_path(normalized_success)
        
        # 绘制策略路径（粗实线）
        ax.plot(mean_path_success[:, 0], mean_path_success[:, 1], mean_path_success[:, 2],
               color='#27ae60', linewidth=5, alpha=0.9, label='成功策略路径',
               linestyle='-', zorder=20)
        
        # 绘制影响范围（置信椭球）
        draw_confidence_ellipsoid(ax, mean_path_success, std_path_success, 
                                 color='#27ae60', alpha=0.15, stride=5)
        
        # 标记策略路径的起点和终点
        ax.scatter([mean_path_success[0, 0]], [mean_path_success[0, 1]], [mean_path_success[0, 2]],
                  c='darkgreen', s=400, marker='o', alpha=0.9, 
                  edgecolors='black', linewidths=3, zorder=25,
                  label='成功策略起点')
        
        ax.scatter([mean_path_success[-1, 0]], [mean_path_success[-1, 1]], [mean_path_success[-1, 2]],
                  c='#27ae60', s=500, marker='D', alpha=0.9, 
                  edgecolors='darkgreen', linewidths=3, zorder=25,
                  label='成功策略终点')
        
        # 绘制所有原始轨迹（半透明细线）
        for traj in success_trajectories[:]:  # 绘制所有成功轨迹
            ax.plot(traj[:, 0], traj[:, 1], traj[:, 2],
                   color='#27ae60', linewidth=0.8, alpha=0.15, zorder=5)
    
    # 4. 处理失败轨迹
    if len(failure_data) > 0:
        failure_trajectories = [d['positions'] for d in failure_data]
        
        # 归一化长度
        normalized_failure = normalize_trajectory_length(failure_trajectories, n_points=50)
        
        # 计算策略路径和标准差
        mean_path_failure, std_path_failure = compute_strategy_path(normalized_failure)
        
        # 绘制策略路径（粗虚线）
        ax.plot(mean_path_failure[:, 0], mean_path_failure[:, 1], mean_path_failure[:, 2],
               color='#e74c3c', linewidth=5, alpha=0.9, label='失败策略路径',
               linestyle='--', zorder=20)
        
        # 绘制影响范围
        draw_confidence_ellipsoid(ax, mean_path_failure, std_path_failure, 
                                 color='#e74c3c', alpha=0.15, stride=5)
        
        # 标记策略路径的起点和终点
        ax.scatter([mean_path_failure[0, 0]], [mean_path_failure[0, 1]], [mean_path_failure[0, 2]],
                  c='darkred', s=400, marker='o', alpha=0.9, 
                  edgecolors='black', linewidths=3, zorder=25,
                  label='失败策略起点')
        
        ax.scatter([mean_path_failure[-1, 0]], [mean_path_failure[-1, 1]], [mean_path_failure[-1, 2]],
                  c='#e74c3c', s=500, marker='s', alpha=0.9, 
                  edgecolors='darkred', linewidths=3, zorder=25,
                  label='失败策略终点')
        
        # 绘制所有原始轨迹（半透明细线）
        for traj in failure_trajectories[:]:  # 绘制所有失败轨迹
            ax.plot(traj[:, 0], traj[:, 1], traj[:, 2],
                   color='#e74c3c', linewidth=0.8, alpha=0.2, zorder=5)
    
    # 5. 绘制原点目标
    ax.scatter([0], [0], [0], c='gold', s=1000, marker='*', 
              edgecolors='orange', linewidths=6, zorder=100,
              label='目标：原点(0,0,0)')
    
    ax.text(0, 0, 0, '  ★ 目标\n  (0,0,0)', fontsize=14, fontweight='bold',
           color='darkred', ha='left', va='bottom', zorder=101)
    
    # 6. 设置坐标轴
    ax.set_xlabel('认知轴 (C)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_ylabel('情感轴 (A)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_zlabel('动机轴 (P)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    
    ax.set_title('统计策略路径可视化\n平均路径（粗线） + 影响范围（半透明椭球） + 原始轨迹（细线）', 
                fontsize=18, fontweight='bold', pad=25)
    
    # 7. 设置视角
    ax.view_init(elev=25, azim=225)
    max_range = 30
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()
    
    ax.grid(True, alpha=0.25, linestyle='--')
    
    # 8. 图例
    ax.legend(loc='upper left', fontsize=13, framealpha=0.95, edgecolor='black')
    
    # 9. 说明文字
    explanation = (
        '统计分析说明：\n'
        f'• 成功策略路径：{len(success_data)}条轨迹的平均路径\n'
        f'• 失败策略路径：{len(failure_data)}条轨迹的平均路径\n'
        '• 半透明椭球：1.5倍标准差（约90%置信区间）\n'
        '• 细线：原始轨迹数据\n'
        '• 粗线：统计平均的策略路径'
    )
    
    fig.text(0.02, 0.02, explanation, fontsize=11, 
            verticalalignment='bottom', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存统计策略路径图：{output_path}")
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_visualizations_statistical"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 生成统计策略路径可视化...")
    print("核心方法:")
    print("  1. 轨迹归一化（插值到相同长度）")
    print("  2. 计算平均路径（策略路径中心线）")
    print("  3. 计算标准差（影响范围）")
    print("  4. 用半透明椭球表示置信区间\n")
    
    # 加载数据
    all_data = load_full_trajectories(results_dir)
    print(f"✅ 已加载 {len(all_data)} 个案例\n")
    
    success_count = len([d for d in all_data if d['status'] == 'success'])
    failure_count = len(all_data) - success_count
    print(f"📊 成功: {success_count}, 失败: {failure_count}\n")
    
    # 生成统计策略图
    print("📊 生成统计策略路径图...\n")
    plot_statistical_strategy(all_data, output_dir / "statistical_strategy_paths.png")
    
    print(f"\n✅ 统计策略路径可视化已生成！")
    print(f"📁 保存位置: {output_dir}\n")
    print("图表说明:")
    print("  • 粗线 = 平均策略路径")
    print("  • 椭球 = 影响范围（90%置信区间）")
    print("  • 细线 = 原始轨迹")

if __name__ == "__main__":
    main()

