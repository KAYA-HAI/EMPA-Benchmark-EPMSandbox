# Benchmark - EPJ共情评估系统

基于科学的三维向量（C-A-P）的AI共情能力评估系统

---

## 🚀 快速开始

### 单个剧本运行

#### 步骤1: 配置API密钥

编辑 `config/api_config.py`:
```python
OPENROUTER_API_KEY = "sk-or-v1-你的实际key"
```

#### 步骤2: （可选）修改模型和剧本

编辑 `run_real_conversation.py`:
```python
SCRIPT_ID = "001"      # 剧本ID: 001-100
ACTOR_MODEL = "openai/gpt-4o-mini"  # 可改为其他模型
```

#### 步骤3: 运行对话

```bash
python3 run_real_conversation.py
```

结果保存在 `results/epj_conversation_result.json`

---

### 批量运行所有剧本 🆕

#### 运行所有100个剧本

```bash
python3 run_all_scripts.py
```

**特点：**
- 自动运行所有剧本（001-100）
- 支持断点续传
- 每个剧本独立保存结果
- 生成汇总报告

#### 分析批量结果

```bash
python3 analyze_batch_results.py
```

详见: [BATCH_RUN_GUIDE.md](BATCH_RUN_GUIDE.md)

---

## 📁 项目结构

```
Benchmark-test/
├── config/                    # ⚙️ 配置文件
│   ├── api_config.py          # API密钥配置（在这里填key）
│   └── README.md              # 配置说明
│
├── Benchmark/                 # 核心代码
│   ├── agents/                # Agent实现
│   ├── epj/                   # EPJ三维向量系统
│   ├── orchestrator/          # 对话编排器
│   ├── prompts/               # Prompt模板
│   ├── topics/data/           # 剧本数据
│   └── llms/                  # LLM API
│
├── run_real_conversation.py   # 主运行脚本（在这里改模型和参数）
├── docs/                      # 文档
├── tests/                     # 测试文件
└── results/                   # 运行结果
```

详细结构说明: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## ⚙️ 配置说明

### 在哪里配置API密钥？

**位置**: `config/api_config.py`

打开文件，修改：
```python
OPENROUTER_API_KEY = "sk-or-v1-你的key"
```

### 在哪里更改模型？

**位置**: `run_real_conversation.py` (第46-50行)

可选模型：
- `openai/gpt-4o-mini` (推荐，便宜)
- `anthropic/claude-3-haiku` (便宜)
- `google/gemini-flash-1.5` (便宜)

### 在哪里修改运行参数？

**位置**: `run_real_conversation.py` (第41-43行)

```python
SCRIPT_ID = "001"      # 使用哪个剧本
MAX_TURNS = 15         # 最大对话轮数
K = 3                  # 每K轮评估一次EPJ
```

---

## 📖 核心概念

### EPJ系统（三维共情向量）

- **C轴**: 认知共情（被理解）
- **A轴**: 情感共情（被共鸣）
- **P轴**: 动机共情（被赋能）

### 三层架构

1. **Judger（传感器-LLM）**: 填写心理量表
2. **Orchestrator（计算器-代码）**: 计算向量和生成状态数据包
3. **Director（决策者-LLM）**: 基于状态数据包做决策

详见: `docs/epj/EPJ.md`

---

## 🎭 剧本数据集

**当前可用: 100个剧本** (script_001 - script_100)

### 示例剧本

- **script_001** (林晚): 暧昧对象不正面回应的愤怒
- **script_002** (林溪): 分享关于亲吻的梦境  
- **script_054** (刘静): 被挑剔甲方点名表扬的喜悦
- **script_100** (赵思琪): 遭遇职场"软攻击"的憋屈

### 数据文件位置

- **角色设定**: `Benchmark/topics/data/character_setting/script_XXX.md`
- **剧情数据**: `Benchmark/topics/data/scenarios/character_stories.json`

---

## 📚 完整文档

- **EPJ系统**: `docs/epj/EPJ.md`
- **配置指南**: `config/README.md`
- **项目结构**: `PROJECT_STRUCTURE.md`
- **运行设置**: `docs/SETUP_REAL_CONVERSATION.md`

---

## 🧪 测试

```bash
# EPJ系统测试（Mock数据）
python3 tests/integration/test_epj_system.py

# 真实剧本测试（Mock数据）
python3 tests/integration/test_epj_with_real_script.py
```

---

## ✅ 数据集状态

**剧本数量**: 100个完整剧本 ✅  
**数据格式**: 已验证并可正确读取 ✅  
**批量运行**: 支持 ✅

### 最近更新 (2025-10-28)

- ✅ 更新 ConfigLoader 支持新数据格式
- ✅ 验证所有100个剧本可正常加载
- ✅ 添加批量运行功能
- ✅ 添加结果分析工具

详见: 
- 单次运行结果: `results/epj_conversation_result.json`
- 批量运行结果: `results/all_scripts/`
- 数据验证报告: `DATA_VALIDATION_REPORT.md`

---

**版本**: EPJ v1.1  
**更新日期**: 2025-10-28
