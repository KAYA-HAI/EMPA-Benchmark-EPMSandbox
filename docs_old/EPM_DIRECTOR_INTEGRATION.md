# EPM v2.0 与 Director 集成说明

## ✅ 确认：EPM 数据已完整传递给 Director

### 📊 数据流图

```
VectorCalculator (计算EPM指标)
    ↓
EPJOrchestrator (生成EPM摘要)
    ↓
state_packet['epm_summary'] (状态包)
    ↓
Director Prompt (格式化显示)
    ↓
Director LLM (理解并决策)
```

---

## 1️⃣ 数据源：VectorCalculator

**文件**: `Benchmark/epj/vector_calculator.py`

每轮计算后，`trajectory` 中的每个点都包含 `epm` 字段：

```python
trajectory_point['epm'] = {
    "v_t_norm": round(v_t_norm, 2),      # 移动模长
    "alignment": round(alignment, 4),    # 对齐度
    "delta_E": round(delta_E, 2),        # 能量增量
    "E_total": round(self.E_total, 2),   # 累计能量
    "P_norm": round(P_t_norm, 2),        # 当前距离
    "projection": round(projection, 2)   # 位置投影
}
```

---

## 2️⃣ 数据汇总：EPJOrchestrator

**文件**: `Benchmark/orchestrator/epj_orchestrator.py`

### 关键代码（第234-258行）

```python
# EPM v2.0: 添加能量动力学摘要（如果启用）
if self.enable_epm and self.calculator.v_star_0 is not None:
    from Benchmark.epj.scoring import get_epm_state_summary
    
    # 获取最新的EPM指标
    latest_trajectory = self.calculator.trajectory[-1]
    if 'epm' in latest_trajectory:
        epm_data = latest_trajectory['epm']
        
        epm_summary = get_epm_state_summary(
            current_turn=current_turn,
            r_t=epm_data['P_norm'],
            projection=epm_data['projection'],
            E_total=epm_data['E_total'],
            epsilon_distance=self.calculator.epsilon_distance_relative,
            epsilon_direction=self.calculator.epsilon_direction_relative,
            epsilon_energy=self.calculator.epsilon_energy,
            trajectory=self.calculator.trajectory
        )
        
        state_packet['epm_summary'] = epm_summary
```

### epm_summary 结构

```python
{
    "turn": 15,
    "success": False,
    "victory_type": None,  # or "geometric"/"positional"/"energetic"
    "collapsed": False,
    "metrics": {
        "r_t": 28.50,
        "projection": -25.30,
        "E_total": 5.20
    },
    "thresholds": {
        "epsilon_distance": 3.03,
        "epsilon_direction": 3.03,
        "epsilon_energy": 30.28
    },
    "progress": {
        "geometric": "5.9%",
        "positional": "16.5%",
        "energetic": "17.2%"
    }
}
```

---

## 3️⃣ 数据展示：Director Prompt

**文件**: `Benchmark/prompts/director_prompts.py`

### Director 看到的 EPM 信息（第188-216行）

```
【EPM v2.0 能量动力学分析】

当前状态：
  • 距离原点: 28.50 / 3.03 (几何进度: 5.9%)
  • 位置投影: -25.30 / -3.03 (位置进度: 16.5%)
  • 累计能量: 5.20 / 30.28 (能量进度: 17.2%)

胜利条件（满足任一即可）：
  ✓ 几何胜利: 距离 ≤ 3.03 ⏳
  ✓ 位置胜利: 投影 ≥ -3.03 ⏳
  ✓ 能量胜利: 累计 ≥ 30.28 ⏳

方向性健康: ✅ 正常

EPM参数说明：
  - 距离(r_t): 当前位置到原点的欧氏距离，越小越好
  - 投影(projection): P_t在理想方向上的投影，越接近0越好（负值表示未穿越，正值表示已穿越）
  - 累计能量(E_total): 所有有效移动的能量总和，反映了"等效进展"
  - 方向性崩溃: 如果连续3步的能量增量都为负，表示持续远离目标
```

---

## 4️⃣ 决策指南：EPM 策略补充（第288-313行）

```
#### 🆕 基于EPM能量动力学的策略补充

**如果系统启用了EPM v2.0，额外参考以下指标：**

1. **距离指标(r_t)**：
   - 快速下降 → AI共情有效，继续当前策略
   - 波动不定 → AI共情不稳定，考虑调整策略或释放新素材
   - 持续上升 → AI共情失败，需要干预或考虑结束

2. **能量指标(E_total)**：
   - 持续增长 → 对话朝正确方向发展，保持节奏
   - 增长缓慢 → 进展有限，可能需要释放关键剧情或记忆
   - 停滞或下降 → 对话陷入困境，需要强力干预

3. **位置投影(projection)**：
   - 接近 -ε_direction → 即将达到位置胜利，可以考虑收尾
   - 变为正值 → 已穿越目标区域，可以优雅结束

4. **方向性崩溃预警**：
   - 如果检测到崩溃（连续3步负能量），说明对话严重偏离
   - 策略：立即释放强力素材（关键剧情或深层记忆）或果断结束

**EPM胜利条件判断**：
- 任一条件满足即可终止对话（标记为成功）
- 不必等待所有条件都满足
- 三个条件提供了多角度的成功判定标准
```

---

## 📋 Director 可用的 EPM 信息总结

### 直接可用的数值

| 字段 | 含义 | 单位 | Director 用途 |
|------|------|------|--------------|
| `r_t` | 当前距离原点 | 浮点数 | 判断几何进度 |
| `projection` | 位置投影 | 浮点数 | 判断是否接近/穿越目标 |
| `E_total` | 累计有效能量 | 浮点数 | 判断等效进展 |
| `collapsed` | 是否方向性崩溃 | 布尔值 | 预警对话失控 |
| `success` | 是否达到胜利条件 | 布尔值 | 判断是否可以结束 |
| `victory_type` | 胜利类型 | 字符串 | 了解成功原因 |

### 进度百分比（直观理解）

| 维度 | 字段 | 说明 |
|------|------|------|
| 几何进度 | `progress.geometric` | 距离缩短的百分比 |
| 位置进度 | `progress.positional` | 向目标半平面靠近的百分比 |
| 能量进度 | `progress.energetic` | 能量累积的百分比 |

---

## 🧠 Director 理解 EPM 的三个层次

### Level 1: 数值感知

Director 能看到所有关键数值（r_t, projection, E_total）及其阈值。

### Level 2: 进度理解

通过百分比（如 "几何进度: 5.9%"），Director 能直观理解当前进展。

### Level 3: 策略应用

通过决策指南，Director 知道：
- 如何根据不同指标调整策略
- 何时应该干预
- 何时可以结束对话

---

## ✅ 验证清单

- [x] **VectorCalculator** 正确计算 EPM 指标并存入 trajectory
- [x] **EPJOrchestrator** 从 trajectory 提取 EPM 数据并生成 epm_summary
- [x] **state_packet** 包含完整的 epm_summary
- [x] **Director Prompt** 格式化显示 EPM 信息（数值 + 说明）
- [x] **决策指南** 包含 EPM 策略建议
- [x] **结果文件** 存储完整的 EPM 数据（`epj_conversation_result.json`）

---

## 🔍 如何检查 Director 是否收到 EPM 数据

### 方法 1: 查看运行日志

运行测试时，查看 Director 的决策输出。如果 EPM 启用，会看到：

```
【EPM v2.0 能量动力学分析】
当前状态：
  • 距离原点: 28.50 / 3.03 (几何进度: 5.9%)
  ...
```

### 方法 2: 检查结果文件

在 `epj_conversation_result.json` 中查看：

```json
{
  "history": [
    {
      "role": "actor",
      "content": "...",
      "director_guidance": "..."  // Director的决策应该基于EPM信息
    }
  ]
}
```

### 方法 3: Debug 模式

在 `epj_orchestrator.py` 中添加 print：

```python
if epm_summary:
    print(f"🆕 [EPM] 传递给Director的摘要:")
    print(f"   r_t = {epm_summary['metrics']['r_t']}")
    print(f"   projection = {epm_summary['metrics']['projection']}")
    print(f"   E_total = {epm_summary['metrics']['E_total']}")
    print(f"   success = {epm_summary['success']}")
```

---

## 🎯 结论

✅ **EPM 数据已完整传递给 Director**

Director 在每轮评估后会收到：
1. **EPJ v1.0 基础数据**: P_0, P_t, v_t, distance
2. **EPM v2.0 扩展数据**: r_t, projection, E_total, collapsed, success, victory_type
3. **进度百分比**: geometric, positional, energetic
4. **参数说明**: 每个指标的含义和使用方法
5. **策略指南**: 如何根据 EPM 指标做决策

Director 现在具备了完整的 EPM 感知能力，能够：
- 理解能量动力学的含义
- 根据三重胜利条件判断对话状态
- 识别方向性崩溃预警
- 做出更科学的剧情控制决策

