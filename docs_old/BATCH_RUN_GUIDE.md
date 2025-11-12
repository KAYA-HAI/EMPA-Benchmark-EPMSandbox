# 批量运行指南

完整的100个剧本批量测试指南

---

## 🚀 快速开始

### 方式1：运行所有剧本（推荐）

```bash
python3 run_all_scripts.py
```

**特点：**
- ✅ 自动运行所有100个剧本
- ✅ 支持断点续传（可随时中断，下次自动跳过已完成的）
- ✅ 实时保存每个剧本的结果
- ✅ 详细的进度显示

### 方式2：自定义批量运行

```bash
python3 run_batch_conversations.py
```

**支持的模式：**
1. 运行所有剧本 (001-100)
2. 运行指定范围 (如 001-010)
3. 运行指定列表 (如 001,005,010,020)
4. 测试模式（只运行前3个）

---

## ⚙️ 配置参数

### 在 `run_all_scripts.py` 中修改（第19-27行）

```python
# 基础参数
MAX_TURNS = 15                              # 每个剧本的最大轮数
K = 3                                       # EPJ评估周期

# 模型配置
ACTOR_MODEL = "openai/gpt-4o-mini"         # Actor模型
DIRECTOR_MODEL = "openai/gpt-4o-mini"      # Director模型
JUDGER_MODEL = "openai/gpt-4o-mini"        # Judger模型
TEST_MODEL = "openai/gpt-4o-mini"          # 被测模型

# 输出设置
OUTPUT_DIR = "results/all_scripts"         # 结果保存目录
SLEEP_BETWEEN_SCRIPTS = 3                  # 剧本间休息时间（秒）
```

### 推荐的模型配置

**快速测试（便宜）：**
```python
ACTOR_MODEL = "openai/gpt-4o-mini"
DIRECTOR_MODEL = "openai/gpt-4o-mini"
JUDGER_MODEL = "openai/gpt-4o-mini"
TEST_MODEL = "openai/gpt-4o-mini"
```

**高质量评估：**
```python
ACTOR_MODEL = "anthropic/claude-3.5-sonnet"
DIRECTOR_MODEL = "anthropic/claude-3.5-sonnet"
JUDGER_MODEL = "anthropic/claude-3.5-sonnet"
TEST_MODEL = "openai/gpt-4"  # 被测模型可以单独配置
```

---

## 📂 输出结构

### 结果文件组织

```
results/all_scripts/
├── result_001.json           # 剧本001的完整结果
├── result_002.json           # 剧本002的完整结果
├── ...
├── result_100.json           # 剧本100的完整结果
├── progress.json             # 实时进度（断点续传用）
├── final_summary.json        # 最终汇总报告
├── analysis_summary.csv      # CSV格式的汇总数据
└── statistics.json           # 详细统计数据
```

### 单个结果文件内容

每个 `result_XXX.json` 包含：

```json
{
  "script_id": "001",
  "剧本编号": "script_001",
  "total_turns": 15,
  "termination_reason": "达到最大轮数",
  "history": [...],          // 完整对话历史
  "epj": {
    "P_0_initial_deficit": "(-10, -21, -25)",
    "P_final_position": "(5, 1, 3)",
    "trajectory": [...],     // EPJ轨迹
    "total_evaluations": 5,
    "K": 3,
    "epsilon": 1.0
  },
  "director_actions": [...], // Director的所有动作
  "elapsed_time_seconds": 125.5,
  "timestamp": "2025-10-28T..."
}
```

---

## 📊 结果分析

### 分析所有结果

```bash
# 分析默认目录
python3 analyze_batch_results.py

# 分析指定目录
python3 analyze_batch_results.py --dir results/batch_runs
```

### 分析报告内容

1. **终止原因分布**
   - 达到最大轮数
   - EPJ达标（成功）
   - 其他原因

2. **对话轮数分布**
   - 轮数范围
   - 平均轮数
   - 分布图表

3. **EPJ向量统计**
   - P_0（初始赤字）分布
   - P_final（最终位置）分布
   - 向量变化趋势

4. **导出数据**
   - CSV格式（可用Excel打开）
   - JSON格式（完整数据）

---

## 🔄 使用流程

### 完整批量运行流程

```bash
# 1. 配置API key
vim config/api_config.py
# 填入: OPENROUTER_API_KEY = "sk-or-v1-你的key"

# 2. （可选）修改运行参数
vim run_all_scripts.py
# 修改: MAX_TURNS, K, 模型配置等

# 3. 开始批量运行
python3 run_all_scripts.py

# 4. 等待完成（可随时Ctrl+C中断）
# 提示: 100个剧本，每个约2-5分钟，总计约3-8小时

# 5. 分析结果
python3 analyze_batch_results.py

# 6. 查看详细数据
cat results/all_scripts/analysis_summary.csv
```

---

## 🛡️ 断点续传

### 如何使用

批量运行**自动支持断点续传**：

1. **中断运行**: 按 `Ctrl+C` 随时中断
2. **查看进度**: 检查 `results/all_scripts/` 目录中已有的文件
3. **继续运行**: 再次运行 `python3 run_all_scripts.py`
4. **自动跳过**: 系统会自动跳过已完成的剧本

### 示例

```bash
# 第一次运行（完成了30个剧本后中断）
$ python3 run_all_scripts.py
# ... 运行到 script_030 时按 Ctrl+C

# 第二次运行（自动从script_031开始）
$ python3 run_all_scripts.py
📋 运行状态:
   总剧本数: 100
   已完成: 30
   待运行: 70
   
准备运行 70 个剧本，是否继续？(y/n): y
```

---

## 📊 运行时估算

### 时间估算

假设每个剧本平均：
- 对话轮数: 10轮
- 每轮耗时: 15秒（包括4个LLM调用）
- EPJ评估: 3次 × 5秒 = 15秒

**单个剧本**: 约 2-3 分钟

**100个剧本总计**: 
- 最快: 约 3 小时
- 平均: 约 4-5 小时  
- 最慢: 约 8 小时（包括重试和休息）

### API成本估算（以 gpt-4o-mini 为例）

每个剧本约：
- Actor: 10轮 × 500 tokens = 5,000 tokens
- TestModel: 10轮 × 500 tokens = 5,000 tokens
- Director: 5次 × 1,000 tokens = 5,000 tokens
- Judger: 4次 × 2,000 tokens = 8,000 tokens

**单个剧本**: 约 23,000 tokens  
**100个剧本**: 约 2,300,000 tokens

**费用**: 
- gpt-4o-mini: 约 $0.50-1.00
- claude-3-haiku: 约 $0.60-1.20
- claude-3.5-sonnet: 约 $6-12

---

## 🎯 使用场景

### 1. 完整Benchmark测试

```bash
# 运行所有100个剧本，全面评估AI模型的共情能力
python3 run_all_scripts.py
```

### 2. 范围测试

```bash
# 只测试前10个剧本
python3 run_batch_conversations.py
# 选择模式2，输入范围: 001 - 010
```

### 3. 特定类型测试

```bash
# 测试特定的剧本（需要先查看剧本内容筛选）
python3 run_batch_conversations.py
# 选择模式3，输入: 001,010,020,030
```

### 4. 对比测试

```bash
# 第一轮：使用 gpt-4o-mini
vim run_all_scripts.py  # 设置模型
python3 run_all_scripts.py
mv results/all_scripts results/gpt4o_mini_results

# 第二轮：使用 claude-3.5-sonnet
vim run_all_scripts.py  # 更换模型
python3 run_all_scripts.py
mv results/all_scripts results/claude35_sonnet_results

# 对比分析
python3 analyze_batch_results.py --dir results/gpt4o_mini_results
python3 analyze_batch_results.py --dir results/claude35_sonnet_results
```

---

## 🔧 常见问题

### Q1: 如何暂停批量运行？

**A**: 按 `Ctrl+C` 即可安全中断，进度会自动保存。

### Q2: 如何查看当前进度？

**A**: 查看 `results/all_scripts/` 目录中的文件数量，或查看 `progress.json`。

### Q3: 某个剧本运行失败怎么办？

**A**: 系统会记录失败原因，继续运行下一个剧本。可以稍后单独重跑失败的剧本：

```bash
# 单独运行某个剧本
vim run_real_conversation.py
# 修改 SCRIPT_ID = "005"
python3 run_real_conversation.py
```

### Q4: 如何重新运行所有剧本？

**A**: 删除或重命名结果目录：

```bash
# 备份旧结果
mv results/all_scripts results/all_scripts_backup_20251028

# 重新运行
python3 run_all_scripts.py
```

### Q5: 运行太慢怎么办？

**A**: 可以调整参数：

```python
# 减少最大轮数
MAX_TURNS = 10  # 从15改为10

# 减少评估频率
K = 5  # 从3改为5（评估次数减少）

# 使用更快的模型
ACTOR_MODEL = "openai/gpt-3.5-turbo"
```

---

## 📝 最佳实践

### 1. 分批运行

建议分成多批运行，每批20-30个剧本：

```bash
# 第一批: 001-025
python3 run_batch_conversations.py
# 选择模式2，输入: 001, 025

# 第二批: 026-050
# 选择模式2，输入: 026, 050

# 第三批: 051-075
# 第四批: 076-100
```

### 2. 定期检查

每运行完一批，进行分析：

```bash
python3 analyze_batch_results.py
```

### 3. 备份结果

重要结果要及时备份：

```bash
# 备份整个结果目录
cp -r results/all_scripts results/backup_$(date +%Y%m%d_%H%M%S)
```

### 4. 日志记录

重定向输出到日志文件：

```bash
python3 run_all_scripts.py 2>&1 | tee logs/batch_run_$(date +%Y%m%d_%H%M%S).log
```

---

## 📈 结果导出

### CSV格式（Excel可打开）

```bash
# 生成CSV
python3 analyze_batch_results.py

# 打开查看
open results/all_scripts/analysis_summary.csv
```

### JSON格式（编程分析）

```python
import json

# 读取汇总统计
with open('results/all_scripts/statistics.json', 'r') as f:
    stats = json.load(f)

# 读取单个剧本结果
with open('results/all_scripts/result_001.json', 'r') as f:
    result = json.load(f)
```

---

## 🎓 高级用法

### 1. 并行运行（谨慎使用）

如果API限额足够，可以修改脚本支持并行：

```python
# 需要修改代码添加多线程支持
# 不推荐，容易触发API限流
```

### 2. 只运行特定类型的剧本

```python
# 在 run_batch_conversations.py 中添加过滤逻辑
# 例如：只运行"高共情阈值"的剧本
```

### 3. 自定义评估指标

修改 `analyze_batch_results.py` 添加自定义分析：

```python
# 例如：分析不同共情阈值的成功率
# 例如：统计各维度的向量变化
```

---

## 🔍 监控和调试

### 实时监控进度

```bash
# 在另一个终端窗口查看结果数量
watch -n 5 "ls -1 results/all_scripts/result_*.json | wc -l"

# 查看最新完成的剧本
ls -lt results/all_scripts/result_*.json | head -5
```

### 查看某个剧本的详细结果

```bash
# 格式化输出
python3 -m json.tool results/all_scripts/result_001.json

# 查看关键信息
cat results/all_scripts/result_001.json | grep -A 5 "termination_reason"
```

---

## ⚡ 性能优化建议

### 1. API调用优化

```python
# 减少评估频率
K = 5  # 从每3轮评估改为每5轮

# 减少最大轮数
MAX_TURNS = 12  # 从15改为12
```

### 2. 网络优化

```bash
# 使用更稳定的网络环境
# 考虑使用代理（如果需要）
export HTTP_PROXY=http://your-proxy:port
export HTTPS_PROXY=http://your-proxy:port
```

### 3. 错误重试

脚本会自动记录失败的剧本，可以手动重跑：

```python
# 查看失败的剧本
cat results/all_scripts/final_summary.json | grep "failed"

# 单独重跑
SCRIPT_ID="失败的ID" python3 run_real_conversation.py
```

---

## 📋 检查清单

运行前检查：

- [ ] API key 已配置（`config/api_config.py`）
- [ ] 模型参数已设置（`run_all_scripts.py`）
- [ ] 输出目录已确认
- [ ] 网络连接正常
- [ ] 有足够的磁盘空间（约100MB）
- [ ] API账户余额充足

运行中监控：

- [ ] 定期查看进度
- [ ] 检查错误日志
- [ ] 监控API使用量
- [ ] 备份重要结果

运行后分析：

- [ ] 运行分析脚本
- [ ] 查看汇总报告
- [ ] 检查异常结果
- [ ] 导出数据用于进一步分析

---

## 🎉 预期结果

### 成功运行后，你将得到：

1. **100个完整的对话记录**
   - 每个剧本的完整对话历史
   - Actor和TestModel的所有消息

2. **100条EPJ轨迹**
   - 每个剧本的初始赤字向量
   - 完整的向量演化过程
   - 最终位置和达标情况

3. **统计分析数据**
   - 终止原因分布
   - 轮数分布
   - 向量统计
   - 时间统计

4. **可视化数据（CSV）**
   - 可导入Excel/Numbers
   - 可用于绘制图表
   - 可用于论文/报告

---

## 💡 使用建议

### 首次使用

1. **先测试**: 使用测试模式运行3个剧本
2. **检查结果**: 确保输出符合预期
3. **调整参数**: 根据测试结果优化配置
4. **正式批量**: 运行所有剧本

### 大规模运行

1. **分批运行**: 每批20-30个，便于管理
2. **定期备份**: 每批完成后备份结果
3. **错误处理**: 记录失败的剧本，稍后重试
4. **数据验证**: 每批完成后运行分析脚本

---

## 📞 故障排除

### 问题：API限流

**症状**: 出现 "Rate limit exceeded" 错误

**解决**:
```python
# 增加休息时间
SLEEP_BETWEEN_SCRIPTS = 10  # 从3秒改为10秒
```

### 问题：内存不足

**症状**: 程序崩溃或变慢

**解决**:
```bash
# 分批运行，每批运行后重启
# 或增加系统swap空间
```

### 问题：某些剧本总是失败

**症状**: 特定剧本重复失败

**解决**:
1. 查看该剧本的数据文件是否完整
2. 检查错误日志
3. 单独运行该剧本调试
4. 跳过该剧本，稍后处理

---

## 🎁 额外功能

### 生成Markdown报告

可以扩展分析脚本生成可读性更好的报告：

```python
# 在 analyze_batch_results.py 中添加
def generate_markdown_report(stats, output_path):
    # 生成美观的Markdown格式报告
    pass
```

### 可视化图表

使用Python绘图库：

```python
import matplotlib.pyplot as plt
import pandas as pd

# 读取CSV
df = pd.read_csv('results/all_scripts/analysis_summary.csv')

# 绘制轮数分布
df['轮数'].hist()
plt.savefig('results/turns_distribution.png')
```

---

**创建日期**: 2025-10-28  
**适用版本**: EPJ v1.0+  
**支持剧本**: script_001 - script_100

