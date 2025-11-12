# EPM指标计算流程（每轮对话）

## 📊 完整调用链

```
chat_loop_epj.py (对话循环)
    ↓
    每K轮触发EPJ评估
    ↓
epj_orchestrator.py::evaluate_at_turn_K()
    ↓
    步骤1: Judger填表
    ↓
    步骤2: VectorCalculator计算v_t和EPM指标 ⭐
    ↓
    步骤3: 生成state_packet
    ↓
    步骤4: 创建epm_summary
    ↓
    返回给Director和chat_loop
```

---

## ⭐ 核心计算位置

### 1. **EPM指标计算** - `VectorCalculator.calculate_v_t_and_update()`

**文件**: `Benchmark/epj/vector_calculator.py`  
**行数**: 217-254

```python
# 每轮K都会执行
def calculate_v_t_and_update(self, filled_mdep_pr: Dict, current_turn: int):
    # ... 基础EPJ计算 ...
    
    # EPM v2.0 能量动力学计算
    if self.enable_epm and self.v_star_0 is not None:
        # 1. 计算向量模长
        v_t_norm = self._calculate_vector_norm(v_t)
        
        # 2. 计算对齐度（夹角余弦）
        if v_t_norm > 0:
            alignment = self._calculate_dot_product(v_t, self.v_star_0) / v_t_norm
        else:
            alignment = 0.0
        
        # 3. 计算有效能量增量（投影功）
        delta_E = v_t_norm * alignment
        
        # 4. 累计能量
        self.E_total += delta_E
        
        # 5. 计算当前位置的投影
        P_t_norm = self._calculate_vector_norm(P_t)
        projection = self._calculate_dot_product(P_t, self.v_star_0)
        
        # 6. 添加EPM字段到轨迹点
        trajectory_point['epm'] = {
            "v_t_norm": round(v_t_norm, 2),         # 移动模长
            "alignment": round(alignment, 4),        # 方向对齐度 ⭐
            "delta_E": round(delta_E, 2),           # 有效能量增量 ⭐
            "E_total": round(self.E_total, 2),      # 累计能量 ⭐
            "P_norm": round(P_t_norm, 2),           # 当前距离
            "projection": round(projection, 2)       # 位置投影
        }
```

**关键计算公式**:
- `alignment = (v_t · v*_0) / ||v_t||`  ← 对齐度（余弦相似度）
- `ΔE_t = ||v_t|| × alignment`  ← 有效能量增量（标量投影）
- `E_total += ΔE_t`  ← 累计能量（状态变量）

---

### 2. **EPM摘要生成** - `epj_orchestrator.evaluate_at_turn_K()`

**文件**: `Benchmark/orchestrator/epj_orchestrator.py`  
**行数**: 234-259

```python
# EPM v2.0: 添加能量动力学摘要
if self.enable_epm and self.calculator.v_star_0 is not None:
    from Benchmark.epj.scoring import get_epm_state_summary
    
    # 获取最新的EPM指标
    latest_trajectory = self.calculator.trajectory[-1]
    if 'epm' in latest_trajectory:
        epm_data = latest_trajectory['epm']
        
        epm_summary = get_epm_state_summary(
            current_turn=current_turn,
            r_t=epm_data['P_norm'],              # 从trajectory提取
            projection=epm_data['projection'],    # 从trajectory提取
            E_total=epm_data['E_total'],         # 从trajectory提取
            epsilon_distance=self.calculator.epsilon_distance_relative,
            epsilon_direction=self.calculator.epsilon_direction_relative,
            epsilon_energy=self.calculator.epsilon_energy,
            trajectory=self.calculator.trajectory
        )
        
        state_packet['epm_summary'] = epm_summary  # 传递给Director
```

---

### 3. **EPM判停检测** - `chat_loop_epj.py`

**文件**: `Benchmark/orchestrator/chat_loop_epj.py`  
**行数**: 186-214

```python
# 🆕 EPM v2.0: 检查能量动力学判停
if 'epm_summary' in state_packet and state_packet['epm_summary']['success']:
    epm_summary = state_packet['epm_summary']
    epm_stop_triggered = True
    
    print(f"\n🎉 [EPM v2.0] 检测到胜利条件!")
    print(f"   胜利类型: {epm_summary['victory_type']}")
    print(f"   指标: E_total={epm_summary['metrics']['E_total']}, "
          f"r_t={epm_summary['metrics']['r_t']}, "
          f"projection={epm_summary['metrics']['projection']}")
    
    # EPM成功时，自动触发停机
    should_continue = False
    termination_type = f"EPM_SUCCESS_{epm_summary['victory_type'].upper()}"
```

---

## 🔄 数据流动路径

### 输入 → 计算 → 输出

```
输入:
  - filled_mdep_pr (Judger评分)
  - P_{t-1} (上一轮位置)
  - v*_0 (理想方向，初始化时计算)

↓ 计算 (VectorCalculator)

EPM指标:
  - v_t_norm = ||v_t||
  - alignment = cos(θ) = (v_t · v*_0) / ||v_t||
  - delta_E = ||v_t|| × alignment
  - E_total += delta_E
  - P_t_norm = ||P_t||
  - projection = P_t · v*_0

↓ 封装 (epj_orchestrator)

state_packet = {
    "trajectory": [...],  # 包含每轮的epm字段
    "epm_summary": {
        "metrics": {r_t, projection, E_total},
        "thresholds": {ε_distance, ε_direction, ε_energy},
        "progress": {geometric%, positional%, energetic%},
        "success": bool,
        "victory_type": str,
        "collapsed": bool
    }
}

↓ 传递给Director

director_prompts.py:
  - 显示最新一轮的 alignment、delta_E
  - 显示累计的 E_total
  - 显示位置状态 r_t、projection
  - 显示胜利条件检查结果
```

---

## 📍 数据存储位置

### 1. **实时状态** (VectorCalculator)
```python
self.E_total        # 累计能量（状态变量）
self.v_star_0       # 理想方向（初始化后不变）
self.trajectory     # 完整轨迹（每个点包含epm字段）
```

### 2. **每轮快照** (trajectory点)
```python
trajectory_point = {
    "turn": t,
    "P_t": (C, A, P),
    "v_t": (c, a, p),
    "epm": {
        "v_t_norm": ...,
        "alignment": ...,    # ⭐ Director需要
        "delta_E": ...,      # ⭐ Director需要
        "E_total": ...,      # ⭐ Director需要
        "P_norm": ...,
        "projection": ...
    }
}
```

### 3. **摘要数据** (state_packet)
```python
state_packet['epm_summary'] = {
    "metrics": {...},
    "thresholds": {...},
    "progress": {...},
    "success": bool,
    "victory_type": str
}
```

---

## ⏱️ 计算时机

### 初始化（T=0）
- 计算 `P_0`
- 计算 `v*_0 = -P_0 / ||P_0||`
- 设置 `E_total = 0`

### 每K轮（T=K, 2K, 3K, ...）
1. Judger填写MDEP-PR → 得到v_t
2. **VectorCalculator计算EPM指标** ← 主计算点 ⭐
3. 更新 `E_total += delta_E`
4. 保存到 `trajectory`
5. 生成 `epm_summary`
6. 检查胜利条件

---

## 🎯 关键要点

1. **单一计算点**: EPM指标只在 `VectorCalculator.calculate_v_t_and_update()` 中计算
2. **状态累积**: `E_total` 是类属性，每轮累加，贯穿整个对话
3. **数据传递**: 通过 `trajectory` 和 `state_packet` 传递给Director
4. **向后兼容**: EPM计算是可选的（`enable_epm`标志），不影响EPJ v1.0

---

## 📊 示例输出

```
🆕 [EPM v2.0] 能量动力学分析
   移动模长 ||v_t|| = 4.12
   对齐度 cos(θ) = 0.873 (正向)
   有效能量增量 ΔE = +3.59
   累计能量 E_total = 18.67 / 31.97 (58.4%)
   当前距离 ||P_t|| = 15.32
   位置投影 P_t·v*_0 = -8.45 (未穿越)
```

