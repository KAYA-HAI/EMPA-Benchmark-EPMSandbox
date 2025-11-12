# 快速开始指南

## 🎯 3步运行EPJ对话

### 1️⃣ 配置API密钥

打开 `config/api_config.py`，修改：

```python
OPENROUTER_API_KEY = "sk-or-v1-你的实际key"
```

> 获取免费key: https://openrouter.ai/keys

---

### 2️⃣ （可选）修改模型

打开 `run_real_conversation.py`，找到第46-50行：

```python
ACTOR_MODEL = "openai/gpt-4o-mini"  # 可改为其他模型
DIRECTOR_MODEL = "openai/gpt-4o-mini"
JUDGER_MODEL = "openai/gpt-4o-mini"
TEST_MODEL_NAME = "openai/gpt-4o-mini"
```

**可用模型**:
- `openai/gpt-4o-mini` ✅ 推荐（便宜且效果好）
- `anthropic/claude-3-haiku` （便宜）
- `google/gemini-flash-1.5` （便宜）

---

### 3️⃣ 运行对话

```bash
python3 run_real_conversation.py
```

运行结果保存在 `results/epj_conversation_result.json`

---

## 📊 你会看到什么？

### 对话过程

```
🎭 EPJ Benchmark 开始

EPJ 初始化 (T=0)
  ✅ P_0 = (-8, -14, -12)  ← Judger分析剧本

第 1/15 轮
  💬 刘静: 我们那个最挑剔的甲方，今天居然点名表扬我了
  🤖 AI助手: [共情回复]
  🎬 Director: 释放"阶段1：引发回忆"

第 3 轮 - EPJ评估
  v_t = (+1, +3, +3)
  P_t = (-7, -11, -9)
  显示进度 = 20.6%
  决策: CONTINUE

...（继续对话）

对话结束
  最终位置: P_t
  总轮数: 15
  结果保存: results/epj_conversation_result.json
```

---

## 🔧 常见问题

### Q: API key在哪里填？

**A**: `config/api_config.py`

```python
OPENROUTER_API_KEY = "sk-or-v1-..."
```

---

### Q: 如何更改使用的模型？

**A**: 编辑 `run_real_conversation.py` (第46-50行)

```python
ACTOR_MODEL = "anthropic/claude-3-haiku"  # 改为你想用的模型
```

---

### Q: 如何更改剧本？

**A**: 编辑 `run_real_conversation.py` (第41行)

```python
SCRIPT_ID = "002"  # 使用其他剧本（需先创建）
```

---

### Q: 如何查看运行结果？

**A**: 打开 `results/epj_conversation_result.json`

包含：
- 完整对话历史
- EPJ向量轨迹
- Director的剧情控制记录

---

## 📖 更多文档

- **完整项目结构**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **EPJ系统设计**: [docs/epj/EPJ.md](docs/epj/EPJ.md)
- **配置详细说明**: [config/README.md](config/README.md)

---

**版本**: 1.0  
**更新**: 2025-10-27

