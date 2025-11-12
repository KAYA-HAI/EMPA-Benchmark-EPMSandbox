# EPM 共情修复轨迹可视化 - 独立前端版本

## 📁 项目结构

```
visualization/
├── index.html              # 主页面
├── js/
│   └── visualization.js    # 可视化逻辑
├── data/
│   └── trajectories.json   # 轨迹数据（自动生成）
└── README.md              # 本文档
```

## 🚀 快速开始

### 1. 生成数据文件

首先运行数据导出脚本：

```bash
cd /Users/shiya/Desktop/Benchmark-test
python3 scripts/export_trajectory_data.py
```

这会生成 `visualization/data/trajectories.json` 文件。

### 2. 本地预览

使用任意HTTP服务器启动：

```bash
# 方法1: Python内置服务器
cd visualization
python3 -m http.server 8080

# 方法2: Node.js (需要先安装 http-server)
npx http-server visualization -p 8080

# 方法3: VS Code Live Server 插件
# 右键 index.html -> Open with Live Server
```

然后在浏览器访问：`http://localhost:8080`

### 3. 部署到GitHub Pages（推荐）

#### 步骤：

1. **创建GitHub仓库**（如果还没有）
   ```bash
   cd /Users/shiya/Desktop/Benchmark-test
   git init
   git add visualization/
   git commit -m "Add EPM visualization"
   git remote add origin https://github.com/你的用户名/仓库名.git
   git push -u origin main
   ```

2. **配置GitHub Pages**
   - 进入仓库 Settings → Pages
   - Source 选择 `main` 分支
   - 文件夹选择 `/visualization` 或 `/` (根目录)
   - 点击 Save

3. **访问链接**
   - 几分钟后，你的可视化将发布到：
   - `https://你的用户名.github.io/仓库名/`
   - 完全免费，全球可访问！

### 4. 其他部署选项

#### Vercel（推荐，更快）
```bash
# 安装Vercel CLI
npm i -g vercel

# 部署
cd visualization
vercel --prod
```

#### Netlify
- 拖拽 `visualization/` 文件夹到 [Netlify Drop](https://app.netlify.com/drop)
- 自动生成链接

## 📊 添加新模型数据

### 方法1：修改导出脚本

编辑 `scripts/export_trajectory_data.py`，添加新模型的数据路径：

```python
# 导出多个模型
models = [
    ("default_20251106_233640", "results/benchmark_runs/default_20251106_233640"),
    ("gpt4_20251107_120000", "results/benchmark_runs/gpt4_20251107_120000"),
    ("claude_20251107_130000", "results/benchmark_runs/claude_20251107_130000")
]

for model_name, results_dir in models:
    output_file = f"visualization/data/{model_name}.json"
    export_trajectories(results_dir, output_file)
```

### 方法2：更新前端配置

编辑 `visualization/index.html`，在模型选择器中添加：

```html
<select id="model-select">
    <option value="default_20251106_233640">Default Model</option>
    <option value="gpt4_20251107_120000">GPT-4 Model</option>
    <option value="claude_20251107_130000">Claude Model</option>
</select>
```

修改 `visualization/js/visualization.js` 的加载逻辑：

```javascript
async function loadAndVisualize(modelName) {
    const response = await fetch(`data/${modelName}.json`);
    // ... 其余代码
}
```

## 🎨 自定义样式

所有样式都在 `index.html` 的 `<style>` 标签中，可以直接修改：

- 颜色主题：修改 `background`, `color` 等属性
- 布局尺寸：调整 `.container`, `.card` 的 `padding`, `margin`
- 字体：修改 `font-family`

## 🔧 技术栈

- **Plotly.js**: 3D可视化库（CDN加载）
- **原生JavaScript**: 无需额外依赖
- **纯HTML/CSS**: 易于部署和维护

## 📝 数据格式

`data/trajectories.json` 结构：

```json
{
  "metadata": {
    "model_name": "模型名称",
    "total_cases": 30,
    "success_count": 23,
    "failure_count": 7,
    "max_turns": 46
  },
  "trajectories": [
    {
      "script_id": "script_001",
      "points": [[c1, a1, p1], [c2, a2, p2], ...],
      "status": "success",
      "total_turns": 15
    },
    ...
  ]
}
```

## 🐛 常见问题

### Q: 浏览器显示"数据加载失败"
A: 
1. 确认 `data/trajectories.json` 文件存在
2. 必须通过HTTP服务器访问（不能直接双击HTML文件）
3. 检查浏览器控制台的错误信息

### Q: 动画不流畅
A: 
- 减少 `numPoints` 参数（在 `smoothTrajectory` 函数中）
- 降低动画帧率（修改 `frame.duration`）

### Q: 如何修改坐标轴范围？
A: 
编辑 `js/visualization.js` 中的：
```javascript
const cRange = [-60, 25];
const aRange = [-60, 25];
const pRange = [-40, 20];
```

## 📧 联系方式

如有问题，请联系项目维护者。

---

**License**: MIT  
**Last Updated**: 2025-11-12

