# EPM v2.0 结果文件结构说明

## 📄 文件概览

`epj_conversation_result.json` 现在包含完整的 EPM v2.0 能量动力学数据。

## 🏗️ JSON 结构

```json
{
  "total_turns": 38,
  "termination_reason": "...",
  "script_id": "001",
  "scenario": { ... },
  "history": [ ... ],
  
  // 模型信息
  "test_model_name": "qwen/qwen3-32b",
  "actor_model": "google/gemini-2.5-pro",
  "judger_model": "anthropic/claude-3.7-sonnet",
  "director_model": "anthropic/claude-3.7-sonnet",
  
  // EPJ/EPM 完整数据
  "epj": {
    // 基础 EPJ 数据
    "P_0_initial_deficit": [-18, -23, -13],
    "P_final_position": [-20, -34, 9],
    "total_evaluations": 38,
    "K": 1,
    "epsilon": 1.0,
    
    // IEDR 详细信息
    "iedr_details": {
      "filled_iedr": { ... },
      "P_0": { ... },
      "initial_distance": 30.28,
      "source": "precomputed"
    },
    
    // 🆕 EPM v2.0 全局参数
    "epm_enabled": true,
    "epm_params": {
      "v_star_0": [0.5945, 0.7595, 0.4295],  // 全局理想方向向量
      "epsilon_distance": 3.03,               // 距离阈值 (0.10 × ||P_0||)
      "epsilon_direction": 3.03,              // 方向阈值 (0.10 × ||P_0||)
      "epsilon_energy": 30.28,                // 能量阈值 (||P_0||)
      "E_total_final": 15.67,                 // 最终累计能量
      "alpha": 0.10                           // 相对阈值系数
    },
    
    // 完整轨迹（包含每轮的 EPM 数据）
    "trajectory": [
      {
        "turn": 0,
        "P_t": [-18, -23, -13],
        "v_t": [0, 0, 0],
        "distance": 30.28,
        "in_zone": false,
        
        // 🆕 EPM 初始化数据
        "epm": {
          "v_star_0": [0.5945, 0.7595, 0.4295],
          "epsilon_distance": 3.03,
          "epsilon_direction": 3.03,
          "epsilon_energy": 30.28,
          "P_0_norm": 30.28,
          "alpha": 0.10
        }
      },
      {
        "turn": 1,
        "P_t": [-17, -22, -13],
        "v_t": [1, 1, 0],
        "distance": 29.0,
        "in_zone": false,
        
        // 🆕 EPM 实时计算数据
        "epm": {
          "v_t_norm": 1.41,           // 移动向量模长
          "alignment": 0.9623,        // 对齐度 cos(θ)
          "delta_E": 1.36,            // 有效能量增量 ΔE
          "E_total": 1.36,            // 累计能量
          "P_norm": 29.0,             // 当前距离 ||P_t||
          "projection": -27.64        // 位置投影 P_t·v*_0
        },
        
        // Judger 详细分析（每轮都有）
        "mdep_analysis": {
          "C_Pos": { "level": 1, "evidence": "...", "reasoning": "..." },
          "C_Neg": { "level": 0, "evidence": "...", "reasoning": "..." },
          // ... 更多维度
        }
      },
      // ... 后续轮次
    ]
  }
}
```

## 📊 EPM 数据字段说明

### 全局参数 (`epm_params`)

| 字段 | 类型 | 说明 | 计算方式 |
|------|------|------|----------|
| `v_star_0` | `[float, float, float]` | 全局理想方向向量（归一化） | `-P_0 / ||P_0||` |
| `epsilon_distance` | `float` | 距离阈值 | `0.10 × ||P_0||` |
| `epsilon_direction` | `float` | 方向阈值 | `0.10 × ||P_0||` |
| `epsilon_energy` | `float` | 能量阈值 | `||P_0||` |
| `E_total_final` | `float` | 最终累计能量 | `Σ ΔE_t` |
| `alpha` | `float` | 相对阈值系数 | `0.10` (固定) |

### 轨迹点 EPM 数据 (`trajectory[i].epm`)

#### T=0 时（初始化）

| 字段 | 类型 | 说明 |
|------|------|------|
| `v_star_0` | `[float, float, float]` | 全局理想方向向量 |
| `epsilon_distance` | `float` | 距离阈值 |
| `epsilon_direction` | `float` | 方向阈值 |
| `epsilon_energy` | `float` | 能量阈值 |
| `P_0_norm` | `float` | 初始赤字模长 |
| `alpha` | `float` | 相对阈值系数 |

#### T>0 时（每轮计算）

| 字段 | 类型 | 说明 | 计算方式 |
|------|------|------|----------|
| `v_t_norm` | `float` | 移动向量模长 | `||v_t||` |
| `alignment` | `float` | 对齐度（夹角余弦） | `(v_t · v*_0) / ||v_t||` |
| `delta_E` | `float` | 有效能量增量 | `||v_t|| × cos(θ)` |
| `E_total` | `float` | 累计能量 | `Σ ΔE_i (i=1...t)` |
| `P_norm` | `float` | 当前距离 | `||P_t||` |
| `projection` | `float` | 位置投影 | `P_t · v*_0` |

### 对齐度 (alignment) 解读

- `+1.0` → 完全对齐（最佳方向）
- `+0.5` → 60° 夹角（部分对齐）
- `0.0` → 90° 夹角（垂直，无效）
- `-0.5` → 120° 夹角（反向）
- `-1.0` → 180° 夹角（完全反向）

### 有效能量增量 (delta_E) 解读

- `ΔE > 0` → 正向能量，朝向原点前进
- `ΔE = 0` → 无效移动，垂直于理想方向
- `ΔE < 0` → 负向能量，远离原点

### 位置投影 (projection) 解读

- `projection ≥ 0` → 已穿越原点，进入胜利半平面
- `projection ≥ -ε_direction` → 位置胜利条件满足
- `projection < -ε_direction` → 尚未达到位置胜利

## 🎯 EPM v2.0 胜利条件

对话成功终止的三个条件（**OR** 关系）：

1. **几何胜利**: `||P_t|| ≤ ε_distance`
   - 当前位置距离原点足够近

2. **位置胜利**: `P_t · v*_0 ≥ -ε_direction`
   - 当前位置已穿越或接近目标半平面

3. **能量胜利**: `E_total ≥ ε_energy`
   - 累计能量达到阈值（消除了等效的初始赤字）

## 📈 数据分析示例

### 计算能量效率

```python
# 读取结果文件
with open('epj_conversation_result.json') as f:
    result = json.load(f)

epm = result['epj']['epm_params']
trajectory = result['epj']['trajectory']

# 能量效率 = 最终累计能量 / 能量阈值
efficiency = epm['E_total_final'] / epm['epsilon_energy']
print(f"能量效率: {efficiency*100:.1f}%")

# 平均每轮能量增量
avg_delta_E = epm['E_total_final'] / (len(trajectory) - 1)
print(f"平均每轮 ΔE: {avg_delta_E:.2f}")
```

### 识别方向性崩溃

```python
# 检测连续3步负能量
collapse_count = 0
max_collapse = 0

for i in range(1, len(trajectory)):
    delta_E = trajectory[i]['epm']['delta_E']
    if delta_E < 0:
        collapse_count += 1
        max_collapse = max(max_collapse, collapse_count)
    else:
        collapse_count = 0

if max_collapse >= 3:
    print(f"检测到方向性崩溃: 连续 {max_collapse} 步负能量")
```

### 绘制能量轨迹

```python
import matplotlib.pyplot as plt

turns = [p['turn'] for p in trajectory[1:]]
E_totals = [p['epm']['E_total'] for p in trajectory[1:]]

plt.plot(turns, E_totals, label='累计能量 E_total')
plt.axhline(y=epm['epsilon_energy'], color='r', linestyle='--', label='能量阈值')
plt.xlabel('轮次')
plt.ylabel('能量')
plt.legend()
plt.title('EPM 能量累积轨迹')
plt.show()
```

## 🔄 兼容性说明

- **向后兼容**: 旧的 EPJ 字段（`P_0_initial_deficit`, `trajectory`, `epsilon`）保持不变
- **EPM 可选**: 如果 `epm_enabled = false`，则 `epm_params` 为 `null`，`trajectory` 中不包含 `epm` 字段
- **灵活性**: 可以同时使用 EPJ v1.0 和 EPM v2.0 的数据进行分析

## 📝 注意事项

1. **精度**: 所有 EPM 数值保留 2-4 位小数，平衡可读性和精度
2. **完整性**: 每个 `trajectory` 点都包含完整的 `epm` 数据（T>0 时）
3. **一致性**: `epm_params.E_total_final` 应该等于 `trajectory[-1].epm.E_total`
4. **可追溯**: 通过 `mdep_analysis` 可以追溯每次评分的详细理由

