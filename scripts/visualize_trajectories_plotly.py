#!/usr/bin/env python3
"""
Plotly交互式3D轨迹可视化
真正的3D渲染 + 完全交互
"""

import json
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

def create_interactive_3d(trajectories, output_path):
    """创建交互式3D可视化"""
    
    # 分类
    success_trajs = [t for t in trajectories if t['status'] == 'success']
    failure_trajs = [t for t in trajectories if t['status'] != 'success']
    
    # 创建figure
    fig = go.Figure()
    
    # 坐标轴范围设置
    # 实际数据范围: C[-42,18], A[-58,12], P[-27,21]
    c_range = [-60, 25]  # 认知轴
    a_range = [-60, 25]  # 情感轴
    p_range = [-40, 20]  # 动机轴（用户指定）
    
    print(f"  添加所有成功轨迹...")
    # 1. 所有成功轨迹（统一蓝色）
    for i, traj in enumerate(success_trajs):
        points = traj['points']
        script_id = traj['script_id']
        smooth_points = smooth_trajectory(points, num_points=100)
        
        # 平滑路径
        fig.add_trace(go.Scatter3d(
            x=smooth_points[:, 0],
            y=smooth_points[:, 1],
            z=smooth_points[:, 2],
            mode='lines',
            line=dict(color='#1f77b4', width=3),
            opacity=0.6,
            name='成功路径' if i == 0 else None,
            legendgroup='success',
            showlegend=(i == 0),
            hovertemplate=f'<b>{script_id}</b> (成功)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
        
        # 原始点（带悬停信息）- 缩小
        fig.add_trace(go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='markers',
            marker=dict(
                color='#1f77b4',
                size=2.0,
                line=dict(color='white', width=0.3)
            ),
            opacity=0.4,
            showlegend=False,
            legendgroup='success',
            hovertemplate=f'<b>{script_id} - 轮次 %{{text}}</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>',
            text=[f'{j+1}' for j in range(len(points))]
        ))
        
        # 起点标记 - 缩小
        fig.add_trace(go.Scatter3d(
            x=[points[0, 0]],
            y=[points[0, 1]],
            z=[points[0, 2]],
            mode='markers',
            marker=dict(
                color='#08519c',
                size=2.5,
                symbol='circle',
                line=dict(color='white', width=0.5)
            ),
            name='起点' if i == 0 else None,
            legendgroup='start',
            showlegend=(i == 0),
            hovertemplate=f'<b>{script_id} 起点</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
        
        # 终点标记 - 缩小
        fig.add_trace(go.Scatter3d(
            x=[points[-1, 0]],
            y=[points[-1, 1]],
            z=[points[-1, 2]],
            mode='markers',
            marker=dict(
                color='#238b45',
                size=2.8,
                symbol='diamond',
                line=dict(color='white', width=0.5)
            ),
            name='成功终点' if i == 0 else None,
            legendgroup='success_end',
            showlegend=(i == 0),
            hovertemplate=f'<b>{script_id} 终点</b> (成功)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
    
    print(f"  添加所有失败轨迹...")
    # 2. 所有失败轨迹（统一红色）
    for i, traj in enumerate(failure_trajs):
        points = traj['points']
        script_id = traj['script_id']
        smooth_points = smooth_trajectory(points, num_points=100)
        
        # 平滑路径
        fig.add_trace(go.Scatter3d(
            x=smooth_points[:, 0],
            y=smooth_points[:, 1],
            z=smooth_points[:, 2],
            mode='lines',
            line=dict(color='#d62728', width=3),
            opacity=0.6,
            name='失败路径' if i == 0 else None,
            legendgroup='failure',
            showlegend=(i == 0),
            hovertemplate=f'<b>{script_id}</b> (失败)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
        
        # 原始点 - 缩小
        fig.add_trace(go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='markers',
            marker=dict(
                color='#d62728',
                size=1.5,
                line=dict(color='white', width=0.3)
            ),
            opacity=0.4,
            showlegend=False,
            legendgroup='failure',
            hovertemplate=f'<b>{script_id} - 轮次 %{{text}}</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>',
            text=[f'{j+1}' for j in range(len(points))]
        ))
        
        # 起点标记 - 缩小
        fig.add_trace(go.Scatter3d(
            x=[points[0, 0]],
            y=[points[0, 1]],
            z=[points[0, 2]],
            mode='markers',
            marker=dict(
                color='#08519c',
                size=2.5,
                symbol='circle',
                line=dict(color='white', width=0.5)
            ),
            showlegend=False,
            legendgroup='start',
            hovertemplate=f'<b>{script_id} 起点</b><br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
        
        # 终点标记 - 缩小
        fig.add_trace(go.Scatter3d(
            x=[points[-1, 0]],
            y=[points[-1, 1]],
            z=[points[-1, 2]],
            mode='markers',
            marker=dict(
                color='#a50f15',
                size=2.5,
                symbol='x',
                line=dict(color='white', width=0.5)
            ),
            name='失败终点' if i == 0 else None,
            legendgroup='failure_end',
            showlegend=(i == 0),
            hovertemplate=f'<b>{script_id} 终点</b> (失败)<br>C: %{{x:.1f}}<br>A: %{{y:.1f}}<br>P: %{{z:.1f}}<extra></extra>'
        ))
    
    print(f"  添加参考元素...")
    # 3. 原点标记（金色菱形，精简）
    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[0],
        z=[0],
        mode='markers',
        marker=dict(
            color='gold',
            size=6,
            symbol='diamond',
            line=dict(color='orange', width=1)
        ),
        name='目标原点',
        hovertemplate='<b>目标原点</b><br>C: 0<br>A: 0<br>P: 0<extra></extra>'
    ))
    
    # 4. 坐标轴参考线（适应不对称范围）
    # X轴（认知）C: [-40, 20]
    fig.add_trace(go.Scatter3d(
        x=[0, c_range[1]],
        y=[0, 0],
        z=[0, 0],
        mode='lines',
        line=dict(color='red', width=4, dash='solid'),
        opacity=0.4,
        name='认知轴+',
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter3d(
        x=[c_range[0], 0],
        y=[0, 0],
        z=[0, 0],
        mode='lines',
        line=dict(color='red', width=3, dash='dash'),
        opacity=0.3,
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Y轴（情感）A: [-40, 2]
    fig.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0, a_range[1]],
        z=[0, 0],
        mode='lines',
        line=dict(color='green', width=4, dash='solid'),
        opacity=0.4,
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[a_range[0], 0],
        z=[0, 0],
        mode='lines',
        line=dict(color='green', width=3, dash='dash'),
        opacity=0.3,
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Z轴（动机）P: [-40, 20]
    fig.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[0, p_range[1]],
        mode='lines',
        line=dict(color='blue', width=4, dash='solid'),
        opacity=0.4,
        showlegend=False,
        hoverinfo='skip'
    ))
    fig.add_trace(go.Scatter3d(
        x=[0, 0],
        y=[0, 0],
        z=[p_range[0], 0],
        mode='lines',
        line=dict(color='blue', width=3, dash='dash'),
        opacity=0.3,
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # 布局设置
    fig.update_layout(
        title=dict(
            text='<b>交互式3D轨迹可视化 | Plotly WebGL渲染</b><br>'
                 '<sub>🖱️ 鼠标拖动旋转 | 滚轮缩放 | 悬停查看数据</sub>',
            x=0.5,
            xanchor='center',
            font=dict(size=20, color='#222222')
        ),
        dragmode='turntable',  # 转盘模式：水平旋转+垂直倾斜，防止坐标轴翻转
        scene=dict(
            xaxis=dict(
                title='<b>认知轴 Cognitive (C)</b><br>← 赤字 | 充足 →',
                range=c_range,
                backgroundcolor='#fafafa',
                gridcolor='#e0e0e0',
                showbackground=True,
                zerolinecolor='darkred',
                zerolinewidth=3,
                autorange='reversed'
            ),
            yaxis=dict(
                title='<b>情感轴 Affective (A)</b><br>← 赤字 | 充足 →',
                range=a_range,
                backgroundcolor='#fafafa',
                gridcolor='#e0e0e0',
                showbackground=True,
                zerolinecolor='darkgreen',
                zerolinewidth=3,
                autorange='reversed'
            ),
            zaxis=dict(
                title='<b>动机轴 Proactive (P)</b><br>← 赤字 | 充足 →',
                range=p_range,
                backgroundcolor='#fafafa',
                gridcolor='#e0e0e0',
                showbackground=True,
                zerolinecolor='darkblue',
                zerolinewidth=3,
                autorange='reversed'
            ),
            camera=dict(
                eye=dict(x=-1.5, y=-1.5, z=1.2),
                center=dict(x=0, y=0, z=0)
            ),
            aspectmode='cube'  # 立方体模式，确保三个轴比例相同，单位刻度一致
        ),
        width=1400,
        height=900,
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#cccccc',
            borderwidth=2,
            font=dict(size=11)
        ),
        hovermode='closest',
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    # 保存为HTML并添加相机角度限制
    print(f"  保存交互式HTML...")
    
    # 自定义JavaScript：限制只能水平旋转（绕Z轴）
    custom_js = """
    <script>
    // 限制相机只能水平旋转，不能垂直翻转
    var plot = document.getElementsByClassName('plotly-graph-div')[0];
    
    plot.on('plotly_relayout', function(eventdata) {
        if (eventdata['scene.camera']) {
            var camera = eventdata['scene.camera'];
            if (camera.eye) {
                // 限制垂直角度：保持Z坐标在合理范围
                var x = camera.eye.x;
                var y = camera.eye.y;
                var z = camera.eye.z;
                
                // 计算水平距离
                var horizontalDist = Math.sqrt(x*x + y*y);
                
                // 限制Z的范围，防止上下翻转
                // 允许从正上方看（z=2）到平视（z=0.3），但不能从下往上看
                var minZ = 0.3;
                var maxZ = 2.0;
                
                if (z < minZ) {
                    z = minZ;
                    camera.eye.z = z;
                    Plotly.relayout(plot, {'scene.camera.eye': camera.eye});
                } else if (z > maxZ) {
                    z = maxZ;
                    camera.eye.z = z;
                    Plotly.relayout(plot, {'scene.camera.eye': camera.eye});
                }
            }
        }
    });
    </script>
    """
    
    # 先生成基本HTML
    fig.write_html(output_path, include_plotlyjs='cdn')
    
    # 读取HTML并注入JavaScript
    with open(output_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 在</body>之前插入自定义JavaScript
    html_content = html_content.replace('</body>', f'{custom_js}</body>')
    
    # 写回文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 已保存: {output_path}")
    print(f"   💡 用浏览器打开此文件可以：")
    print(f"      • 🖱️ 水平旋转视角（限制垂直翻转）")
    print(f"      • 🔍 滚轮缩放")
    print(f"      • 👆 悬停查看详细数据")
    print(f"      • 📸 点击相机图标截图")

def main():
    """主函数"""
    results_dir = "results/benchmark_runs/default_20251106_233640"
    output_dir = Path(results_dir) / "3d_trajectories_plotly"
    output_dir.mkdir(exist_ok=True)
    
    print("🎨 Plotly交互式3D轨迹可视化\n")
    
    # 加载数据
    trajectories = load_all_trajectories(results_dir)
    print(f"✅ 已加载 {len(trajectories)} 个案例\n")
    
    success_count = len([t for t in trajectories if t['status'] == 'success'])
    failure_count = len(trajectories) - success_count
    
    print(f"📊 创建交互式3D可视化...")
    print(f"   💙 成功轨迹: {success_count} 条（蓝色）")
    print(f"   ❤️ 失败轨迹: {failure_count} 条（红色）")
    print(f"   📍 所有轨迹统一样式，带script ID悬停信息\n")
    
    create_interactive_3d(trajectories, output_dir / "interactive_3d.html")
    
    print(f"\n✅ 完成！")
    print(f"📁 输出位置: {output_dir}")
    print(f"\n💡 打开方式: 直接用浏览器打开 interactive_3d.html")
    print(f"   Chrome/Safari/Firefox 都支持")

if __name__ == "__main__":
    main()

