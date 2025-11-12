#!/usr/bin/env python3
"""
Plotly交互式3D轨迹可视化 - 时间动画版本
真正的3D渲染 + 完全交互 + 时间动画
"""

import json
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from scipy.interpolate import make_interp_spline

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

def create_animated_3d(trajectories, output_path):
    """创建带时间动画的交互式3D可视化 - 完全复制静态版参数"""
    
    # 分类
    success_trajs = [t for t in trajectories if t['status'] == 'success']
    failure_trajs = [t for t in trajectories if t['status'] != 'success']
    
    # 坐标轴范围（与静态版一致）
    c_range = [-60, 25]
    a_range = [-60, 25]
    p_range = [-40, 20]
    
    # 找出最大轮次
    max_turns = max([len(t['points']) for t in trajectories])
    
    print(f"  最大轮次: {max_turns}")
    print(f"  创建动画frames...")
    
    # 创建初始frame（轮次0：所有轨迹占位，路径为空，仅保留起点与参考元素）
    initial_data = []
    
    # 1. 成功路径（空线条 + 空散点，用于后续帧填充）
    for i, traj in enumerate(success_trajs):
        script_id = traj['script_id']
        initial_data.append(go.Scatter3d(
            x=[np.nan], y=[np.nan], z=[np.nan],
            mode='lines',
            line=dict(color='#1f77b4', width=3),
            opacity=0.6,
            legendgroup='success',
            showlegend=False,
            hovertemplate=f'<b>{script_id}</b> (成功)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
        initial_data.append(go.Scatter3d(
            x=[np.nan], y=[np.nan], z=[np.nan],
            mode='markers',
            marker=dict(color='#1f77b4', size=2.0, line=dict(color='white', width=0.3)),
            opacity=0.4,
            legendgroup='success',
            showlegend=False,
            hovertemplate=f'<b>{script_id} - 轮次 %{{text}}</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>',
            text=[]
        ))
    
    # 2. 失败路径（空线条 + 空散点，占位）
    for i, traj in enumerate(failure_trajs):
        script_id = traj['script_id']
        initial_data.append(go.Scatter3d(
            x=[np.nan], y=[np.nan], z=[np.nan],
            mode='lines',
            line=dict(color='#d62728', width=3),
            opacity=0.6,
            legendgroup='failure',
            showlegend=False,
            hovertemplate=f'<b>{script_id}</b> (失败)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
        initial_data.append(go.Scatter3d(
            x=[np.nan], y=[np.nan], z=[np.nan],
            mode='markers',
            marker=dict(color='#d62728', size=1.5, line=dict(color='white', width=0.3)),
            opacity=0.4,
            legendgroup='failure',
            showlegend=False,
            hovertemplate=f'<b>{script_id} - 轮次 %{{text}}</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>',
            text=[]
        ))
    
    # 3. 起点（立即可见，图例使用单独trace）
    ordered_trajs = success_trajs + failure_trajs
    for i, traj in enumerate(ordered_trajs):
        points = traj['points']
        script_id = traj['script_id']
        initial_data.append(go.Scatter3d(
            x=[points[0, 0]],
            y=[points[0, 1]],
            z=[points[0, 2]],
            mode='markers',
            marker=dict(color='#08519c', size=2.5, symbol='circle', line=dict(color='white', width=0.5)),
            legendgroup='start',
            showlegend=False,
            hovertemplate=f'<b>{script_id} 起点</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
    
    # 4. 终点占位（初始为空，图例使用单独trace）
    for i, traj in enumerate(success_trajs):
        script_id = traj['script_id']
        initial_data.append(go.Scatter3d(
            x=[np.nan], y=[np.nan], z=[np.nan],
            mode='markers',
            marker=dict(color='#238b45', size=2.8, symbol='diamond', line=dict(color='white', width=0.5)),
            legendgroup='success_end',
            showlegend=False,
            hovertemplate=f'<b>{script_id} 终点</b> (成功)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
    for i, traj in enumerate(failure_trajs):
        script_id = traj['script_id']
        initial_data.append(go.Scatter3d(
            x=[np.nan], y=[np.nan], z=[np.nan],
            mode='markers',
            marker=dict(color='#a50f15', size=3.0, symbol='x', line=dict(color='white', width=0.5)),
            legendgroup='failure_end',
            showlegend=False,
            hovertemplate=f'<b>{script_id} 终点</b> (失败)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
    
    # 5. 原点标记
    initial_data.append(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers',
        marker=dict(color='gold', size=8, symbol='diamond', line=dict(color='#f97316', width=1.2)),
        name='目标原点',
        legendgroup='target_origin',
        legendrank=68,
        showlegend=False,
        hovertemplate='<b>目标原点</b><br>C: 0<br>A: 0<br>P: 0<extra></extra>'
    ))
    
    # 6. 坐标轴参考线
    for axis_data in [
        {'x': [0, c_range[1]], 'y': [0, 0], 'z': [0, 0], 'color': 'red', 'width': 4, 'dash': 'solid'},
        {'x': [c_range[0], 0], 'y': [0, 0], 'z': [0, 0], 'color': 'red', 'width': 3, 'dash': 'dash'},
        {'x': [0, 0], 'y': [0, a_range[1]], 'z': [0, 0], 'color': 'green', 'width': 4, 'dash': 'solid'},
        {'x': [0, 0], 'y': [a_range[0], 0], 'z': [0, 0], 'color': 'green', 'width': 3, 'dash': 'dash'},
        {'x': [0, 0], 'y': [0, 0], 'z': [0, p_range[1]], 'color': 'blue', 'width': 4, 'dash': 'solid'},
        {'x': [0, 0], 'y': [0, 0], 'z': [p_range[0], 0], 'color': 'blue', 'width': 3, 'dash': 'dash'},
    ]:
        initial_data.append(go.Scatter3d(
            x=axis_data['x'], y=axis_data['y'], z=axis_data['z'],
            mode='lines',
            line=dict(color=axis_data['color'], width=axis_data['width'], dash=axis_data['dash']),
            opacity=0.3,
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # 图例条目将通过独立的 legend-only trace 控制
    legend_only_traces = [
        go.Scatter3d(
            x=[0, 1], y=[0, 0], z=[0, 0],
            mode='lines',
            line=dict(color='#1f77b4', width=8),
            name='蓝色成功路径',
            legendgroup='success',
            showlegend=True,
            visible='legendonly',
            hoverinfo='skip',
            legendrank=60
        ),
        go.Scatter3d(
            x=[0, 1], y=[0, 0], z=[0, 0],
            mode='lines',
            line=dict(color='#d62728', width=8),
            name='红色失败路径',
            legendgroup='failure',
            showlegend=True,
            visible='legendonly',
            hoverinfo='skip',
            legendrank=61
        ),
        go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(color='#08519c', size=10, symbol='circle', line=dict(color='white', width=1.6)),
            name='起点',
            legendgroup='start',
            showlegend=True,
            visible='legendonly',
            hoverinfo='skip',
            legendrank=70
        ),
        go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(color='#238b45', size=11, symbol='diamond', line=dict(color='white', width=1.6)),
            name='成功终点',
            legendgroup='success_end',
            showlegend=True,
            visible='legendonly',
            hoverinfo='skip',
            legendrank=71
        ),
        go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(color='#a50f15', size=11, symbol='x', line=dict(color='white', width=1.6)),
            name='失败终点',
            legendgroup='failure_end',
            showlegend=True,
            visible='legendonly',
            hoverinfo='skip',
            legendrank=72
        ),
        go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(color='gold', size=12, symbol='diamond', line=dict(color='#f97316', width=1.8)),
            name='目标原点',
            legendgroup='target_origin',
            showlegend=True,
            visible='legendonly',
            hoverinfo='skip',
            legendrank=73
        ),
    ]
    initial_data.extend(legend_only_traces)
    
    # 创建动画frames（纯色，不渐变）
    print(f"  生成{max_turns}个动画帧...")
    frames = []
    
    for turn in range(1, max_turns + 1):
        frame_data = []
        
        # 成功路径：线条 + 轨迹点（顺序与initial_data一致）
        for idx, traj in enumerate(success_trajs):
            points = traj['points']
            script_id = traj['script_id']
            max_index = min(turn, len(points) - 1)
            current_points = points[:max_index + 1]
            showlegend_success = False
            if len(current_points) >= 2:
                smooth_points = smooth_trajectory(current_points, num_points=min(100, len(current_points) * 10))
                line_x, line_y, line_z = smooth_points[:, 0], smooth_points[:, 1], smooth_points[:, 2]
                progress_steps = np.linspace(1, len(current_points), len(smooth_points))
                line_hovertemplate = '第 %{customdata:.1f} 轮<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>'
            else:
                line_x = line_y = line_z = []
                progress_steps = []
                line_hovertemplate = 'C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>'
            
            frame_data.append(go.Scatter3d(
                x=line_x, y=line_y, z=line_z,
                mode='lines',
                line=dict(color='#1f77b4', width=3),
                opacity=0.6,
                legendgroup='success',
                showlegend=False,
                customdata=progress_steps if len(progress_steps) else None,
                hovertemplate=f'<b>{script_id}</b> (成功)<br>{line_hovertemplate}'
            ))
            
            if len(current_points) >= 1:
                marker_x, marker_y, marker_z = current_points[:, 0], current_points[:, 1], current_points[:, 2]
                marker_text = [f'{j+1}' for j in range(len(current_points))]
            else:
                marker_x = marker_y = marker_z = []
                marker_text = []
            
            frame_data.append(go.Scatter3d(
                x=marker_x, y=marker_y, z=marker_z,
                mode='markers',
                marker=dict(color='#1f77b4', size=2.0, line=dict(color='white', width=0.3)),
                opacity=0.4,
                legendgroup='success',
                showlegend=False,
                hovertemplate=f'<b>{script_id} - 轮次 %{{text}}</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>',
                text=marker_text
            ))
        
        # 失败路径
        for idx, traj in enumerate(failure_trajs):
            points = traj['points']
            script_id = traj['script_id']
            max_index = min(turn, len(points) - 1)
            current_points = points[:max_index + 1]
            showlegend_failure = False
            
            if len(current_points) >= 2:
                smooth_points = smooth_trajectory(current_points, num_points=min(100, len(current_points) * 10))
                line_x, line_y, line_z = smooth_points[:, 0], smooth_points[:, 1], smooth_points[:, 2]
                progress_steps = np.linspace(1, len(current_points), len(smooth_points))
                line_hovertemplate = '第 %{customdata:.1f} 轮<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>'
            else:
                line_x = line_y = line_z = []
                progress_steps = []
                line_hovertemplate = 'C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>'
            
            frame_data.append(go.Scatter3d(
                x=line_x, y=line_y, z=line_z,
                mode='lines',
                line=dict(color='#d62728', width=3),
                opacity=0.6,
                legendgroup='failure',
                showlegend=False,
                customdata=progress_steps if len(progress_steps) else None,
                hovertemplate=f'<b>{script_id}</b> (失败)<br>{line_hovertemplate}'
            ))
            
            if len(current_points) >= 1:
                marker_x, marker_y, marker_z = current_points[:, 0], current_points[:, 1], current_points[:, 2]
                marker_text = [f'{j+1}' for j in range(len(current_points))]
            else:
                marker_x = marker_y = marker_z = []
                marker_text = []
            
            frame_data.append(go.Scatter3d(
                x=marker_x, y=marker_y, z=marker_z,
                mode='markers',
                marker=dict(color='#d62728', size=1.5, line=dict(color='white', width=0.3)),
                opacity=0.4,
                legendgroup='failure',
                showlegend=False,
                hovertemplate=f'<b>{script_id} - 轮次 %{{text}}</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>',
                text=marker_text
            ))
        
        # 起点（恒定）
        for idx, traj in enumerate(ordered_trajs):
            points = traj['points']
            script_id = traj['script_id']
            showlegend_start = False
            frame_data.append(go.Scatter3d(
                x=[points[0, 0]],
                y=[points[0, 1]],
                z=[points[0, 2]],
                mode='markers',
                marker=dict(color='#08519c', size=2.5, symbol='circle', line=dict(color='white', width=0.5)),
                legendgroup='start',
                name='起点' if showlegend_start else None,
                showlegend=showlegend_start,
                hovertemplate=f'<b>{script_id} 起点</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
            ))
        
        # 成功终点（达到终点前为空）
        for idx, traj in enumerate(success_trajs):
            points = traj['points']
            script_id = traj['script_id']
            if turn >= len(points) - 1:
                end_x, end_y, end_z = [points[-1, 0]], [points[-1, 1]], [points[-1, 2]]
            else:
                end_x = end_y = end_z = [np.nan]
            showlegend_success_end = False
            frame_data.append(go.Scatter3d(
                x=end_x, y=end_y, z=end_z,
                mode='markers',
                marker=dict(color='#238b45', size=2.8, symbol='diamond', line=dict(color='white', width=0.5)),
                legendgroup='success_end',
                showlegend=False,
                hovertemplate=f'<b>{script_id} 终点</b> (成功)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
            ))
        
        # 失败终点
        for idx, traj in enumerate(failure_trajs):
            points = traj['points']
            script_id = traj['script_id']
            if turn >= len(points) - 1:
                end_x, end_y, end_z = [points[-1, 0]], [points[-1, 1]], [points[-1, 2]]
            else:
                end_x = end_y = end_z = [np.nan]
            showlegend_failure_end = False
            frame_data.append(go.Scatter3d(
                x=end_x, y=end_y, z=end_z,
                mode='markers',
                marker=dict(color='#a50f15', size=3.0, symbol='x', line=dict(color='white', width=0.5)),
                legendgroup='failure_end',
                showlegend=False,
                hovertemplate=f'<b>{script_id} 终点</b> (失败)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
            ))
        
        # 原点
        frame_data.append(go.Scatter3d(
            x=[0], y=[0], z=[0],
            mode='markers',
            marker=dict(color='gold', size=6, symbol='diamond', line=dict(color='orange', width=1)),
            legendgroup='target_origin',
            showlegend=False,
            hovertemplate='<b>目标原点</b><br>C: 0<br>A: 0<br>P: 0<extra></extra>'
        ))
        
        # 坐标轴参考线
        for axis_data in [
            {'x': [0, c_range[1]], 'y': [0, 0], 'z': [0, 0], 'color': 'red', 'width': 4, 'dash': 'solid'},
            {'x': [c_range[0], 0], 'y': [0, 0], 'z': [0, 0], 'color': 'red', 'width': 3, 'dash': 'dash'},
            {'x': [0, 0], 'y': [0, a_range[1]], 'z': [0, 0], 'color': 'green', 'width': 4, 'dash': 'solid'},
            {'x': [0, 0], 'y': [a_range[0], 0], 'z': [0, 0], 'color': 'green', 'width': 3, 'dash': 'dash'},
            {'x': [0, 0], 'y': [0, 0], 'z': [0, p_range[1]], 'color': 'blue', 'width': 4, 'dash': 'solid'},
            {'x': [0, 0], 'y': [0, 0], 'z': [p_range[0], 0], 'color': 'blue', 'width': 3, 'dash': 'dash'},
        ]:
            frame_data.append(go.Scatter3d(
                x=axis_data['x'], y=axis_data['y'], z=axis_data['z'],
                mode='lines',
                line=dict(color=axis_data['color'], width=axis_data['width'], dash=axis_data['dash']),
                opacity=0.3,
                showlegend=False,
                hoverinfo='skip'
            ))
        
        frames.append(go.Frame(data=frame_data, name=f'turn_{turn}', layout={'title': f'第 {turn} 轮'}))
    
    # 创建figure
    fig = go.Figure(data=initial_data, frames=frames)
    
    # 清理图例：只保留命名好的项目
    allowed_legend_names = {"蓝色成功路径", "红色失败路径", "起点", "成功终点", "失败终点", "目标原点"}
    for trace in fig.data:
        if trace.name not in allowed_legend_names:
            trace.showlegend = False
    debug_legend_names = [(trace.name, trace.showlegend) for trace in fig.data if trace.showlegend]
    print("  图例显示项：", debug_legend_names)
    
    # 布局（与静态版一致）
    fig.update_layout(
        title=dict(text=' '),
        autosize=True,
        height=720,
        margin=dict(t=70, b=70, l=56, r=220),
        dragmode='turntable',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest',
        hoverlabel=dict(bgcolor='rgba(15,23,42,0.9)', font=dict(size=12, color='#f8fafc')),
        legend=dict(
            title=dict(text='<b>图例</b>'),
            x=1.02,
            xanchor='left',
            y=0.98,
            yanchor='top',
            bgcolor='rgba(255,255,255,0.88)',
            bordercolor='#d4d8e2',
            borderwidth=1,
            font=dict(size=12, color='#1f2937'),
            groupclick='togglegroup'
        ),
        legend_tracegroupgap=12,
        scene=dict(
            xaxis=dict(
                title=dict(
                    text='<b>认知轴 Cognitive (C)</b><br>← 赤字 | 充足 →',
                    font=dict(size=13, color='#0f172a')
                ),
                range=c_range,
                backgroundcolor='#ffffff',
                gridcolor='#e2e8f0',
                showbackground=True,
                zerolinecolor='darkred',
                zerolinewidth=3,
                autorange='reversed',
                tickfont=dict(size=11, color='#334155')
            ),
            yaxis=dict(
                title=dict(
                    text='<b>情感轴 Affective (A)</b><br>← 赤字 | 充足 →',
                    font=dict(size=13, color='#0f172a')
                ),
                range=a_range,
                backgroundcolor='#ffffff',
                gridcolor='#e2e8f0',
                showbackground=True,
                zerolinecolor='darkgreen',
                zerolinewidth=3,
                autorange='reversed',
                tickfont=dict(size=11, color='#334155')
            ),
            zaxis=dict(
                title=dict(
                    text='<b>动机轴 Proactive (P)</b><br>← 赤字 | 充足 →',
                    font=dict(size=13, color='#0f172a')
                ),
                range=p_range,
                backgroundcolor='#ffffff',
                gridcolor='#e2e8f0',
                showbackground=True,
                zerolinecolor='darkblue',
                zerolinewidth=3,
                autorange='reversed',
                tickfont=dict(size=11, color='#334155')
            ),
            camera=dict(
                eye=dict(x=-1.5, y=-1.5, z=1.2),
                center=dict(x=0, y=0, z=0)
            ),
            aspectmode='cube'
        ),
        font=dict(family="PingFang SC, 'Microsoft YaHei', sans-serif", size=13, color='#1f2937'),
        updatemenus=[dict(
            type='buttons',
            showactive=False,
            buttons=[
                dict(label='▶️ 播放',
                     method='animate',
                     args=[None, dict(
                         frame=dict(duration=300, redraw=True),
                         fromcurrent=True,
                         mode='immediate',
                         transition=dict(duration=0)
                     )]),
                dict(label='⏸️ 暂停',
                     method='animate',
                     args=[[None], dict(
                         frame=dict(duration=0, redraw=False),
                         mode='immediate',
                         transition=dict(duration=0)
                     )])
            ],
            direction='left',
            pad=dict(r=10, t=0),
            x=0.02,
            xanchor='left',
            y=0.94,
            yanchor='bottom'
        )],
        sliders=[dict(
            active=0,
            yanchor='bottom',
            y=0.96,
            xanchor='left',
            x=0.23,
            currentvalue=dict(
                prefix='当前轮次: ',
                visible=True,
                xanchor='left',
                font=dict(size=13, color='#1f2937')
            ),
            pad=dict(b=4, t=4),
            len=0.72,
            steps=[dict(
                args=[[f'turn_{turn}'], dict(
                    frame=dict(duration=0, redraw=True),
                    mode='immediate',
                    transition=dict(duration=0)
                )],
                method='animate',
                label=f'{turn}',
                value=f'{turn}'
            ) for turn in range(1, max_turns + 1)]
        )]
    )
    
    # 保存
    print(f"  保存动画HTML...")
    fig.write_html(output_path, include_plotlyjs='cdn')
    
    # 添加相机限制
    custom_js = """
    <script>
    var plot = document.getElementsByClassName('plotly-graph-div')[0];
    plot.on('plotly_relayout', function(eventdata) {
        if (eventdata['scene.camera']) {
            var camera = eventdata['scene.camera'];
            if (camera.eye) {
                var z = camera.eye.z;
                var minZ = 0.3;
                var maxZ = 2.0;
                if (z < minZ) {
                    camera.eye.z = minZ;
                    Plotly.relayout(plot, {'scene.camera.eye': camera.eye});
                } else if (z > maxZ) {
                    camera.eye.z = maxZ;
                    Plotly.relayout(plot, {'scene.camera.eye': camera.eye});
                }
            }
        }
    });
    </script>
    """
    
    custom_css = """
    <style>
    html, body {
        margin: 0;
        padding: 0;
        height: 100%;
    }
    body.viz-body {
        background: linear-gradient(180deg, #f3f6fb 0%, #f8f9fc 100%);
        font-family: "PingFang SC","Microsoft YaHei",sans-serif;
        color: #1f2937;
    }
    .viz-wrapper {
        max-width: 1500px;
        margin: 0 auto;
        padding: 20px 32px 32px;
        box-sizing: border-box;
        min-height: 100%;
        display: flex;
        flex-direction: column;
    }
    .viz-card {
        background: #ffffff;
        border-radius: 22px;
        box-shadow: 0 28px 70px rgba(15, 40, 80, 0.08);
        padding: 24px 36px 26px;
        flex: 1;
        display: flex;
        flex-direction: column;
    }
    .viz-header {
        display: flex;
        align-items: flex-end;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 16px;
    }
    .viz-title {
        margin: 0;
        font-size: 28px;
        font-weight: 600;
        color: #0f172a;
        letter-spacing: 0.01em;
    }
    .viz-subtitle {
        margin: 4px 0 0;
        font-size: 15px;
        color: #475569;
    }
    .viz-badges {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    .viz-chip {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: #e0ecff;
        color: #1d4ed8;
        font-size: 12px;
        font-weight: 500;
        letter-spacing: 0.02em;
    }
    .viz-chip-danger {
        background: #fde2e2;
        color: #b91c1c;
    }
    .viz-instruction {
        margin-top: 6px;
        padding: 14px 16px;
        border-radius: 14px;
        background: linear-gradient(135deg, rgba(59,130,246,0.1) 0%, rgba(59,130,246,0.04) 100%);
        border: 1px solid rgba(59,130,246,0.18);
        color: #1e3a8a;
        font-size: 13px;
        line-height: 1.6;
    }
    .viz-instruction strong {
        display: inline-block;
        min-width: 92px;
        color: #1d4ed8;
    }
    .viz-instruction ul {
        margin: 8px 0 0;
        padding-left: 16px;
    }
    .viz-instruction li {
        margin: 4px 0;
    }
    .viz-footer {
        margin-top: 14px;
        text-align: right;
        font-size: 12px;
        color: #617086;
    }
    .plotly-graph-div {
        width: 100% !important;
        height: 620px !重要;
        border-radius: 18px;
        box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.04);
        margin-top: 10px;
        flex: 1;
    }
    @media (max-width: 1440px) {
        .viz-wrapper { padding: 22px 24px 28px; }
        .viz-card { padding: 26px 28px 28px; }
    }
    @media (max-width: 960px) {
        .viz-wrapper { padding: 18px 16px 24px; }
        .viz-card { padding: 24px; }
        .plotly-graph-div { height: 600px !important; margin-top: 16px; }
        .viz-title { font-size: 24px; }
        .viz-subtitle { font-size: 13px; }
    }
    @media (max-width: 720px) {
        .viz-header { flex-direction: column; align-items: flex-start; }
        .viz-badges { gap: 6px; }
        .plotly-graph-div { height: 540px !important; margin-top: 12px; }
    }
    </style>
    """
    
    header_html = """
    <div class="viz-wrapper">
      <div class="viz-card">
        <header class="viz-header">
          <div class="viz-heading">
            <h1 class="viz-title">EPM 共情修复轨迹 · 时间动画</h1>
            <p class="viz-subtitle">点击“播放”观看轨迹从起点生长，使用图例切换成功/失败路径。</p>
          </div>
          <div class="viz-badges">
            <span class="viz-chip">30 条真实案例</span>
            <span class="viz-chip viz-chip-danger">蓝色成功 · 红色失败</span>
          </div>
        </header>
      <div class="viz-instruction">
        <strong>交互提示：</strong>
        <ul>
          <li>鼠标拖动：绕三轴旋转；按住 Shift + 拖动：平移视角</li>
          <li>滚轮缩放：拉近/拉远；双击恢复初始视角</li>
          <li>图例点击：显示/隐藏某类轨迹或终点标记</li>
          <li>悬停轨迹：查看该点所在轮次与三轴坐标</li>
        </ul>
      </div>
    """
    
    footer_html = """
        <p class="viz-footer">Tips：图例可点击隐藏类别 · 鼠标拖动旋转视角 · Shift + 滚轮进行平移</p>
      </div>
    </div>
    """
    
    with open(output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = html_content.replace('<head>', f'<head>\n{custom_css}', 1)
    html_content = html_content.replace('<body>', '<body class="viz-body">\n' + header_html, 1)
    html_content = html_content.replace('</body>', f'{footer_html}\n{custom_js}</body>')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 已保存: {output_path}")
    print(f"   💡 动画功能：")
    print(f"      • 🎬 点击'播放'按钮观看轨迹从起点开始生长")
    print(f"      • ⏸️ 点击'暂停'停止动画")
    print(f"      • 🎚️ 拖动滑块跳到指定轮次")
    print(f"      • 🔵 蓝色=成功路径 | 🔴 红色=失败路径")

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_trajectories_plotly"
    output_dir.mkdir(exist_ok=True)
    
    print("🎬 Plotly交互式3D轨迹动画可视化\n")
    print("📌 特性: 复制静态版参数 + 路径生长动画\n")
    
    trajectories = load_all_trajectories(results_dir)
    print(f"✅ 已加载 {len(trajectories)} 个案例\n")
    
    success_count = len([t for t in trajectories if t['status'] == 'success'])
    failure_count = len(trajectories) - success_count
    
    print(f"📊 创建动画可视化...")
    print(f"   💙 成功轨迹: {success_count} 条（纯蓝色）")
    print(f"   ❤️ 失败轨迹: {failure_count} 条（纯红色）")
    print(f"   🎬 动画模式: 轨迹从起点逐轮生长\n")
    
    create_animated_3d(trajectories, output_dir / "interactive_3d_animated.html")
    
    print(f"\n✅ 完成！")
    print(f"📁 输出位置: {output_dir}")
    print(f"\n💡 打开方式: 用浏览器打开 interactive_3d_animated.html")

if __name__ == "__main__":
    main()

