#!/usr/bin/env python3
"""
简单直接的聚类轨迹可视化

核心思想：
1. 直接使用trajectory里已有的P_t坐标（按轮数）
2. 用turn作为对齐依据（而非复杂的弧长或EPM进度）
3. 基于轨迹的简单统计特征进行聚类
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.cluster import KMeans
from pathlib import Path
from scipy.interpolate import interp1d

# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti', 'PingFang SC']
matplotlib.rcParams['axes.unicode_minus'] = False

def load_trajectories_simple(results_dir):
    """直接加载每个script的轨迹数据（按turn）"""
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
        
        # 提取轨迹（直接用trajectory里的P_t）
        if 'epj' in data and 'trajectory' in data['epj']:
            trajectory = data['epj']['trajectory']
            
            # 提取每个turn的P_t
            positions = []
            for point in trajectory:
                positions.append(point['P_t'])
            
            if len(positions) > 1:
                all_data.append({
                    'script_id': script_id,
                    'total_turns': total_turns,
                    'status': status,
                    'positions': np.array(positions),
                })
    
    return all_data

def normalize_trajectory_by_turn(trajectories, max_turns=50):
    """
    按turn归一化轨迹长度（线性插值到统一长度）
    这是最简单直接的对齐方法
    """
    normalized = []
    
    for traj in trajectories:
        n = len(traj)
        if n < 2:
            continue
        
        # 原始turn序列：0, 1, 2, ..., n-1
        old_turns = np.arange(n)
        
        # 插值到统一长度
        new_turns = np.linspace(0, n-1, max_turns)
        
        try:
            interp_C = interp1d(old_turns, traj[:, 0], kind='linear')
            interp_A = interp1d(old_turns, traj[:, 1], kind='linear')
            interp_P = interp1d(old_turns, traj[:, 2], kind='linear')
            
            new_traj = np.column_stack([
                interp_C(new_turns),
                interp_A(new_turns),
                interp_P(new_turns)
            ])
            
            normalized.append(new_traj)
        except:
            continue
    
    return np.array(normalized)

def compute_simple_features(traj):
    """
    提取简单的轨迹特征用于聚类
    """
    # 起点和终点
    start = traj[0]
    end = traj[-1]
    
    # 总位移向量
    displacement = end - start
    displacement_norm = np.linalg.norm(displacement) + 1e-6
    displacement_dir = displacement / displacement_norm
    
    # 各轴的净变化
    delta_C = end[0] - start[0]
    delta_A = end[1] - start[1]
    delta_P = end[2] - start[2]
    
    # 路径总长度（累积距离）
    path_length = 0
    for i in range(1, len(traj)):
        path_length += np.linalg.norm(traj[i] - traj[i-1])
    
    # 直线度：位移/路径长度（越接近1越直）
    straightness = displacement_norm / (path_length + 1e-6)
    
    # 平均位置（轨迹中心）
    mean_pos = np.mean(traj, axis=0)
    
    # 组合特征
    features = np.concatenate([
        displacement_dir,    # 3维：总体方向
        [delta_C, delta_A, delta_P],  # 3维：各轴变化
        [straightness],      # 1维：路径直线度
        mean_pos             # 3维：平均位置
    ])
    
    # 检查NaN
    if np.any(np.isnan(features)) or np.any(np.isinf(features)):
        return np.zeros_like(features)
    
    return features

def cluster_trajectories_simple(normalized_trajs, n_clusters=3):
    """简单聚类"""
    features = []
    for traj in normalized_trajs:
        feat = compute_simple_features(traj)
        features.append(feat)
    
    features = np.array(features)
    
    # K-means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    labels = kmeans.fit_predict(features)
    
    # 计算每个簇的平均轨迹
    cluster_centers = []
    for i in range(n_clusters):
        cluster_trajs = normalized_trajs[labels == i]
        if len(cluster_trajs) > 0:
            center_traj = np.mean(cluster_trajs, axis=0)
            cluster_centers.append(center_traj)
        else:
            cluster_centers.append(None)
    
    return labels, cluster_centers

def draw_coordinate_planes(ax, size=30, alpha=0.1):
    """绘制坐标平面"""
    grid_size = 2
    
    xx, yy = np.meshgrid(np.linspace(-size, size, grid_size), 
                         np.linspace(-size, size, grid_size))
    zz = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=alpha, color='lightblue', 
                   edgecolor='blue', linewidth=0.5, shade=False)
    
    xx, zz = np.meshgrid(np.linspace(-size, size, grid_size), 
                         np.linspace(-size, size, grid_size))
    yy = np.zeros_like(xx)
    ax.plot_surface(xx, yy, zz, alpha=alpha, color='lightgreen', 
                   edgecolor='green', linewidth=0.5, shade=False)
    
    yy, zz = np.meshgrid(np.linspace(-size, size, grid_size), 
                         np.linspace(-size, size, grid_size))
    xx = np.zeros_like(yy)
    ax.plot_surface(xx, yy, zz, alpha=alpha, color='lightyellow', 
                   edgecolor='orange', linewidth=0.5, shade=False)

def plot_clustered_simple(all_data, output_path):
    """绘制简单聚类图"""
    fig = plt.figure(figsize=(24, 18))
    ax = fig.add_subplot(111, projection='3d')
    
    # 只处理成功案例
    success_data = [d for d in all_data if d['status'] == 'success']
    success_trajectories = [d['positions'] for d in success_data]
    
    if len(success_trajectories) < 3:
        print("⚠️  成功案例太少，无法聚类")
        return
    
    # 归一化（按turn插值）
    normalized_trajs = normalize_trajectory_by_turn(success_trajectories, max_turns=50)
    
    # 聚类
    n_clusters = 3
    labels, cluster_centers = cluster_trajectories_simple(normalized_trajs, n_clusters=n_clusters)
    
    # 定义簇的颜色和名称
    cluster_colors = ['#e74c3c', '#3498db', '#2ecc71']  # 红、蓝、绿
    cluster_names = ['策略A', '策略B', '策略C']
    cluster_markers = ['o', 's', '^']
    
    # 统计每个簇的数量
    cluster_counts = [np.sum(labels == i) for i in range(n_clusters)]
    
    # 1. 绘制坐标平面
    draw_coordinate_planes(ax, size=30, alpha=0.1)
    
    # 2. 绘制坐标轴
    axis_limit = 30
    ax.plot([0, axis_limit], [0, 0], [0, 0], 'r-', linewidth=2.5, alpha=0.3)
    ax.plot([0, 0], [0, axis_limit], [0, 0], 'g-', linewidth=2.5, alpha=0.3)
    ax.plot([0, 0], [0, 0], [0, axis_limit], 'b-', linewidth=2.5, alpha=0.3)
    ax.plot([-axis_limit, 0], [0, 0], [0, 0], 'r--', linewidth=2, alpha=0.3)
    ax.plot([0, 0], [-axis_limit, 0], [0, 0], 'g--', linewidth=2, alpha=0.3)
    ax.plot([0, 0], [0, 0], [-axis_limit, 0], 'b--', linewidth=2, alpha=0.3)
    
    # 3. 绘制每个簇的轨迹
    for cluster_id in range(n_clusters):
        cluster_mask = labels == cluster_id
        cluster_trajs = [success_trajectories[i] for i, mask in enumerate(cluster_mask) if mask]
        
        color = cluster_colors[cluster_id]
        name = cluster_names[cluster_id]
        count = cluster_counts[cluster_id]
        
        # 绘制簇内所有原始轨迹（细线）
        for traj in cluster_trajs:
            ax.plot(traj[:, 0], traj[:, 1], traj[:, 2],
                   color=color, linewidth=1.5, alpha=0.3, zorder=5)
        
        # 绘制簇中心路径（粗线）
        if cluster_centers[cluster_id] is not None:
            center = cluster_centers[cluster_id]
            ax.plot(center[:, 0], center[:, 1], center[:, 2],
                   color=color, linewidth=7, alpha=0.95, zorder=20,
                   label=f'{name} ({count}条)')
            
            # 标记簇中心的起点和终点
            ax.scatter([center[0, 0]], [center[0, 1]], [center[0, 2]],
                      c=color, s=400, marker=cluster_markers[cluster_id], 
                      alpha=0.9, edgecolors='black', linewidths=3, zorder=25)
            
            ax.scatter([center[-1, 0]], [center[-1, 1]], [center[-1, 2]],
                      c=color, s=500, marker=cluster_markers[cluster_id], 
                      alpha=0.95, edgecolors='black', linewidths=4, zorder=25)
    
    # 4. 绘制原点
    ax.scatter([0], [0], [0], c='gold', s=1200, marker='*', 
              edgecolors='orange', linewidths=6, zorder=100,
              label='目标：原点(0,0,0)')
    
    ax.text(0, 0, 0, '  ★ 目标\n  (0,0,0)', fontsize=16, fontweight='bold',
           color='darkred', ha='left', va='bottom', zorder=101)
    
    # 5. 设置坐标轴
    ax.set_xlabel('认知轴 (C)\n← 赤字 | 充足 →', fontsize=15, fontweight='bold')
    ax.set_ylabel('情感轴 (A)\n← 赤字 | 充足 →', fontsize=15, fontweight='bold')
    ax.set_zlabel('动机轴 (P)\n← 赤字 | 充足 →', fontsize=15, fontweight='bold')
    
    ax.set_title('轨迹聚类分析 (按轮数对齐)\n' + 
                '基于trajectory中的P_t坐标', 
                fontsize=20, fontweight='bold', pad=30)
    
    # 6. 设置视角
    ax.view_init(elev=25, azim=225)
    max_range = 30
    ax.set_xlim([-max_range, max_range])
    ax.set_ylim([-max_range, max_range])
    ax.set_zlim([-max_range, max_range])
    
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()
    
    ax.grid(True, alpha=0.25, linestyle='--')
    
    # 7. 图例
    ax.legend(loc='upper left', fontsize=14, framealpha=0.95, edgecolor='black')
    
    # 8. 说明文字
    explanation = (
        '聚类策略分析：\n'
        f'• 总成功案例：{len(success_data)}条\n'
        f'• 识别策略类型：{n_clusters}种\n'
        '• 对齐方法：按turn线性插值\n'
        '• 聚类特征：方向+各轴变化+直线度\n'
        '• 粗线：各策略的平均路径\n'
        '• 细线：策略簇内的原始轨迹'
    )
    
    fig.text(0.02, 0.02, explanation, fontsize=12, 
            verticalalignment='bottom', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存简化聚类图：{output_path}")
    
    # 打印聚类分析结果
    print(f"\n📊 聚类分析结果：")
    for i in range(n_clusters):
        print(f"  {cluster_names[i]}: {cluster_counts[i]}条 ({cluster_counts[i]/len(success_data)*100:.1f}%)")
    
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_visualizations_simple_clustered"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 生成简化聚类轨迹可视化...")
    print("  • 直接使用trajectory里的P_t坐标")
    print("  • 按turn对齐（最简单直接的方法）\n")
    
    # 加载数据
    all_data = load_trajectories_simple(results_dir)
    print(f"✅ 已加载 {len(all_data)} 个案例\n")
    
    success_count = len([d for d in all_data if d['status'] == 'success'])
    failure_count = len(all_data) - success_count
    print(f"📊 成功: {success_count}, 失败: {failure_count}\n")
    
    # 生成聚类图
    print("📊 执行轨迹聚类与可视化...\n")
    plot_clustered_simple(all_data, output_dir / "simple_clustered_paths.png")
    
    print(f"\n✅ 简化聚类可视化已生成！")
    print(f"📁 保存位置: {output_dir}")

if __name__ == "__main__":
    main()


