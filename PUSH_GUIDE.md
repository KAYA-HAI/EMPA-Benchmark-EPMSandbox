# 🚀 推送代码到 GitHub 指南

## 方法1：使用 Personal Access Token（推荐）

### 步骤1：生成 Token

1. 访问：https://github.com/settings/tokens
2. 点击 **Generate new token (classic)**
3. 设置：
   - Note: `EPM-Visualization-Deploy`
   - Expiration: 选择有效期（建议 90 days）
   - 勾选权限：✅ **repo** (全选)
4. 点击 **Generate token**
5. ⚠️ **立即复制 token**（只显示一次！）

### 步骤2：推送代码

在终端运行：

```bash
cd /Users/shiya/Desktop/Benchmark-test
git push -u origin main
```

当提示输入：
- **Username**: 输入你的 GitHub 用户名 `Shiyaaaaaaaa`
- **Password**: 粘贴刚才复制的 Personal Access Token

---

## 方法2：使用 SSH（一劳永逸）

### 步骤1：生成 SSH 密钥

```bash
# 生成密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 按 Enter 使用默认路径
# 可以设置密码或直接 Enter 跳过

# 启动 ssh-agent
eval "$(ssh-agent -s)"

# 添加密钥
ssh-add ~/.ssh/id_ed25519
```

### 步骤2：添加到 GitHub

```bash
# 复制公钥
cat ~/.ssh/id_ed25519.pub
```

1. 访问：https://github.com/settings/keys
2. 点击 **New SSH key**
3. Title: `Mac Desktop`
4. 粘贴刚才复制的公钥
5. 点击 **Add SSH key**

### 步骤3：更改远程仓库地址

```bash
cd /Users/shiya/Desktop/Benchmark-test
git remote set-url origin git@github.com:Shiyaaaaaaaa/EPM-Visualization.git
git push -u origin main
```

---

## 方法3：使用 GitHub Desktop（最简单）

1. 下载：https://desktop.github.com/
2. 安装并登录 GitHub 账号
3. File → Add Local Repository
4. 选择 `/Users/shiya/Desktop/Benchmark-test`
5. 点击 **Publish repository**

---

## ✅ 推送成功后

返回 GitHub Pages 设置页面：
https://github.com/Shiyaaaaaaaa/EPM-Visualization/settings/pages

刷新页面，Folder 下拉菜单会出现：
- `/ (root)`
- `/visualization` ← **选择这个！**

保存后等待 1-3 分钟，访问：
https://shiyaaaaaaaa.github.io/EPM-Visualization/

---

## ❓ 遇到问题？

### 推送失败：Authentication failed
- 确认 Token 权限包含 `repo`
- Token 可能过期，重新生成

### 推送失败：Permission denied
- 检查是否是仓库的 Owner
- SSH 密钥是否正确添加

### Folder 仍然只有 / (root)
- 确认代码已成功推送（访问 https://github.com/Shiyaaaaaaaa/EPM-Visualization 查看文件）
- 刷新 Pages 设置页面
- 等待几秒钟让 GitHub 检测文件结构

