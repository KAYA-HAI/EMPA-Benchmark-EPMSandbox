# Scripts 目录说明

本目录包含各种工具和分析脚本。

## 📊 分析脚本

### `analyze_correlations.py`
**功能**：分析采样维度之间的相关性
- 检查轴分布（C/A/P）、难度分布、情境分布之间的关联性
- 生成相关性分析报告

**运行**：
```bash
python3 scripts/analyze_correlations.py
```

### `analyze_epm_distribution.py`
**功能**：分析EPM参数分布
- 分析alpha、epsilon、v_star_0等EPM参数的分布特征
- 判断EPM参数是否需要作为独立采样维度

**运行**：
```bash
python3 scripts/analyze_epm_distribution.py
```

### `check_vstar_independence.py`
**功能**：检查v_star_0的独立性
- 验证v_star_0的主导方向是否与P_0主导轴一致
- 输出独立性分析结果

**运行**：
```bash
python3 scripts/check_vstar_independence.py
```

## 🔧 工具脚本

### `batch_evaluate_iedr.py`
**功能**：批量评估IEDR（初始共情赤字）
- 对所有剧本进行初始共情赤字评估
- 生成`results/iedr_batch_results.json`

**运行**：
```bash
python3 scripts/batch_evaluate_iedr.py
```

### `sample_benchmark_cases.py`
**功能**：三维分层抽样
- 基于C-A-P轴、难度、情境三个维度进行分层抽样
- 从281个剧本中科学地抽取30个测试案例
- 生成`results/sampled_benchmark_30_ids.txt`

**运行**：
```bash
python3 scripts/sample_benchmark_cases.py
```

### `analyze_iedr_distribution.py`
**功能**：分析IEDR分布
- 生成IEDR的统计分析和可视化
- 输出分布图表和分析报告

**运行**：
```bash
python3 scripts/analyze_iedr_distribution.py
```

### `generate_iedr_report.py`
**功能**：生成IEDR综合报告
- 汇总IEDR评估结果
- 生成详细的分析报告

**运行**：
```bash
python3 scripts/generate_iedr_report.py
```

## 🏃 批量运行脚本

### `run_batch_conversations.py`
**功能**：批量运行对话评测
- 并发执行多个对话测试
- 自动保存和汇总结果

**运行**：
```bash
python3 scripts/run_batch_conversations.py
```

### `run_all_scripts.py`
**功能**：一键运行所有脚本
- 按依赖顺序执行所有必要脚本
- 完整的数据处理流程

**运行**：
```bash
python3 scripts/run_all_scripts.py
```

## 🔄 维护脚本

### `fix_character_prompts.py`
**功能**：修复角色提示词
- 批量修正角色设定文件中的格式问题
- 确保prompt格式一致性

**运行**：
```bash
python3 scripts/fix_character_prompts.py
```

### `retry_failed_scripts.py`
**功能**：重试失败的测试
- 自动识别失败的测试案例
- 重新运行失败的评测

**运行**：
```bash
python3 scripts/retry_failed_scripts.py
```

### `monitor_progress.py`
**功能**：监控批量运行进度
- 实时显示批量测试的进度
- 输出当前完成情况

**运行**：
```bash
python3 scripts/monitor_progress.py
```

---

## 📝 注意事项

1. **运行路径**：所有脚本都应该在项目根目录下运行（使用`python3 scripts/xxx.py`）
2. **依赖关系**：
   - `sample_benchmark_cases.py` 依赖 `batch_evaluate_iedr.py` 的输出
   - `analyze_*` 系列脚本依赖相应的数据文件
3. **数据文件**：运行结果通常保存在`results/`目录下

## 🔗 相关文档

- 主文档：`../README.md`
- 快速开始：`../QUICK_START.md`
- EPJ系统：`../docs/EPJ.md`
- EPM系统：`../docs/EPM.md`
