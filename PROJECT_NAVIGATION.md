# 🗺️ 项目导航指南

本文档帮助您快速找到项目中的各类文件。

## 📂 项目结构概览

```
Benchmark-test/
├── 📄 README.md                          # 项目主文档
├── 📄 QUICK_START.md                     # 快速开始指南
├── 📄 PROJECT_NAVIGATION.md              # 本文档（项目导航）
│
├── 🚀 run_benchmark_custom_model.py      # [核心] 自定义模型评测脚本
├── 🚀 run_real_conversation.py           # [核心] 实际对话运行脚本
│
├── 📁 Benchmark/                         # 核心系统代码
│   ├── agents/                          # 智能体（Actor, Director, Judger, TestModel）
│   ├── epj/                             # EPJ评估系统
│   ├── llms/                            # LLM API封装
│   ├── orchestrator/                    # 对话编排器
│   ├── prompts/                         # 提示词模板
│   └── topics/                          # 话题数据（281个剧本）
│
├── 📁 config/                            # 配置文件
│   ├── api_config.py                    # API密钥配置
│   └── README.md                        # 配置说明
│
├── 📁 docs/                              # 📚 所有文档
│   ├── EPJ.md                           # EPJ系统说明
│   ├── EPM.md                           # EPM系统说明
│   ├── PROJECT_STRUCTURE.md             # 项目结构详解
│   ├── README_CUSTOM_MODEL.md           # 自定义模型评测指南
│   ├── sample.md                        # 采样逻辑说明
│   ├── EPM_STRICTER_CRITERIA.md         # EPM严格标准
│   ├── JUDGER_SCORING_STRICTNESS_FIX.md # Judger评分修复
│   └── ... (更多技术文档)
│
├── 📁 scripts/                           # 🔧 工具和分析脚本
│   ├── README.md                        # 脚本说明文档
│   ├── analyze_correlations.py          # 相关性分析
│   ├── analyze_epm_distribution.py      # EPM分布分析
│   ├── batch_evaluate_iedr.py           # 批量IEDR评估
│   ├── sample_benchmark_cases.py        # 测试案例采样
│   └── ... (更多工具脚本)
│
├── 📁 results/                           # 📊 评测结果
│   ├── benchmark_runs/                  # 模型评测结果
│   │   └── [模型名]_[日期]_[序号]/      # 单次运行结果
│   ├── iedr_batch_results.json          # IEDR批量评估结果
│   ├── sampled_benchmark_30_ids.txt     # 采样的30个测试案例
│   └── iedr_analysis/                   # IEDR分析报告
│
└── 📁 tests/                             # 🧪 单元测试
    ├── integration/                     # 集成测试
    └── test_*.py                        # 各类测试脚本
```

---

## 🎯 快速查找指南

### 我想... 那么应该看...

#### 📖 了解项目
- **项目概述** → `README.md`
- **快速开始** → `QUICK_START.md`
- **EPJ系统** → `docs/EPJ.md`
- **EPM系统** → `docs/EPM.md`
- **项目结构详解** → `docs/PROJECT_STRUCTURE.md`

#### 🚀 运行评测
- **评测自定义模型** → `run_benchmark_custom_model.py` + `docs/README_CUSTOM_MODEL.md`
- **运行单次对话** → `run_real_conversation.py`
- **批量运行评测** → `scripts/run_batch_conversations.py`

#### 🔧 使用工具
- **抽取测试案例** → `scripts/sample_benchmark_cases.py`
- **批量评估IEDR** → `scripts/batch_evaluate_iedr.py`
- **分析采样相关性** → `scripts/analyze_correlations.py`
- **分析EPM分布** → `scripts/analyze_epm_distribution.py`
- **工具脚本说明** → `scripts/README.md`

#### ⚙️ 配置系统
- **API密钥配置** → `config/api_config.py`
- **修改提示词** → `Benchmark/prompts/`
- **调整评分标准** → `Benchmark/epj/judger_prompts.py`
- **修改EPM参数** → `Benchmark/epj/vector_calculator.py`

#### 📊 查看结果
- **评测结果** → `results/benchmark_runs/`
- **IEDR数据** → `results/iedr_batch_results.json`
- **采样案例** → `results/sampled_benchmark_30_ids.txt`

#### 🔬 了解技术细节
- **EPM严格标准** → `docs/EPM_STRICTER_CRITERIA.md`
- **Judger评分标准** → `docs/JUDGER_SCORING_STRICTNESS_FIX.md`
- **终止逻辑** → `docs/TERMINATION_LOGIC_FIX.md`
- **批量运行指南** → `docs/BATCH_RUN_GUIDE.md`

#### 💻 开发和调试
- **系统核心代码** → `Benchmark/`
- **单元测试** → `tests/`
- **集成测试** → `tests/integration/`

---

## 📋 常见任务速查

### 任务1：评测一个自定义模型
```bash
# 1. 配置API密钥
vim config/api_config.py

# 2. 修改评测脚本中的模型配置
vim run_benchmark_custom_model.py
# 修改 CUSTOM_API_CONFIG 部分

# 3. 运行评测
python3 run_benchmark_custom_model.py
```

### 任务2：重新采样测试案例
```bash
# 1. 查看采样逻辑说明
cat docs/sample.md

# 2. 运行采样脚本
python3 scripts/sample_benchmark_cases.py

# 3. 查看采样结果
cat results/sampled_benchmark_30_ids.txt
```

### 任务3：批量评估IEDR
```bash
# 运行批量IEDR评估
python3 scripts/batch_evaluate_iedr.py

# 查看结果
cat results/iedr_batch_results.json
```

### 任务4：分析评测结果
```bash
# 查看最近一次评测结果
ls -lt results/benchmark_runs/ | head -2

# 查看具体案例结果
cat results/benchmark_runs/[模型名]_[日期]/script_001_result.json
```

---

## 🆘 需要帮助？

- **快速开始**：`QUICK_START.md`
- **主文档**：`README.md`
- **脚本说明**：`scripts/README.md`
- **技术文档**：`docs/` 目录下的各类文档

---

**最后更新**: 2025-11-05

