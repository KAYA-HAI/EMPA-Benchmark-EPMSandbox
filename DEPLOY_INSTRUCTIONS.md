# 🚀 GitHub Pages 部署指南

## ✅ 已完成
- [x] Git 仓库初始化
- [x] 可视化文件已提交

## 📝 接下来的步骤

### 1️⃣ 在 GitHub 创建仓库

访问：https://github.com/new

填写：
- Repository name: `EPM-Visualization` (或其他名字)
- Description: `EPM共情修复轨迹3D可视化`
- 选择 **Public**
- ❌ 不要勾选 "Add a README file"

点击 **Create repository**

### 2️⃣ 推送代码

在终端运行以下命令（替换成你的GitHub仓库地址）：

```bash
cd /Users/shiya/Desktop/Benchmark-test

# 添加远程仓库（替换成你的仓库地址）
git remote add origin https://github.com/你的用户名/EPM-Visualization.git

# 推送代码
git branch -M main
git push -u origin main
```

### 3️⃣ 配置 GitHub Pages

1. 进入你的 GitHub 仓库页面
2. 点击 **Settings** (设置)
3. 左侧菜单找到 **Pages**
4. 在 "Build and deployment" 部分：
   - **Source**: 选择 `Deploy from a branch`
   - **Branch**: 选择 `main`
   - **Folder**: 选择 `/visualization` ⚠️ 重要！
5. 点击 **Save**

### 4️⃣ 等待部署完成

- GitHub 会自动构建和部署（约1-3分钟）
- 刷新 Pages 设置页面，会看到绿色提示：
  ```
  Your site is live at https://你的用户名.github.io/EPM-Visualization/
  ```

### 5️⃣ 访问你的可视化

打开链接：`https://你的用户名.github.io/EPM-Visualization/`

🎉 完成！全世界都能访问你的可视化了！

---

## 🔄 更新数据

当你有新的模型数据时：

```bash
# 1. 导出新数据
python3 scripts/export_trajectory_data.py

# 2. 提交更新
git add visualization/data/
git commit -m "Update trajectory data"
git push

# 3. 等待1-2分钟，GitHub Pages 自动更新
```

---

## ❓ 常见问题

### Q: 显示 404 错误
A: 检查 Pages 设置中 Folder 是否选择了 `/visualization`

### Q: 数据加载失败
A: 确保 `visualization/data/trajectories.json` 已提交到仓库

### Q: 想用自定义域名
A: 在 Pages 设置中添加 Custom domain，并配置 DNS

---

## 📧 需要帮助？

如果遇到问题，可以：
1. 检查 GitHub Actions 页面的构建日志
2. 查看浏览器控制台的错误信息
3. 确认所有文件都已正确提交

---

**最后更新**: 2025-11-12

