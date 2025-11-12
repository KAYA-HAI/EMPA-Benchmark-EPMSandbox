/**
 * EPM轨迹3D可视化 - 前端独立版本
 * 支持动态加载数据、时间动画、多模型切换
 */

// B-spline平滑函数（简化版，使用线性插值）
function smoothTrajectory(points, numPoints = 100) {
    if (points.length < 4) return points;
    
    // 计算累积距离
    let distances = [0];
    for (let i = 1; i < points.length; i++) {
        const dx = points[i][0] - points[i-1][0];
        const dy = points[i][1] - points[i-1][1];
        const dz = points[i][2] - points[i-1][2];
        distances.push(distances[i-1] + Math.sqrt(dx*dx + dy*dy + dz*dz));
    }
    
    const totalDist = distances[distances.length - 1];
    if (totalDist === 0) return points;
    
    // 归一化参数
    const t = distances.map(d => d / totalDist);
    
    // 线性插值生成平滑点
    const smoothPoints = [];
    for (let i = 0; i < numPoints; i++) {
        const targetT = i / (numPoints - 1);
        
        // 找到对应的区间
        let idx = 0;
        while (idx < t.length - 1 && t[idx + 1] < targetT) idx++;
        
        if (idx >= points.length - 1) {
            smoothPoints.push(points[points.length - 1]);
            continue;
        }
        
        // 线性插值
        const localT = (targetT - t[idx]) / (t[idx + 1] - t[idx]);
        const x = points[idx][0] + localT * (points[idx + 1][0] - points[idx][0]);
        const y = points[idx][1] + localT * (points[idx + 1][1] - points[idx][1]);
        const z = points[idx][2] + localT * (points[idx + 1][2] - points[idx][2]);
        
        smoothPoints.push([x, y, z]);
    }
    
    return smoothPoints;
}

// 创建动画可视化
function createAnimated3D(trajectories, metadata) {
    const successTrajs = trajectories.filter(t => t.status === 'success');
    const failureTrajs = trajectories.filter(t => t.status !== 'success');
    
    // 坐标轴范围
    const cRange = [-60, 25];
    const aRange = [-60, 25];
    const pRange = [-40, 20];
    
    const maxTurns = metadata.max_turns;
    
    console.log(`创建动画: ${maxTurns} 轮, ${successTrajs.length} 成功, ${failureTrajs.length} 失败`);
    
    // 初始数据（轮次0：仅起点、原点、坐标轴）
    const initialData = [];
    
    // 1. 成功路径占位（空线条 + 空散点）
    successTrajs.forEach((traj, i) => {
        initialData.push({
            x: [NaN], y: [NaN], z: [NaN],
            type: 'scatter3d',
            mode: 'lines',
            line: { color: '#1f77b4', width: 3 },
            opacity: 0.6,
            legendgroup: 'success',
            showlegend: false,
            hovertemplate: `<b>${traj.script_id}</b> (成功)<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
        });
        initialData.push({
            x: [NaN], y: [NaN], z: [NaN],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: '#1f77b4', size: 2.0, line: { color: 'white', width: 0.3 } },
            opacity: 0.4,
            legendgroup: 'success',
            showlegend: false,
            hovertemplate: `<b>${traj.script_id} - 轮次 %{text}</b><br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`,
            text: []
        });
    });
    
    // 2. 失败路径占位
    failureTrajs.forEach((traj, i) => {
        initialData.push({
            x: [NaN], y: [NaN], z: [NaN],
            type: 'scatter3d',
            mode: 'lines',
            line: { color: '#d62728', width: 3 },
            opacity: 0.6,
            legendgroup: 'failure',
            showlegend: false,
            hovertemplate: `<b>${traj.script_id}</b> (失败)<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
        });
        initialData.push({
            x: [NaN], y: [NaN], z: [NaN],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: '#d62728', size: 1.5, line: { color: 'white', width: 0.3 } },
            opacity: 0.4,
            legendgroup: 'failure',
            showlegend: false,
            hovertemplate: `<b>${traj.script_id} - 轮次 %{text}</b><br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`,
            text: []
        });
    });
    
    // 3. 起点（立即可见）
    const orderedTrajs = [...successTrajs, ...failureTrajs];
    orderedTrajs.forEach(traj => {
        const p0 = traj.points[0];
        initialData.push({
            x: [p0[0]], y: [p0[1]], z: [p0[2]],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: '#08519c', size: 2.5, symbol: 'circle', line: { color: 'white', width: 0.5 } },
            legendgroup: 'start',
            showlegend: false,
            hovertemplate: `<b>${traj.script_id} 起点</b><br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
        });
    });
    
    // 4. 终点占位
    successTrajs.forEach(traj => {
        initialData.push({
            x: [NaN], y: [NaN], z: [NaN],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: '#238b45', size: 2.8, symbol: 'diamond', line: { color: 'white', width: 0.5 } },
            legendgroup: 'success_end',
            showlegend: false,
            hovertemplate: `<b>${traj.script_id} 终点</b> (成功)<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
        });
    });
    failureTrajs.forEach(traj => {
        initialData.push({
            x: [NaN], y: [NaN], z: [NaN],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: '#a50f15', size: 3.0, symbol: 'x', line: { color: 'white', width: 0.5 } },
            legendgroup: 'failure_end',
            showlegend: false,
            hovertemplate: `<b>${traj.script_id} 终点</b> (失败)<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
        });
    });
    
    // 5. 原点标记
    initialData.push({
        x: [0], y: [0], z: [0],
        type: 'scatter3d',
        mode: 'markers',
        marker: { color: 'gold', size: 8, symbol: 'diamond', line: { color: '#f97316', width: 1.2 } },
        legendgroup: 'target_origin',
        showlegend: false,
        hovertemplate: '<b>目标原点</b><br>C: 0<br>A: 0<br>P: 0<extra></extra>'
    });
    
    // 6. 坐标轴参考线
    const axisLines = [
        { x: [0, cRange[1]], y: [0, 0], z: [0, 0], color: 'red', width: 4, dash: 'solid' },
        { x: [cRange[0], 0], y: [0, 0], z: [0, 0], color: 'red', width: 3, dash: 'dash' },
        { x: [0, 0], y: [0, aRange[1]], z: [0, 0], color: 'green', width: 4, dash: 'solid' },
        { x: [0, 0], y: [aRange[0], 0], z: [0, 0], color: 'green', width: 3, dash: 'dash' },
        { x: [0, 0], y: [0, 0], z: [0, pRange[1]], color: 'blue', width: 4, dash: 'solid' },
        { x: [0, 0], y: [0, 0], z: [pRange[0], 0], color: 'blue', width: 3, dash: 'dash' }
    ];
    
    axisLines.forEach(axis => {
        initialData.push({
            x: axis.x, y: axis.y, z: axis.z,
            type: 'scatter3d',
            mode: 'lines',
            line: { color: axis.color, width: axis.width, dash: axis.dash },
            opacity: 0.3,
            showlegend: false,
            hoverinfo: 'skip'
        });
    });
    
    // 图例专用traces（独立于实际绘图）
    const legendTraces = [
        {
            x: [0, 1], y: [0, 0], z: [0, 0],
            type: 'scatter3d',
            mode: 'lines',
            line: { color: '#1f77b4', width: 8 },
            name: '蓝色成功路径',
            legendgroup: 'success',
            showlegend: true,
            visible: 'legendonly',
            hoverinfo: 'skip',
            legendrank: 60
        },
        {
            x: [0, 1], y: [0, 0], z: [0, 0],
            type: 'scatter3d',
            mode: 'lines',
            line: { color: '#d62728', width: 8 },
            name: '红色失败路径',
            legendgroup: 'failure',
            showlegend: true,
            visible: 'legendonly',
            hoverinfo: 'skip',
            legendrank: 61
        },
        {
            x: [0], y: [0], z: [0],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: '#08519c', size: 10, symbol: 'circle', line: { color: 'white', width: 1.6 } },
            name: '起点',
            legendgroup: 'start',
            showlegend: true,
            visible: 'legendonly',
            hoverinfo: 'skip',
            legendrank: 70
        },
        {
            x: [0], y: [0], z: [0],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: '#238b45', size: 11, symbol: 'diamond', line: { color: 'white', width: 1.6 } },
            name: '成功终点',
            legendgroup: 'success_end',
            showlegend: true,
            visible: 'legendonly',
            hoverinfo: 'skip',
            legendrank: 71
        },
        {
            x: [0], y: [0], z: [0],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: '#a50f15', size: 11, symbol: 'x', line: { color: 'white', width: 1.6 } },
            name: '失败终点',
            legendgroup: 'failure_end',
            showlegend: true,
            visible: 'legendonly',
            hoverinfo: 'skip',
            legendrank: 72
        },
        {
            x: [0], y: [0], z: [0],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: 'gold', size: 12, symbol: 'diamond', line: { color: '#f97316', width: 1.8 } },
            name: '目标原点',
            legendgroup: 'target_origin',
            showlegend: true,
            visible: 'legendonly',
            hoverinfo: 'skip',
            legendrank: 73
        }
    ];
    
    initialData.push(...legendTraces);
    
    // 创建动画frames
    console.log(`生成 ${maxTurns} 个动画帧...`);
    const frames = [];
    
    for (let turn = 1; turn <= maxTurns; turn++) {
        const frameData = [];
        
        // 成功路径
        successTrajs.forEach(traj => {
            const points = traj.points;
            const maxIndex = Math.min(turn, points.length - 1);
            const currentPoints = points.slice(0, maxIndex + 1);
            
            let lineX = [], lineY = [], lineZ = [], progressSteps = [];
            if (currentPoints.length >= 2) {
                const smoothPoints = smoothTrajectory(currentPoints, Math.min(100, currentPoints.length * 10));
                lineX = smoothPoints.map(p => p[0]);
                lineY = smoothPoints.map(p => p[1]);
                lineZ = smoothPoints.map(p => p[2]);
                
                for (let i = 0; i < smoothPoints.length; i++) {
                    progressSteps.push(1 + (currentPoints.length - 1) * i / (smoothPoints.length - 1));
                }
            }
            
            frameData.push({
                x: lineX, y: lineY, z: lineZ,
                type: 'scatter3d',
                mode: 'lines',
                line: { color: '#1f77b4', width: 3 },
                opacity: 0.6,
                legendgroup: 'success',
                showlegend: false,
                customdata: progressSteps,
                hovertemplate: `<b>${traj.script_id}</b> (成功)<br>第 %{customdata:.1f} 轮<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
            });
            
            const markerX = currentPoints.map(p => p[0]);
            const markerY = currentPoints.map(p => p[1]);
            const markerZ = currentPoints.map(p => p[2]);
            const markerText = currentPoints.map((_, i) => `${i + 1}`);
            
            frameData.push({
                x: markerX, y: markerY, z: markerZ,
                type: 'scatter3d',
                mode: 'markers',
                marker: { color: '#1f77b4', size: 2.0, line: { color: 'white', width: 0.3 } },
                opacity: 0.4,
                legendgroup: 'success',
                showlegend: false,
                text: markerText,
                hovertemplate: `<b>${traj.script_id} - 轮次 %{text}</b><br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
            });
        });
        
        // 失败路径
        failureTrajs.forEach(traj => {
            const points = traj.points;
            const maxIndex = Math.min(turn, points.length - 1);
            const currentPoints = points.slice(0, maxIndex + 1);
            
            let lineX = [], lineY = [], lineZ = [], progressSteps = [];
            if (currentPoints.length >= 2) {
                const smoothPoints = smoothTrajectory(currentPoints, Math.min(100, currentPoints.length * 10));
                lineX = smoothPoints.map(p => p[0]);
                lineY = smoothPoints.map(p => p[1]);
                lineZ = smoothPoints.map(p => p[2]);
                
                for (let i = 0; i < smoothPoints.length; i++) {
                    progressSteps.push(1 + (currentPoints.length - 1) * i / (smoothPoints.length - 1));
                }
            }
            
            frameData.push({
                x: lineX, y: lineY, z: lineZ,
                type: 'scatter3d',
                mode: 'lines',
                line: { color: '#d62728', width: 3 },
                opacity: 0.6,
                legendgroup: 'failure',
                showlegend: false,
                customdata: progressSteps,
                hovertemplate: `<b>${traj.script_id}</b> (失败)<br>第 %{customdata:.1f} 轮<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
            });
            
            const markerX = currentPoints.map(p => p[0]);
            const markerY = currentPoints.map(p => p[1]);
            const markerZ = currentPoints.map(p => p[2]);
            const markerText = currentPoints.map((_, i) => `${i + 1}`);
            
            frameData.push({
                x: markerX, y: markerY, z: markerZ,
                type: 'scatter3d',
                mode: 'markers',
                marker: { color: '#d62728', size: 1.5, line: { color: 'white', width: 0.3 } },
                opacity: 0.4,
                legendgroup: 'failure',
                showlegend: false,
                text: markerText,
                hovertemplate: `<b>${traj.script_id} - 轮次 %{text}</b><br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
            });
        });
        
        // 起点（恒定）
        orderedTrajs.forEach(traj => {
            const p0 = traj.points[0];
            frameData.push({
                x: [p0[0]], y: [p0[1]], z: [p0[2]],
                type: 'scatter3d',
                mode: 'markers',
                marker: { color: '#08519c', size: 2.5, symbol: 'circle', line: { color: 'white', width: 0.5 } },
                legendgroup: 'start',
                showlegend: false,
                hovertemplate: `<b>${traj.script_id} 起点</b><br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
            });
        });
        
        // 成功终点（达到终点后显示）
        successTrajs.forEach(traj => {
            const points = traj.points;
            let endX, endY, endZ;
            if (turn >= points.length - 1) {
                const pEnd = points[points.length - 1];
                endX = [pEnd[0]];
                endY = [pEnd[1]];
                endZ = [pEnd[2]];
            } else {
                endX = endY = endZ = [NaN];
            }
            frameData.push({
                x: endX, y: endY, z: endZ,
                type: 'scatter3d',
                mode: 'markers',
                marker: { color: '#238b45', size: 2.8, symbol: 'diamond', line: { color: 'white', width: 0.5 } },
                legendgroup: 'success_end',
                showlegend: false,
                hovertemplate: `<b>${traj.script_id} 终点</b> (成功)<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
            });
        });
        
        // 失败终点
        failureTrajs.forEach(traj => {
            const points = traj.points;
            let endX, endY, endZ;
            if (turn >= points.length - 1) {
                const pEnd = points[points.length - 1];
                endX = [pEnd[0]];
                endY = [pEnd[1]];
                endZ = [pEnd[2]];
            } else {
                endX = endY = endZ = [NaN];
            }
            frameData.push({
                x: endX, y: endY, z: endZ,
                type: 'scatter3d',
                mode: 'markers',
                marker: { color: '#a50f15', size: 3.0, symbol: 'x', line: { color: 'white', width: 0.5 } },
                legendgroup: 'failure_end',
                showlegend: false,
                hovertemplate: `<b>${traj.script_id} 终点</b> (失败)<br>C: %{x:.1f}<br>A: %{y:.1f}<br>P: %{z:.1f}<extra></extra>`
            });
        });
        
        // 原点
        frameData.push({
            x: [0], y: [0], z: [0],
            type: 'scatter3d',
            mode: 'markers',
            marker: { color: 'gold', size: 6, symbol: 'diamond', line: { color: 'orange', width: 1 } },
            legendgroup: 'target_origin',
            showlegend: false,
            hovertemplate: '<b>目标原点</b><br>C: 0<br>A: 0<br>P: 0<extra></extra>'
        });
        
        // 坐标轴
        axisLines.forEach(axis => {
            frameData.push({
                x: axis.x, y: axis.y, z: axis.z,
                type: 'scatter3d',
                mode: 'lines',
                line: { color: axis.color, width: axis.width, dash: axis.dash },
                opacity: 0.3,
                showlegend: false,
                hoverinfo: 'skip'
            });
        });
        
        frames.push({
            name: `turn_${turn}`,
            data: frameData,
            layout: { title: `第 ${turn} 轮` }
        });
    }
    
    // 布局配置
    const layout = {
        title: ' ',
        autosize: true,
        height: 720,
        margin: { t: 70, b: 70, l: 56, r: 220 },
        dragmode: 'turntable',
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        hovermode: 'closest',
        hoverlabel: {
            bgcolor: 'rgba(15,23,42,0.9)',
            font: { size: 12, color: '#f8fafc' }
        },
        legend: {
            title: { text: '<b>图例</b>' },
            x: 1.02,
            xanchor: 'left',
            y: 0.98,
            yanchor: 'top',
            bgcolor: 'rgba(255,255,255,0.88)',
            bordercolor: '#d4d8e2',
            borderwidth: 1,
            font: { size: 12, color: '#1f2937' },
            groupclick: 'togglegroup'
        },
        legend_tracegroupgap: 12,
        scene: {
            xaxis: {
                title: {
                    text: '<b>认知轴 Cognitive (C)</b><br>← 赤字 | 充足 →',
                    font: { size: 13, color: '#0f172a' }
                },
                range: cRange,
                backgroundcolor: '#ffffff',
                gridcolor: '#e2e8f0',
                showbackground: true,
                zerolinecolor: 'darkred',
                zerolinewidth: 3,
                autorange: 'reversed',
                tickfont: { size: 11, color: '#334155' }
            },
            yaxis: {
                title: {
                    text: '<b>情感轴 Affective (A)</b><br>← 赤字 | 充足 →',
                    font: { size: 13, color: '#0f172a' }
                },
                range: aRange,
                backgroundcolor: '#ffffff',
                gridcolor: '#e2e8f0',
                showbackground: true,
                zerolinecolor: 'darkgreen',
                zerolinewidth: 3,
                autorange: 'reversed',
                tickfont: { size: 11, color: '#334155' }
            },
            zaxis: {
                title: {
                    text: '<b>动机轴 Proactive (P)</b><br>← 赤字 | 充足 →',
                    font: { size: 13, color: '#0f172a' }
                },
                range: pRange,
                backgroundcolor: '#ffffff',
                gridcolor: '#e2e8f0',
                showbackground: true,
                zerolinecolor: 'darkblue',
                zerolinewidth: 3,
                autorange: 'reversed',
                tickfont: { size: 11, color: '#334155' }
            },
            camera: {
                eye: { x: -1.5, y: -1.5, z: 1.2 },
                center: { x: 0, y: 0, z: 0 }
            },
            aspectmode: 'cube'
        },
        font: {
            family: "PingFang SC, 'Microsoft YaHei', sans-serif",
            size: 13,
            color: '#1f2937'
        },
        updatemenus: [{
            type: 'buttons',
            showactive: false,
            buttons: [
                {
                    label: '▶️ 播放',
                    method: 'animate',
                    args: [null, {
                        frame: { duration: 300, redraw: true },
                        fromcurrent: true,
                        mode: 'immediate',
                        transition: { duration: 0 }
                    }]
                },
                {
                    label: '⏸️ 暂停',
                    method: 'animate',
                    args: [[null], {
                        frame: { duration: 0, redraw: false },
                        mode: 'immediate',
                        transition: { duration: 0 }
                    }]
                }
            ],
            direction: 'left',
            pad: { r: 10, t: 0 },
            x: 0.02,
            xanchor: 'left',
            y: 0.94,
            yanchor: 'bottom'
        }],
        sliders: [{
            active: 0,
            yanchor: 'bottom',
            y: 0.96,
            xanchor: 'left',
            x: 0.23,
            currentvalue: {
                prefix: '当前轮次: ',
                visible: true,
                xanchor: 'left',
                font: { size: 13, color: '#1f2937' }
            },
            pad: { b: 4, t: 4 },
            len: 0.72,
            steps: frames.map((frame, i) => ({
                args: [[frame.name], {
                    frame: { duration: 0, redraw: true },
                    mode: 'immediate',
                    transition: { duration: 0 }
                }],
                method: 'animate',
                label: `${i + 1}`,
                value: `${i + 1}`
            }))
        }]
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['toImage']
    };
    
    // 绘制
    Plotly.newPlot('plotly-container', initialData, layout, config).then(() => {
        Plotly.addFrames('plotly-container', frames);
        
        // 添加相机限制
        const plotDiv = document.getElementById('plotly-container');
        plotDiv.on('plotly_relayout', function(eventdata) {
            if (eventdata['scene.camera']) {
                const camera = eventdata['scene.camera'];
                if (camera.eye) {
                    const z = camera.eye.z;
                    const minZ = 0.3;
                    const maxZ = 2.0;
                    if (z < minZ || z > maxZ) {
                        camera.eye.z = Math.max(minZ, Math.min(maxZ, z));
                        Plotly.relayout(plotDiv, { 'scene.camera.eye': camera.eye });
                    }
                }
            }
        });
        
        console.log('✅ 可视化渲染完成');
    });
}

// 加载数据并渲染
async function loadAndVisualize(modelName) {
    try {
        console.log(`加载模型数据: ${modelName}`);
        
        const response = await fetch('data/trajectories.json');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // 更新UI
        document.getElementById('case-count').textContent = `${data.metadata.total_cases} 条真实案例`;
        
        // 创建可视化
        createAnimated3D(data.trajectories, data.metadata);
        
    } catch (error) {
        console.error('加载数据失败:', error);
        document.getElementById('plotly-container').innerHTML = 
            '<div class="loading" style="color: #dc2626;">❌ 数据加载失败，请检查网络连接或数据文件路径</div>';
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    const modelSelect = document.getElementById('model-select');
    
    // 加载默认模型
    loadAndVisualize(modelSelect.value);
    
    // 监听模型切换
    modelSelect.addEventListener('change', (e) => {
        loadAndVisualize(e.target.value);
    });
});

