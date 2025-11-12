# 快速参考

---

## 🚀 运行命令

### 单个剧本

```bash
# 运行单个剧本（需先在文件中配置SCRIPT_ID）
python3 run_real_conversation.py
```

### 批量运行

```bash
# 运行所有100个剧本（推荐）
python3 run_all_scripts.py

# 自定义批量运行（可选择范围）
python3 run_batch_conversations.py
```

### 结果分析

```bash
# 分析批量运行结果
python3 analyze_batch_results.py

# 查看CSV文件（可用Excel打开）
open results/all_scripts/analysis_summary.csv
```

---

## ⚙️ 配置位置

| 配置项 | 文件 | 位置 |
|--------|------|------|
| API密钥 | `config/api_config.py` | 第1行 |
| 剧本ID（单次） | `run_real_conversation.py` | 第41行 |
| 模型选择（单次） | `run_real_conversation.py` | 第46-50行 |
| 批量运行参数 | `run_all_scripts.py` | 第19-27行 |

---

## 📊 剧本数据集

**总数**: 100个剧本  
**编号**: script_001 - script_100  
**格式**: 已验证 ✅

### 数据文件

- 角色设定: `Benchmark/topics/data/character_setting/script_XXX.md`
- 剧情数据: `Benchmark/topics/data/scenarios/character_stories.json`

---

## 📂 结果文件

### 单次运行

```
results/epj_conversation_result.json
```

### 批量运行

```
results/all_scripts/
├── result_001.json        # 每个剧本的完整结果
├── result_002.json
├── ...
├── final_summary.json     # 汇总报告
└── analysis_summary.csv   # CSV格式数据
```

---

## 🔥 常用场景

### 场景1: 测试单个剧本

```bash
# 1. 修改剧本ID
vim run_real_conversation.py
# SCRIPT_ID = "005"

# 2. 运行
python3 run_real_conversation.py

# 3. 查看结果
cat results/epj_conversation_result.json
```

### 场景2: 批量测试所有剧本

```bash
# 1. 确认配置
cat config/api_config.py  # 检查API key
cat run_all_scripts.py    # 检查参数

# 2. 开始批量运行
python3 run_all_scripts.py

# 3. 等待完成（约3-8小时）
# 可以Ctrl+C中断，下次会继续

# 4. 分析结果
python3 analyze_batch_results.py
```

### 场景3: 对比不同模型

```bash
# 测试模型A
vim run_all_scripts.py
# 设置: TEST_MODEL = "openai/gpt-4o-mini"
python3 run_all_scripts.py
mv results/all_scripts results/gpt4o_mini

# 测试模型B  
vim run_all_scripts.py
# 设置: TEST_MODEL = "anthropic/claude-3.5-sonnet"
python3 run_all_scripts.py
mv results/all_scripts results/claude35

# 对比分析
python3 analyze_batch_results.py --dir results/gpt4o_mini
python3 analyze_batch_results.py --dir results/claude35
```

---

## 🛠️ 调试命令

### 测试配置加载

```bash
# 测试config_loader
python3 Benchmark/topics/config_loader.py

# 列出所有可用剧本
python3 -c "from Benchmark.topics.config_loader import list_scenarios; print(list_scenarios())"
```

### 查看某个剧本的数据

```bash
# 查看角色设定
cat Benchmark/topics/data/character_setting/script_001.md

# 查看剧情（需要从JSON中提取）
python3 -c "
from Benchmark.topics.config_loader import load_scenario
scenario = load_scenario('001')
import json
print(json.dumps(scenario, ensure_ascii=False, indent=2))
"
```

### 检查运行进度

```bash
# 查看已完成的剧本数量
ls results/all_scripts/result_*.json | wc -l

# 查看最新完成的5个剧本
ls -lt results/all_scripts/result_*.json | head -5

# 实时监控（每5秒刷新）
watch -n 5 "ls -1 results/all_scripts/result_*.json | wc -l"
```

---

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| `README.md` | 项目总览 |
| `QUICK_START.md` | 快速入门 |
| `BATCH_RUN_GUIDE.md` | 批量运行详细指南 |
| `DATA_VALIDATION_REPORT.md` | 数据验证报告 |
| `PROJECT_STRUCTURE.md` | 项目结构说明 |
| `docs/epj/EPJ.md` | EPJ系统设计文档 |

---

## 💡 提示

- 🔑 运行前确保 API key 已配置
- 💰 注意 API 费用（100个剧本约$0.5-1）
- ⏱️ 预留足够时间（3-8小时）
- 💾 定期备份结果
- 🔄 利用断点续传功能

---

**版本**: v1.1  
**更新**: 2025-10-28

