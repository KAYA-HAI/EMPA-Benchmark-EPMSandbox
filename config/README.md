# API配置

## 配置API密钥

### 步骤1: 复制示例文件

```bash
cp api_config.py.example api_config.py
```

### 步骤2: 编辑 api_config.py

```python
OPENROUTER_API_KEY = "sk-or-v1-你的真实key"
```

### 步骤3: 获取API key

访问: https://openrouter.ai/keys  
注册并获取免费API key

---

## 文件说明

- `api_config.py.example` - 示例文件（可以提交到git）
- `api_config.py` - 实际配置（包含真实key，已在.gitignore中）

---

## ⚠️ 安全提示

`api_config.py` 包含你的真实API密钥，已被 `.gitignore` 忽略，不会被提交到git仓库。

---

**更多配置**（模型、参数等）请查看: 
- 项目根目录的 `QUICK_START.md`
- 项目根目录的 `README.md`
