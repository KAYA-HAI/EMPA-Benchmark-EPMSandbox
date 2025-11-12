# 📊 批量IEDR评估脚本使用说明

## 🎯 功能

批量评估所有 `character_setting/` 中剧本的初始共情赤字（IEDR），使用详细的prompt（包含evidence和reasoning）。

---

## 🚀 快速开始

### 1. 运行脚本

```bash
cd /Users/shiya/Desktop/Benchmark-test
python3 batch_evaluate_iedr.py
```

### 2. 等待完成

脚本会：
1. 自动加载所有剧本（约100个）
2. 为每个剧本调用Judger模型
3. 保存详细的评估结果

**预计时间**：约30-60分钟（取决于API速度）

### 3. 查看结果

结果保存在：`results/iedr_batch_results.json`

---

## 📁 输入数据

### 必需文件

1. **`Benchmark/topics/data/character_setting/script_*.md`**
   - Actor的完整system prompt
   - 包含角色信息、性格、共情需求等

2. **`Benchmark/topics/data/scenarios/character_stories.json`**
   - 每个剧本的scenario信息
   - 包含故事经过、结果、插曲

---

## 📤 输出格式

### 输出文件：`results/iedr_batch_results.json`

```json
[
  {
    "script_id": "script_001",
    "status": "success",
    "iedr": {
      "C.1": 3,
      "C.2": 2,
      "A.1": 3,
      "A.2": 2,
      "A.3": 3,
      "P.1": 2,
      "P.2": 3,
      "P.3": 3,
      "_detailed": {
        "C.1_level": 3,
        "C.1_evidence": "角色独特的、复杂的个人经历...",
        "C.1_reasoning": "从profile中提取到...",
        "C.2_level": 2,
        ...
      }
    },
    "timestamp": "2025-10-29T12:34:56.789"
  },
  ...
]
```

### 字段说明

| 字段 | 说明 |
|------|------|
| `script_id` | 剧本编号（如 script_001） |
| `status` | 评估状态（success / error） |
| `iedr` | 标准IEDR格式（C.1-P.3） |
| `iedr._detailed` | 详细格式（包含evidence和reasoning） |
| `timestamp` | 评估时间戳 |
| `error` | 错误信息（仅当status=error时） |

---

## 🔧 配置说明

### 脚本顶部的配置项

```python
# 文件路径
CHARACTER_SETTING_DIR = "Benchmark/topics/data/character_setting"
SCENARIOS_FILE = "Benchmark/topics/data/scenarios/character_stories.json"
OUTPUT_FILE = "results/iedr_batch_results.json"

# 模型配置
JUDGER_MODEL = "google/gemini-2.5-pro"
```

### 修改配置

如果需要更改模型或路径，直接编辑脚本顶部的配置项。

---

## 📊 Prompt差异

### 原版Prompt（`judger_prompts.py`）

```python
# 简洁版
- 要求输出简短reasoning（<20字）
- 输出格式：{"C.1": 2, "C.2": 1, ..., "reasoning": "简要说明"}
- 适合：在线评估，快速反馈
```

### 详细版Prompt（`batch_evaluate_iedr.py`）

```python
# 详细版（用户提供）
- 要求为每个指标提供evidence和reasoning
- 输出格式：{"C.1_level": 2, "C.1_evidence": "...", "C.1_reasoning": "..."}
- 适合：离线批量评估，深度分析
```

---

## 🎯 使用场景

### 何时使用批量脚本

✅ **适合**：
- 离线评估大量剧本
- 需要详细的evidence和reasoning
- 需要可追溯的评估依据
- 研究和分析用途

❌ **不适合**：
- 在线实时评估（太慢）
- 只需要最终分数（用原版即可）

### 何时使用原版Prompt

✅ **适合**：
- 在线对话评估（T=0时）
- 快速获取IEDR分数
- 用于向量计算

---

## 📈 处理大量数据

### 当前剧本数量：~100个

**预计资源消耗**：
- 时间：30-60分钟
- API调用：100次
- Tokens：每个约10k-15k（因为prompt很详细）

### 如果遇到API限流

1. **修改脚本添加延迟**：
   ```python
   import time
   for script_file in script_files:
       result = evaluate_single_script(...)
       time.sleep(5)  # 每个剧本之间延迟5秒
   ```

2. **分批处理**：
   ```python
   # 只处理前10个
   script_files = script_files[:10]
   ```

3. **使用更快的模型**：
   ```python
   JUDGER_MODEL = "google/gemini-2.5-flash"  # 更快但可能质量略低
   ```

---

## 🔍 结果验证

### 检查评估质量

```python
import json

# 加载结果
with open('results/iedr_batch_results.json', 'r') as f:
    results = json.load(f)

# 检查成功率
success = sum(1 for r in results if r['status'] == 'success')
print(f"成功率: {success}/{len(results)} = {success/len(results)*100:.1f}%")

# 检查某个剧本的详细reasoning
script_001 = next(r for r in results if r['script_id'] == 'script_001')
print(json.dumps(script_001['iedr']['_detailed'], indent=2, ensure_ascii=False))
```

### 常见问题检查

1. **所有指标都是0**：
   - 检查prompt是否正确传递
   - 检查LLM是否理解任务

2. **JSON解析失败**：
   - 检查max_tokens是否足够（当前6000）
   - 检查模型输出是否被截断

3. **Evidence为空**：
   - 检查LLM是否遵循指令
   - 可能需要调整prompt强调evidence的重要性

---

## 🛠️ 故障排查

### 问题1：找不到文件

```
❌ 错误：找不到目录 Benchmark/topics/data/character_setting
```

**解决**：
- 确保在项目根目录运行脚本
- 检查路径是否正确

### 问题2：API调用失败

```
❌ 评估失败: API error...
```

**解决**：
- 检查网络连接
- 检查API key配置（`config/api_config.py`）
- 检查模型名称是否正确

### 问题3：JSON解析失败

```
❌ JSON解析失败: Expecting value...
```

**解决**：
- 增加max_tokens（当前6000）
- 检查LLM响应格式
- 查看错误日志中的响应内容

---

## 📋 后续处理

### 1. 计算P_0向量

```python
from Benchmark.epj.scoring import calculate_initial_deficit

for result in results:
    if result['status'] == 'success':
        iedr = result['iedr']
        P_0 = calculate_initial_deficit(iedr)
        result['P_0'] = P_0
        print(f"{result['script_id']}: P_0 = {P_0}")
```

### 2. 统计分析

```python
import pandas as pd

# 转换为DataFrame
df = pd.DataFrame([
    {
        'script_id': r['script_id'],
        **r['iedr']
    }
    for r in results if r['status'] == 'success'
])

# 统计
print(df.describe())
print(df.mean())
```

### 3. 导出为CSV

```python
df.to_csv('results/iedr_batch_summary.csv', index=False)
```

---

## 🎉 完成后

### 验证结果

1. 检查 `results/iedr_batch_results.json`
2. 确认成功率 > 95%
3. 抽查几个剧本的详细reasoning

### 使用结果

- 作为EPJ系统的初始P_0向量输入
- 用于研究分析
- 验证量表的信效度

---

## 📚 相关文档

- **[EPJ_SYSTEM.md](Benchmark/epj/EPJ_SYSTEM.md)** - EPJ系统概览
- **[RUBRICS_DEFINITION.md](Benchmark/epj/RUBRICS_DEFINITION.md)** - 量表详细定义
- **[judger_prompts.py](Benchmark/epj/judger_prompts.py)** - 在线版Prompt

---

**创建日期**：2025-10-29  
**版本**：1.0

