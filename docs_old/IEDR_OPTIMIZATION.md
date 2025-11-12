# IEDR 加载优化

**日期**: 2025-10-30  
**目的**: 避免在每次对话运行时重复计算IEDR，节省API消耗和运行时间

---

## 问题背景

之前的流程：
```
每次运行对话 → Judger.fill_iedr() → 调用LLM → 计算P_0
             ↓
         消耗API，耗时较长
```

由于已经完成了所有100个剧本的IEDR批量评估（存储在`results/iedr_batch_results.json`），每次对话运行时重复计算IEDR是不必要的浪费。

---

## 解决方案

### 新增组件

#### 1. `Benchmark/epj/iedr_loader.py`
- **功能**: 从 `iedr_batch_results.json` 加载预先计算的IEDR数据
- **核心类**: `IEDRLoader`
- **主要方法**:
  - `get_iedr(script_id)`: 获取完整IEDR数据
  - `get_P_0(script_id)`: 获取初始赤字向量
  - `get_iedr_dict(script_id)`: 获取IEDR量表字典

#### 2. `EPJOrchestrator.initialize_with_precomputed_iedr()`
- **功能**: 使用预先计算的IEDR初始化，跳过Judger调用
- **参数**: 
  - `filled_iedr`: 预先填写的IEDR量表
  - `P_0`: 预先计算的初始赤字向量 (C, A, P)

### 修改的文件

#### 1. `Benchmark/orchestrator/chat_loop_epj.py`
**修改**: T=0初始化阶段
```python
# 新逻辑
precomputed_data = load_precomputed_iedr(script_id)
if precomputed_data:
    # ✅ 使用预计算的IEDR（跳过Judger调用）
    init_result = epj_orch.initialize_with_precomputed_iedr(filled_iedr, P_0)
else:
    # 回退：实时计算（消耗API）
    init_result = epj_orch.initialize_at_T0(script_content)
```

#### 2. `Benchmark/epj/judger_prompts.py`
**修改**: 添加说明注释
- `generate_iedr_prompt()` 现在主要用于批量评估
- 对话运行时从 `iedr_batch_results.json` 加载

---

## 优化效果

### ✅ 节省资源
- **API调用**: 每次对话节省1次Judger调用（~6000 tokens）
- **时间**: 每次对话启动快约5-10秒

### ✅ 保持兼容
- 如果找不到预计算的IEDR，自动回退到实时计算
- 不影响新剧本的评估流程

### ✅ 数据一致性
- 所有对话使用相同的初始IEDR评估
- 便于结果对比和分析

---

## 使用方式

### 对话运行（自动优化）
```bash
python run_real_conversation.py
# 自动从 iedr_batch_results.json 加载IEDR
# 输出：📝 跳过Judger调用，节省API消耗
```

### 批量评估新剧本（生成IEDR）
```bash
python scripts/batch_evaluate_iedr.py
# 生成/更新 iedr_batch_results.json
```

---

## 文件结构

```
Benchmark/
├── epj/
│   ├── iedr_loader.py          # 新增：IEDR加载器
│   ├── judger_prompts.py       # 修改：添加说明注释
│   └── ...
├── orchestrator/
│   ├── epj_orchestrator.py     # 修改：新增 initialize_with_precomputed_iedr()
│   ├── chat_loop_epj.py        # 修改：使用预计算IEDR
│   └── ...
└── ...

results/
└── iedr_batch_results.json     # 预计算的IEDR数据（100个剧本）
```

---

## 技术细节

### IEDR数据格式
```json
{
  "script_id": "script_001",
  "status": "success",
  "iedr": {
    "C.1": 3, "C.2": 2, "C.3": 2,
    "A.1": 3, "A.2": 2, "A.3": 3,
    "P.1": 0, "P.2": 3, "P.3": 1,
    "_detailed": {...}
  },
  "P_0": {
    "C": -16,
    "A": -21,
    "P": -15,
    "total": -52
  },
  "timestamp": "2025-10-29T18:03:57.915117"
}
```

### 初始化流程对比

**优化前**:
```
chat_loop_epj.py
  └─> epj_orch.initialize_at_T0(script_content)
       └─> judger.fill_iedr(script_content)  ← 调用LLM
            └─> calculator.calculate_P_0(filled_iedr)
```

**优化后**:
```
chat_loop_epj.py
  └─> load_precomputed_iedr(script_id)  ← 读取JSON文件
       └─> epj_orch.initialize_with_precomputed_iedr(iedr, P_0)
            └─> 直接初始化（无LLM调用）
```

---

## 测试验证

已通过测试：
- ✅ IEDR加载器正确读取数据
- ✅ EPJOrchestrator正确使用预计算IEDR
- ✅ 成功跳过Judger调用
- ✅ 回退机制（找不到预计算数据时）正常工作

---

## 注意事项

1. **新剧本**: 需要先运行 `batch_evaluate_iedr.py` 生成IEDR
2. **数据同步**: 如果修改了IEDR定义或评分规则，需要重新运行批量评估
3. **向后兼容**: 保留了原有的 `initialize_at_T0()` 方法作为回退方案

---

## 总结

此优化通过复用预先计算的IEDR数据，显著提升了对话运行效率，同时保持了系统的灵活性和向后兼容性。这是一个重要的性能优化，为批量运行对话评估奠定了基础。


