# EPM v2.0 实现文档

## 概述

EPM (Empathy Progress Model) v2.0 是对EPJ系统的升级，引入了**能量动力学**的概念，将共情进展建模为一个物理过程。

## 核心概念

### 1. 理想方向向量 v*_0

```python
v*_0 = -P_0 / ||P_0||  # 归一化的理想方向
```

- **物理意义**：从初始赤字点指向原点的单位向量
- **作用**：作为全局基准，衡量每次移动的"对齐度"

### 2. 能量动力学

对于每一步移动 v_t：

```python
# 1. 对齐度（夹角余弦）
cos(θ_t) = (v_t · v*_0) / ||v_t||

# 2. 有效能量增量（投影功）
ΔE_t = ||v_t|| × cos(θ_t)

# 3. 累计能量
E_total += ΔE_t
```

- **ΔE_t > 0**：正向移动，积累能量
- **ΔE_t < 0**：反向移动，消耗能量
- **ΔE_t ≈ 0**：垂直移动，无效功

### 3. 三重胜利条件

```python
STOP-SUCCESS if:
  (r_t ≤ ε_distance) OR           # 几何胜利：精准到达
  (P_t·v*_0 ≥ -ε_direction) OR    # 位置胜利：穿越或接近
  (E_total ≥ ε_energy)             # 能量胜利：累积足够
```

#### 阈值设定（α = 0.10）

```python
ε_distance = 0.10 × ||P_0||    # 要求消除90%赤字
ε_direction = 0.10 × ||P_0||   # 半开放区域阈值
ε_energy = ||P_0||              # 能量阈值等于初始赤字
```

## 实现架构

### 文件修改清单

1. **`Benchmark/epj/vector_calculator.py`** ⭐ 核心计算
   - 新增 `_calculate_vector_norm`、`_calculate_dot_product`、`_normalize_vector`
   - 新增 `_initialize_epm_from_P0`（统一的EPM初始化方法）
   - 修改 `calculate_P_0`：调用EPM初始化
   - 修改 `calculate_v_t_and_update`：添加能量计算

2. **`Benchmark/epj/scoring.py`** ⭐ 判停逻辑
   - 新增 `check_epm_success`：三重胜利判断
   - 新增 `check_directional_collapse`：崩溃检测
   - 新增 `get_epm_state_summary`：状态摘要

3. **`Benchmark/orchestrator/epj_orchestrator.py`**
   - 修改 `__init__`：添加 `enable_epm` 参数
   - 修改 `initialize_with_precomputed_iedr`：使用预计算EPM参数
   - 修改 `evaluate_at_turn_K`：添加EPM摘要到状态包

4. **`Benchmark/orchestrator/chat_loop_epj.py`**
   - 修改 IEDR加载：附加EPM参数到 `filled_iedr`
   - 添加 EPM判停逻辑：检测 `epm_summary['success']`

5. **`batch_evaluate_iedr.py`**
   - 添加 EPM参数计算和存储

## 离线预计算优化

### 为什么需要预计算？

EPM参数（v*_0、ε_distance等）仅依赖于P_0，每个剧本的值是固定的。预计算可以：

- ✅ 节省运行时计算时间
- ✅ 确保所有测试使用相同参数
- ✅ 与IEDR预计算逻辑保持一致

### 如何添加EPM参数到现有数据？

```bash
# 使用临时脚本（已完成，可删除）
python3 add_epm_to_iedr.py

# 或者重新运行批量评估（会自动包含EPM参数）
python3 batch_evaluate_iedr.py
```

### 数据结构

`iedr_batch_results.json` 中每个条目：

```json
{
  "script_id": "script_001",
  "status": "success",
  "iedr": { "C.1": 3, "C.2": 3, ... },
  "P_0": {
    "C": -18,
    "A": -23,
    "P": -13,
    "total": 31.97
  },
  "epm": {
    "P_0_norm": 31.97,
    "v_star_0": [0.5631, 0.7194, 0.4067],
    "epsilon_distance": 3.20,
    "epsilon_direction": 3.20,
    "epsilon_energy": 31.97,
    "alpha": 0.10
  },
  "timestamp": "..."
}
```

## 运行时行为

### 初始化（T=0）

```
🆕 [EPM v2.0] 使用预计算参数
   ||P_0|| = 31.97
   v*_0（理想方向）= (0.563, 0.72, 0.407)
   ε_distance（距离阈值）= 3.20
   ε_direction（方向阈值）= 3.20
   ε_energy（能量阈值）= 31.97
```

### 每轮计算（T>0）

```
🆕 [EPM v2.0] 能量动力学分析
   移动模长 ||v_t|| = 3.16
   对齐度 cos(θ) = 0.762 (正向)
   有效能量增量 ΔE = +2.41
   累计能量 E_total = 2.41 / 31.97 (7.5%)
   当前距离 ||P_t|| = 29.63
   位置投影 P_t·v*_0 = -29.56 (未穿越)
```

### 判停触发

```
🎉 [EPM v2.0] 检测到胜利条件!
   胜利类型: energetic
   指标: E_total=32.50, r_t=8.45, projection=-5.32
   阈值: ε_energy=31.97, ε_distance=3.20, ε_direction=3.20

🏁 [EPM判停] 对话成功终止
   类型: EPM_SUCCESS_ENERGETIC
   理由: EPM v2.0 判定成功: 能量胜利（累积足够的共情能量）
```

## 向后兼容

EPM v2.0 完全向后兼容EPJ v1.0：

- 所有EPJ v1.0字段保留（`distance`, `in_zone`等）
- EPM字段作为**可选**新增字段（`epm`）
- 可通过 `enable_epm=False` 禁用EPM，回退到EPJ v1.0

## 配置参数

### 全局参数（在 `_initialize_epm_from_P0` 中）

```python
alpha = 0.10  # 相对阈值系数（10%，可调整为5%-15%）
collapse_window = 3  # 崩溃检测窗口（连续3步负能量）
```

### 如何调整参数

如需调整α值，修改 `Benchmark/epj/vector_calculator.py`:

```python
# 当前值：要求消除90%赤字
alpha = 0.10

# 更严格（消除95%赤字）
alpha = 0.05

# 更宽松（消除85%赤字）
alpha = 0.15
```

修改后需要重新运行 `batch_evaluate_iedr.py` 或使用脚本更新所有EPM参数。

## 测试与验证

### 单案例测试

```bash
python3 run_real_conversation.py
```

观察输出中的EPM指标是否正常显示。

### 批量测试

```bash
# 测试特定script
python3 run_real_conversation.py --script 001
```

### 关键验证点

- ✅ EPM初始化显示预计算参数
- ✅ 每轮显示能量动力学分析
- ✅ ε_distance = ε_direction（设计要求）
- ✅ 能量累计正确
- ✅ 判停条件正确触发

## 常见问题

### Q1: 为什么ε_distance和ε_direction相同？

**A**: 这是设计选择。两个阈值使用同一个α系数，确保"原点附近的球"和"半空间的闭合侧"在几何上对齐。

### Q2: 如果没有预计算EPM参数会怎样？

**A**: 系统会自动回退到运行时计算（调用 `_initialize_epm_from_P0`），不影响功能，只是稍慢。

### Q3: 能量胜利和几何胜利有什么区别？

**A**:
- **几何胜利**：精准到达，r_t很小（< 10% ||P_0||）
- **能量胜利**：娓娓道来，累积能量充足，即使位置不够精准

这符合EPM的核心哲学：**共情不只是"到达零点"，而是"释放足够的正向能量"**。

## 性能影响

- **内存**：每个轨迹点增加约50-100字节（EPM字段）
- **计算**：每轮增加约5-10个浮点运算（可忽略）
- **API调用**：无变化（EPM只是数学计算）
- **初始化时间**：使用预计算后接近零（仅字典查找）

## 未来扩展

可能的增强方向：

1. **自适应α**：根据案例难度动态调整阈值
2. **能量衰减**：引入时间衰减因子
3. **角度惩罚**：对严重偏离方向的移动施加惩罚
4. **多模态能量**：分别计算C、A、P轴的能量

---

**最后更新**: 2025-11-03  
**版本**: EPM v2.0  
**状态**: ✅ 已完成并测试通过

