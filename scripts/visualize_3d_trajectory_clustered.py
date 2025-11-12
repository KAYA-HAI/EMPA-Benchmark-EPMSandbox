#!/usr/bin/env python3
"""
聚类流场拟合可视化 (Clustered Flow Field Fitting)

核心思想：
1. 不求平均路径，而是识别策略簇群
2. 揭示多模态策略分布（认知导向、情感导向、动机导向）
3. 构建能量流场而非单一中心线

理论基础：
- 共情不是路径的平均，而是路径族的结构
- 应捕捉能量流的统计场，而非压扁为单一均值
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import interp1d
from scipy.spatial.distance import euclidean
from sklearn.cluster import KMeans
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

def normalize_by_epm_progress(trajectories, n_points=50):
    """
    基于EPM进度的归一化（距离原点）
    
    这是心理意义上的对齐：相同"共情赤字消除进度"的点应该对应
    """
    normalized = []
    
    for traj in trajectories:
        # 计算每个点到原点的距离（EPM物理意义）
        distances = np.linalg.norm(traj, axis=1)
        
        # 归一化进度：1.0 (起点，最大赤字) → 0.0 (终点，接近原点)
        initial_dist = distances[0]
        final_dist = distances[-1]
        
        # 处理非单调情况（确保单调递减）
        distances_monotonic = np.minimum.accumulate(distances)
        
        # 计算进度：0.0 (起点) → 1.0 (终点)
        total_progress = (initial_dist - final_dist)
        if total_progress < 1e-6:  # 几乎没有进展
            continue
            
        progress = (initial_dist - distances_monotonic) / total_progress
        progress = np.clip(progress, 0, 1)
        
        # 插值到统一进度网格
        progress_grid = np.linspace(0, 1, n_points)
        
        try:
            interp_C = interp1d(progress, traj[:, 0], kind='linear', 
                               bounds_error=False, fill_value='extrapolate')
            interp_A = interp1d(progress, traj[:, 1], kind='linear',
                               bounds_error=False, fill_value='extrapolate')
            interp_P = interp1d(progress, traj[:, 2], kind='linear',
                               bounds_error=False, fill_value='extrapolate')
            
            new_traj = np.column_stack([
                interp_C(progress_grid),
                interp_A(progress_grid),
                interp_P(progress_grid)
            ])
            
            normalized.append(new_traj)
        except:
            continue
    
    return np.array(normalized)

def compute_trajectory_features(traj):
    """
    提取轨迹特征用于聚类
    
    特征维度：
    1. 初始方向（前10%的主方向）
    2. 中段方向（中间段的主方向）
    3. 最终方向（后10%的主方向）
    4. C/A/P各轴的变化量
    5. 路径曲率（弯曲程度）
    """
    n = len(traj)
    
    # 1. 初始方向（前10%）
    initial_vec = traj[min(int(n*0.1), n-1)] - traj[0]
    initial_norm = np.linalg.norm(initial_vec)
    if initial_norm < 1e-6:
        initial_dir = np.zeros(3)
    else:
        initial_dir = initial_vec / initial_norm
    
    # 2. 中段方向
    mid_start = int(n*0.4)
    mid_end = min(int(n*0.6), n-1)
    mid_vec = traj[mid_end] - traj[mid_start]
    mid_norm = np.linalg.norm(mid_vec)
    if mid_norm < 1e-6:
        mid_dir = np.zeros(3)
    else:
        mid_dir = mid_vec / mid_norm
    
    # 3. 最终方向
    final_start = int(n*0.9)
    final_vec = traj[-1] - traj[final_start]
    final_norm = np.linalg.norm(final_vec)
    if final_norm < 1e-6:
        final_dir = np.zeros(3)
    else:
        final_dir = final_vec / final_norm
    
    # 4. 各轴变化量
    delta_C = traj[-1, 0] - traj[0, 0]
    delta_A = traj[-1, 1] - traj[0, 1]
    delta_P = traj[-1, 2] - traj[0, 2]
    
    # 5. 路径曲率（总弯曲度）
    curvature = 0
    valid_angles = 0
    for i in range(1, n-1):
        v1 = traj[i] - traj[i-1]
        v2 = traj[i+1] - traj[i]
        v1_norm = np.linalg.norm(v1)
        v2_norm = np.linalg.norm(v2)
        
        if v1_norm > 1e-6 and v2_norm > 1e-6:
            cos_angle = np.dot(v1, v2) / (v1_norm * v2_norm)
            cos_angle = np.clip(cos_angle, -1, 1)
            curvature += np.arccos(cos_angle)
            valid_angles += 1
    
    # 归一化曲率
    if valid_angles > 0:
        curvature = curvature / valid_angles
    
    # 组合特征向量
    features = np.concatenate([
        initial_dir,     # 3维
        mid_dir,         # 3维
        final_dir,       # 3维
        [delta_C, delta_A, delta_P],  # 3维
        [curvature]      # 1维
    ])
    
    # 检查NaN
    if np.any(np.isnan(features)) or np.any(np.isinf(features)):
        # 返回零向量作为fallback
        return np.zeros_like(features)
    
    return features

def cluster_trajectories(normalized_trajs, n_clusters=3):
    """
    对轨迹进行聚类
    
    返回：聚类标签和每个簇的中心轨迹
    """
    # 提取特征
    features = []
    for traj in normalized_trajs:
        feat = compute_trajectory_features(traj)
        features.append(feat)
    
    features = np.array(features)
    
    # K-means聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    labels = kmeans.fit_predict(features)
    
    # 计算每个簇的中心轨迹（簇内平均）
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

def plot_clustered_strategies(all_data, output_path):
    """
    绘制聚类后的策略分布图
    """
    fig = plt.figure(figsize=(24, 18))
    ax = fig.add_subplot(111, projection='3d')
    
    # 只处理成功案例
    success_data = [d for d in all_data if d['status'] == 'success']
    success_trajectories = [d['positions'] for d in success_data]
    
    # 归一化（基于EPM进度）
    normalized_trajs = normalize_by_epm_progress(success_trajectories, n_points=50)
    
    if len(normalized_trajs) < 3:
        print("⚠️  成功案例太少，无法聚类")
        return
    
    # 聚类
    n_clusters = 3
    labels, cluster_centers = cluster_trajectories(normalized_trajs, n_clusters=n_clusters)
    
    # 定义簇的颜色和名称
    cluster_colors = ['#e74c3c', '#3498db', '#2ecc71']  # 红、蓝、绿
    cluster_names = ['策略A：认知优先', '策略B：情感优先', '策略C：平衡型']
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
                   color=color, linewidth=1.2, alpha=0.25, zorder=5)
        
        # 绘制簇中心路径（粗线）
        if cluster_centers[cluster_id] is not None:
            center = cluster_centers[cluster_id]
            ax.plot(center[:, 0], center[:, 1], center[:, 2],
                   color=color, linewidth=6, alpha=0.95, zorder=20,
                   label=f'{name} ({count}条)')
            
            # 标记簇中心的起点和终点
            ax.scatter([center[0, 0]], [center[0, 1]], [center[0, 2]],
                      c=color, s=300, marker=cluster_markers[cluster_id], 
                      alpha=0.9, edgecolors='black', linewidths=2.5, zorder=25)
            
            ax.scatter([center[-1, 0]], [center[-1, 1]], [center[-1, 2]],
                      c=color, s=400, marker=cluster_markers[cluster_id], 
                      alpha=0.95, edgecolors='black', linewidths=3, zorder=25)
    
    # 4. 绘制原点
    ax.scatter([0], [0], [0], c='gold', s=1000, marker='*', 
              edgecolors='orange', linewidths=6, zorder=100,
              label='目标：原点(0,0,0)')
    
    ax.text(0, 0, 0, '  ★ 目标\n  (0,0,0)', fontsize=14, fontweight='bold',
           color='darkred', ha='left', va='bottom', zorder=101)
    
    # 5. 设置坐标轴
    ax.set_xlabel('认知轴 (C)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_ylabel('情感轴 (A)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    ax.set_zlabel('动机轴 (P)\n← 赤字 | 充足 →', fontsize=14, fontweight='bold')
    
    ax.set_title('聚类策略分布可视化 (Clustered Flow Field)\n' + 
                '基于EPM进度归一化 + 轨迹特征聚类', 
                fontsize=18, fontweight='bold', pad=25)
    
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
    ax.legend(loc='upper left', fontsize=13, framealpha=0.95, edgecolor='black')
    
    # 8. 说明文字
    explanation = (
        '聚类策略分析：\n'
        f'• 总成功案例：{len(success_data)}条\n'
        f'• 识别策略类型：{n_clusters}种\n'
        '• 归一化方法：EPM进度（距离原点）\n'
        '• 聚类特征：初始/中段/最终方向 + 各轴变化 + 曲率\n'
        '• 粗线：各策略的中心路径\n'
        '• 细线：策略簇内的原始轨迹'
    )
    
    fig.text(0.02, 0.02, explanation, fontsize=11, 
            verticalalignment='bottom', family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ 已保存聚类策略图：{output_path}")
    
    # 打印聚类分析结果
    print(f"\n📊 聚类分析结果：")
    for i in range(n_clusters):
        print(f"  {cluster_names[i]}: {cluster_counts[i]}条 ({cluster_counts[i]/len(success_data)*100:.1f}%)")
    
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_visualizations_clustered"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 生成聚类流场拟合可视化 (Clustered Flow Field Fitting)...")
    print("\n理论基础:")
    print("  • 共情过程不是路径的平均，而是路径族的结构")
    print("  • 识别多模态策略分布（认知导向、情感导向、平衡型）")
    print("  • 基于EPM进度归一化（心理意义上的对齐）\n")
    
    # 加载数据
    all_data = load_full_trajectories(results_dir)
    print(f"✅ 已加载 {len(all_data)} 个案例\n")
    
    success_count = len([d for d in all_data if d['status'] == 'success'])
    failure_count = len(all_data) - success_count
    print(f"📊 成功: {success_count}, 失败: {failure_count}\n")
    
    # 生成聚类策略图
    print("📊 执行轨迹聚类与可视化...\n")
    plot_clustered_strategies(all_data, output_dir / "clustered_strategy_paths.png")
    
    print(f"\n✅ 聚类流场可视化已生成！")
    print(f"📁 保存位置: {output_dir}\n")
    print("关键洞察:")
    print("  • 是否存在多种成功策略？")
    print("  • 不同策略在空间中的分布如何？")
    print("  • 策略簇间的差异体现在哪些维度？")

if __name__ == "__main__":
    main()

