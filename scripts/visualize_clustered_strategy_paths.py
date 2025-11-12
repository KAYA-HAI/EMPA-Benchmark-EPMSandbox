#!/usr/bin/env python3
"""
分簇策略路径可视化 - 为每个策略簇分别计算平均路径

核心改进：
1. 先聚类识别不同策略类型
2. 对每个簇分别计算平均路径和标准差
3. 用不同颜色展示不同策略的典型路径和波动范围

理论意义：
- 不再假设单一平均路径
- 揭示多模态策略分布
- 保留策略多样性
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import interp1d, make_interp_spline
from sklearn.cluster import KMeans
from pathlib import Path

# 配置matplotlib为专业科研风格（手动实现seaborn-like样式）
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

def load_trajectories(results_dir):
    """加载所有轨迹"""
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
        
        # 提取轨迹
        if 'epj' in data and 'trajectory' in data['epj']:
            trajectory = data['epj']['trajectory']
            positions = np.array([point['P_t'] for point in trajectory])
            
            if len(positions) > 1:
                all_data.append({
                    'script_id': script_id,
                    'status': status,
                    'positions': positions,
                })
    
    return all_data

def normalize_trajectory(traj, n_points=100):
    """弧长归一化 + 线性插值"""
    if len(traj) < 2:
        return None
    
    try:
        # 计算累积弧长
        distances = np.sqrt(np.sum(np.diff(traj, axis=0)**2, axis=1))
        cum_distances = np.concatenate([[0], np.cumsum(distances)])
        
        if cum_distances[-1] < 1e-6:
            return None
        
        cum_distances = cum_distances / cum_distances[-1]  # 归一化到 [0, 1]
        
        # 线性插值
        new_params = np.linspace(0, 1, n_points)
        
        interp_x = interp1d(cum_distances, traj[:, 0], kind='linear')
        interp_y = interp1d(cum_distances, traj[:, 1], kind='linear')
        interp_z = interp1d(cum_distances, traj[:, 2], kind='linear')
        
        normalized = np.column_stack([
            interp_x(new_params),
            interp_y(new_params),
            interp_z(new_params)
        ])
        
        return normalized
    except:
        return None

def extract_trajectory_features(traj):
    """提取轨迹特征用于聚类"""
    # 起点和终点
    start = traj[0]
    end = traj[-1]
    
    # 总位移向量
    displacement = end - start
    displacement_norm = np.linalg.norm(displacement) + 1e-6
    displacement_dir = displacement / displacement_norm
    
    # 各轴变化
    delta_C = end[0] - start[0]
    delta_A = end[1] - start[1]
    delta_P = end[2] - start[2]
    
    # 路径总长度
    path_length = 0
    for i in range(1, len(traj)):
        path_length += np.linalg.norm(traj[i] - traj[i-1])
    
    # 直线度
    straightness = displacement_norm / (path_length + 1e-6)
    
    # 平均位置
    mean_pos = np.mean(traj, axis=0)
    
    # 组合特征
    features = np.concatenate([
        displacement_dir,    # 3维：总体方向
        [delta_C, delta_A, delta_P],  # 3维：各轴变化
        [straightness],      # 1维：直线度
        mean_pos             # 3维：平均位置
    ])
    
    if np.any(np.isnan(features)) or np.any(np.isinf(features)):
        return np.zeros_like(features)
    
    return features

def cluster_and_compute_paths(trajectories, n_clusters=3):
    """
    聚类并为每个簇计算平均路径
    
    返回：
        clusters: 每个簇的信息 [{'label': 0, 'trajectories': [...], 'mean_path': ..., 'std_path': ...}]
    """
    # 1. 归一化所有轨迹
    normalized_trajs = []
    valid_indices = []
    
    for i, traj_data in enumerate(trajectories):
        norm_traj = normalize_trajectory(traj_data['positions'])
        if norm_traj is not None:
            normalized_trajs.append(norm_traj)
            valid_indices.append(i)
    
    normalized_trajs = np.array(normalized_trajs)
    
    if len(normalized_trajs) < n_clusters:
        print(f"⚠️  轨迹数({len(normalized_trajs)})少于簇数({n_clusters})")
        return []
    
    # 2. 提取特征并聚类
    features = []
    for traj in normalized_trajs:
        feat = extract_trajectory_features(traj)
        features.append(feat)
    
    features = np.array(features)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    labels = kmeans.fit_predict(features)
    
    # 3. 为每个簇计算统计量
    clusters = []
    for cluster_id in range(n_clusters):
        mask = labels == cluster_id
        cluster_trajs = normalized_trajs[mask]
        
        if len(cluster_trajs) == 0:
            continue
        
        # 计算平均路径和标准差
        mean_path = np.mean(cluster_trajs, axis=0)
        std_path = np.std(cluster_trajs, axis=0)
        
        # 获取原始轨迹数据
        cluster_original = [trajectories[valid_indices[i]] for i in range(len(valid_indices)) if mask[i]]
        
        clusters.append({
            'label': cluster_id,
            'count': len(cluster_trajs),
            'trajectories': cluster_original,
            'normalized_trajectories': cluster_trajs,
            'mean_path': mean_path,
            'std_path': std_path
        })
    
    return clusters

def smooth_path_bspline(path, smoothing_factor=3):
    """
    使用B-spline对路径进行平滑处理
    
    参数:
        path: Nx3 数组，原始路径点
        smoothing_factor: 平滑因子，越大越平滑
    
    返回:
        平滑后的路径
    """
    if len(path) < 4:  # B-spline需要至少4个点
        return path
    
    # 创建参数t
    t = np.linspace(0, 1, len(path))
    
    # 为每个维度创建B-spline插值
    try:
        # 使用三次B-spline
        k = min(3, len(path) - 1)  # spline阶数
        
        # 生成更密集的采样点
        t_smooth = np.linspace(0, 1, len(path) * smoothing_factor)
        
        # 对每个维度进行B-spline插值
        spline_x = make_interp_spline(t, path[:, 0], k=k)
        spline_y = make_interp_spline(t, path[:, 1], k=k)
        spline_z = make_interp_spline(t, path[:, 2], k=k)
        
        # 生成平滑路径
        smooth_path = np.column_stack([
            spline_x(t_smooth),
            spline_y(t_smooth),
            spline_z(t_smooth)
        ])
        
        return smooth_path
    except:
        # 如果平滑失败，返回原始路径
        return path

def draw_confidence_ellipsoids(ax, path, std, color, alpha=0.05, stride=12):
    """
    绘制置信椭球（适中透明度，不遮挡路径）
    
    椭圆含义：
    - 中心 = 平均路径上的点
    - 大小 = 1.5倍标准差（该簇内轨迹在此位置的波动范围）
    - 作用 = 显示该策略的"影响范围"或"置信区域"
    """
    for i in range(0, len(path), stride):
        center = path[i]
        radii = std[i] * 1.5  # 1.5倍标准差
        
        # 生成椭球表面点（增加采样密度以获得更光滑的表面）
        u = np.linspace(0, 2 * np.pi, 20)  # 增加到20个点（水平方向）
        v = np.linspace(0, np.pi, 12)      # 增加到12个点（垂直方向）
        
        x = center[0] + radii[0] * np.outer(np.cos(u), np.sin(v))
        y = center[1] + radii[1] * np.outer(np.sin(u), np.sin(v))
        z = center[2] + radii[2] * np.outer(np.ones(np.size(u)), np.cos(v))
        
        # zorder=1 确保椭球在最底层
        ax.plot_surface(x, y, z, color=color, alpha=alpha, shade=True, 
                       edgecolor='none', zorder=1, antialiased=True)

def plot_clustered_strategy_paths(clusters, output_path):
    """绘制分簇策略路径（专业科研级可视化）"""
    # 创建图形
    fig = plt.figure(figsize=(20, 14), facecolor='white')
    ax = fig.add_subplot(111, projection='3d', facecolor='white')
    
    # 使用专业配色方案（参考matplotlib默认深色调）
    cluster_colors = [
        '#d62728',  # 深红色
        '#1f77b4',  # 深蓝色  
        '#2ca02c',  # 深绿色
    ]
    cluster_names = ['策略A', '策略B', '策略C']
    
    # 计算总案例数和每个簇的占比，用于动态调整线宽
    total_count = sum(cluster['count'] for cluster in clusters)
    
    # 绘制每个簇
    for i, cluster in enumerate(clusters):
        color = cluster_colors[i]
        name = cluster_names[i]
        mean_path = cluster['mean_path']
        std_path = cluster['std_path']
        count = cluster['count']
        
        # 统计簇内成功/失败数量
        n_success = sum(1 for t in cluster['trajectories'] if t['status'] == 'success')
        n_failure = count - n_success
        
        # 1. 绘制置信椭球（影响范围）- 先画，在最底层
        draw_confidence_ellipsoids(ax, mean_path, std_path, color)
        
        # 2. 绘制簇内原始轨迹（细线，半透明）
        for traj_data in cluster['trajectories']:
            traj = traj_data['positions']
            # 根据成功/失败使用不同的线型
            linestyle = '-' if traj_data['status'] == 'success' else '--'
            ax.plot(traj[:, 0], traj[:, 1], traj[:, 2],
                   color=color, linewidth=1.2, alpha=0.25, linestyle=linestyle, zorder=10)
        
        # 3. 绘制平均路径（粗线，线宽与案例占比成正比）- 使用B-spline平滑
        # 计算该簇的占比，映射到线宽范围 [4, 14]
        proportion = count / total_count
        linewidth = 4 + proportion * 10  # 线宽范围：4到14
        
        # 对平均路径进行B-spline平滑处理，使线条更流畅
        smooth_mean_path = smooth_path_bspline(mean_path, smoothing_factor=2)
        
        ax.plot(smooth_mean_path[:, 0], smooth_mean_path[:, 1], smooth_mean_path[:, 2],
               color=color, linewidth=linewidth, alpha=0.92, zorder=20,
               label=f'{name}: N={count} ({proportion*100:.1f}%) (✓{n_success} ✗{n_failure})',
               solid_capstyle='round', solid_joinstyle='round')
        
        # 4. 标记起点和终点（大小也与案例占比成正比）
        marker_size_start = 200 + proportion * 400  # 起点标记大小：200到600
        marker_size_end = 250 + proportion * 450    # 终点标记大小：250到700
        
        ax.scatter([mean_path[0, 0]], [mean_path[0, 1]], [mean_path[0, 2]],
                  c=color, s=marker_size_start, marker='o', alpha=0.9, zorder=25, 
                  edgecolors='white', linewidths=2.5)
        
        ax.scatter([mean_path[-1, 0]], [mean_path[-1, 1]], [mean_path[-1, 2]],
                  c=color, s=marker_size_end, marker='D', alpha=0.9, zorder=25,
                  edgecolors='white', linewidths=2.5)
    
    # 绘制原点（目标点）
    ax.scatter([0], [0], [0], c='#FFD700', s=1000, marker='*', 
              edgecolors='#FF8C00', linewidths=5, zorder=100,
              label='Target: (0,0,0)')
    
    ax.text(0, 0, 0, '  ★ 目标\n  (0,0,0)', fontsize=14, fontweight='bold',
           color='#8B0000', ha='left', va='bottom', zorder=101)
    
    # 坐标轴参考线（seaborn风格，更细腻）
    axis_limit = 35
    ax.plot([0, axis_limit], [0, 0], [0, 0], color='#d62728', linewidth=2.0, alpha=0.35)
    ax.plot([0, 0], [0, axis_limit], [0, 0], color='#2ca02c', linewidth=2.0, alpha=0.35)
    ax.plot([0, 0], [0, 0], [0, axis_limit], color='#1f77b4', linewidth=2.0, alpha=0.35)
    ax.plot([-axis_limit, 0], [0, 0], [0, 0], color='#d62728', linewidth=1.5, alpha=0.25, linestyle='--')
    ax.plot([0, 0], [-axis_limit, 0], [0, 0], color='#2ca02c', linewidth=1.5, alpha=0.25, linestyle='--')
    ax.plot([0, 0], [0, 0], [-axis_limit, 0], color='#1f77b4', linewidth=1.5, alpha=0.25, linestyle='--')
    
    # 设置坐标轴标签（seaborn风格字体）
    ax.set_xlabel('认知轴 Cognitive (C)\n← 赤字 Deficit | 充足 Sufficient →', 
                  fontsize=12, fontweight='normal', labelpad=18, color='#555555')
    ax.set_ylabel('情感轴 Affective (A)\n← 赤字 Deficit | 充足 Sufficient →', 
                  fontsize=12, fontweight='normal', labelpad=18, color='#555555')
    ax.set_zlabel('动机轴 Proactive (P)\n← 赤字 Deficit | 充足 Sufficient →', 
                  fontsize=12, fontweight='normal', labelpad=28, color='#555555')
    
    # 设置刻度标签（seaborn风格）
    ax.tick_params(axis='x', labelsize=9, pad=6, colors='#555555')
    ax.tick_params(axis='y', labelsize=9, pad=6, colors='#555555')
    ax.tick_params(axis='z', labelsize=9, pad=6, colors='#555555')
    
    # 标题（seaborn风格）
    ax.set_title('共情修复策略分簇可视化\nClustered Empathy Repair Strategy Paths', 
                fontsize=16, fontweight='600', pad=28, color='#333333')
    
    # 视角和范围
    ax.view_init(elev=25, azim=225)
    ax.set_xlim([-axis_limit, axis_limit])
    ax.set_ylim([-axis_limit, axis_limit])
    ax.set_zlim([-axis_limit, axis_limit])
    
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()
    
    # 网格和背景（seaborn风格，更干净）
    ax.grid(True, alpha=0.15, linestyle='-', linewidth=0.6, color='#e0e0e0')
    
    # 设置背景面板（更轻、更统一的灰色）
    ax.xaxis.pane.fill = True
    ax.yaxis.pane.fill = True
    ax.zaxis.pane.fill = True
    ax.xaxis.pane.set_facecolor('#fafafa')
    ax.yaxis.pane.set_facecolor('#fafafa')
    ax.zaxis.pane.set_facecolor('#fafafa')
    ax.xaxis.pane.set_alpha(0.8)
    ax.yaxis.pane.set_alpha(0.8)
    ax.zaxis.pane.set_alpha(0.8)
    
    # 设置坐标轴线条颜色（seaborn风格）
    ax.xaxis.line.set_color('#cccccc')
    ax.yaxis.line.set_color('#cccccc')
    ax.zaxis.line.set_color('#cccccc')
    
    # 图例（seaborn风格）
    legend = ax.legend(loc='upper left', fontsize=10, framealpha=0.9, 
                      edgecolor='#cccccc', fancybox=False, shadow=False,
                      frameon=True, facecolor='white', borderpad=1.0,
                      labelspacing=0.6, handlelength=2.0)
    
    # 说明
    total_trajs = sum(c['count'] for c in clusters)
    total_success = sum(sum(1 for t in c['trajectories'] if t['status'] == 'success') for c in clusters)
    total_failure = total_trajs - total_success
    
    # 中文说明（放在图内右上角，seaborn风格）
    info_text = (
        f'样本数据\n'
        f'  总样本数: N = {total_trajs}\n'
        f'  成功案例: {total_success} 例\n'
        f'  失败案例: {total_failure} 例\n'
        f'\n'
        f'分析方法\n'
        f'  聚类算法: K-Means (K={len(clusters)})\n'
        f'  归一化: 弧长参数化 (n=100)\n'
        f'  路径平滑: B-spline插值\n'
        f'  置信区间: 1.5σ 椭球体\n'
        f'\n'
        f'可视化要素\n'
        f'  粗线: 平均路径（线宽∝占比）\n'
        f'  椭球: 1.5σ 置信区间\n'
        f'  细线: 原始轨迹\n'
        f'  金星: 目标原点 (0,0,0)'
    )
    
    # 图内右上角：统一说明框（seaborn简约风格）
    fig.text(0.94, 0.96, info_text, fontsize=9, 
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round,pad=0.8', facecolor='white', 
                     edgecolor='#cccccc', alpha=0.95, linewidth=1.2),
            transform=fig.transFigure, color='#555555', linespacing=1.5)
    
    # 使用subplots_adjust精确控制布局
    # 减小左右边距，让3D图占据更多画布空间，同时保持居中
    plt.subplots_adjust(left=0.10, right=0.90, top=0.94, bottom=0.08)
    # 移除bbox_inches='tight'以确保subplots_adjust生效
    plt.savefig(output_path, dpi=300)
    print(f"✅ 已保存分簇策略路径图：{output_path}")
    plt.close()

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_clustered_strategy_paths"
    output_dir.mkdir(exist_ok=True)
    
    print("🚀 生成分簇策略路径可视化...")
    print("\n核心改进：")
    print("  • 对所有案例（成功+失败）一起聚类")
    print("  • 识别不同的共情策略模式")
    print("  • 揭示成功vs失败的路径差异\n")
    
    # 加载数据
    all_data = load_trajectories(results_dir)
    success_data = [d for d in all_data if d['status'] == 'success']
    failure_data = [d for d in all_data if d['status'] != 'success']
    
    print(f"✅ 已加载 {len(all_data)} 个案例")
    print(f"   成功: {len(success_data)}")
    print(f"   失败: {len(failure_data)}\n")
    
    if len(all_data) < 3:
        print("❌ 案例太少，无法聚类")
        return
    
    # 对所有案例聚类（不区分成功失败）
    print("📊 执行聚类分析（包含所有案例）...\n")
    clusters = cluster_and_compute_paths(all_data, n_clusters=3)
    
    if not clusters:
        print("❌ 聚类失败")
        return
    
    # 打印聚类结果
    print("📊 聚类结果：")
    for i, cluster in enumerate(clusters):
        n_success = sum(1 for t in cluster['trajectories'] if t['status'] == 'success')
        n_failure = cluster['count'] - n_success
        print(f"  策略{chr(65+i)}: {cluster['count']}条 (✓{n_success} ✗{n_failure}) - {cluster['count']/len(all_data)*100:.1f}%")
    print()
    
    # 绘图
    print("🎨 绘制分簇策略路径...\n")
    plot_clustered_strategy_paths(clusters, output_dir / "clustered_strategy_paths.png")
    
    print(f"\n✅ 完成！")
    print(f"📁 保存位置: {output_dir}\n")
    print("🔬 核心发现：")
    print("  • 对所有案例（成功+失败）聚类")
    print("  • 识别不同的共情策略模式")
    print("  • 可以看到哪些簇主要是成功，哪些主要是失败")
    print("  • 椭球显示该策略的波动范围")
    print("  • 实线=成功轨迹，虚线=失败轨迹")

if __name__ == "__main__":
    main()

