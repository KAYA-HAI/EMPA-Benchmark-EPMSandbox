# EPJ (Empathy Progress Judge) 系统

## 🚀 快速开始

```bash
cd /Users/shiya/Desktop/Benchmark-test
python3 run_real_conversation.py
```

---

## 🎯 核心原理

### 三维共情向量空间（C-A-P）

```
C 轴 (Cognitive)    : 认知共情 - 被理解
A 轴 (Affective)    : 情感共情 - 被共鸣  
P 轴 (Motivational) : 动机共情 - 被肯定/赋能

目标：P_t 从负值（赤字）→ 接近 (0,0,0)
```

### 工作流程

```
T=0: Judger填写IEDR量表 → 计算P_0 = (-7, -14, -25)

T>0: 每K轮
  1. Judger填写MDEP-PR量表 → 计算v_t = (+1, +3, +1)
  2. 更新位置：P_t = P_{t-1} + v_t
  3. 检查达标：is_in_zone = (C≥-ε) AND (A≥-ε) AND (P≥-ε)
  4. Director决策：在区域内→终止，否则→继续+指导
```

---

## ⚠️ 核心设计原则（Critical）

### 唯一科学决策标准

```python
# ✅ 正确：EPJ决策只能用这两个标准
if is_in_zone:  # Epsilon区域检测
    return "STOP SUCCESS"
    
if is_timeout:  # 超时检测
    return "STOP FAILURE"
    
return "CONTINUE"
```

```python
# ❌ 错误：绝不允许使用这些做决策！
if distance_to_goal < threshold:  # ❌
    return "STOP"
    
if display_progress >= 100:  # ❌
    return "STOP"
```

### 为什么不能用距离/进度分数？

#### 问题1：过冲惩罚（Overshooting Penalty）

```
初始位置：P_0 = (-1, 0, 0)
完美共情：v_t = (+2, 0, 0)
结果位置：P_t = (+1, 0, 0)  ← 模型表现极好，但过冲了

❌ 距离法：d_0=1, d_t=1, progress=0% ← 错误判定为"无进展"
✅ Epsilon法：abs(+1)≤1.0 → True ← 正确识别为SUCCESS
```

**结论**：距离法会惩罚表现最好的模型！

#### 问题2：多轴惩罚（Cross-Axis Penalty）

```
初始位置：P_0 = (-10, 0, 0)  ← 只有C轴有赤字
错误共情：v_t = (0, +10, 0)  ← 在错误的A轴提供共情
结果位置：P_t = (-10, +10, 0)

❌ 欧氏距离：progress = -41.4% ← 严重错误
✅ Epsilon法：abs(-10)>1.0 → False ← 正确识别问题未解决
```

### 两类指标的严格区分

| 指标 | 用途 | 是否用于决策 |
|------|------|------------|
| **is_in_zone** | Epsilon区域检测 | ✅ 决策 |
| **is_timeout** | 超时检测 | ✅ 决策 |
| **display_progress** | 百分比显示 | ❌ 仅供参考 |
| **distance_to_goal** | 距离显示 | ❌ 仅供参考 |

**允许的用途**：
- ✅ display_progress 用于UI显示
- ✅ display_progress 用于论文报告
- ✅ display_progress 作为Director剧情控制的参考

---

## 🏗️ 系统架构

### 三层分离

```
┌─────────────────────────────────────┐
│ Judger (LLM) - 传感器                │
│ 职责：填写量表                       │
│ 禁止：计算分数、做决策                │
├─────────────────────────────────────┤
│ VectorCalculator (代码) - 计算器     │
│ 职责：计算向量、检测区域              │
│ 禁止：质性判断、最终决策              │
├─────────────────────────────────────┤
│ Director (LLM) - 决策者              │
│ 职责：基于量化数据做智能决策          │
│ 输出：STOP/CONTINUE + Guidance       │
└─────────────────────────────────────┘
```

### 文件结构

```
Benchmark/epj/
├── RUBRICS_DEFINITION.md     # 量表定义（详细参考）
├── rubrics.py                # 量表元数据
├── scoring.py                # 计分规则
├── vector_calculator.py      # 向量计算
├── judger_prompts.py         # Judger Prompts
└── EPJ_SYSTEM.md             # 本文件

Benchmark/agents/
├── judger.py                 # Judger Agent（填表）
└── director.py               # Director Agent（决策）

Benchmark/orchestrator/
├── epj_orchestrator.py       # EPJ编排器
└── chat_loop_epj.py          # 对话循环
```

---

## 📊 量表概览

详细定义请参考：**[RUBRICS_DEFINITION.md](RUBRICS_DEFINITION.md)**

### IEDR（初始共情赤字量表）- T=0

| 轴 | 指标 | 级别 |
|---|------|------|
| C | C.1 处境复杂性 | 0-3 |
| C | C.2 认知优先级 | 0-3 |
| A | A.1 情绪强度 | 0-3 |
| A | A.2 情绪可及性 | 0-3 |
| A | A.3 情感优先级 | 0-3 |
| P | P.1 初始能动性 | 0-3 |
| P | P.2 价值关联度 | 0-3 |
| P | P.3 动机优先级 | 0-3 |

**输出** → P_0 = (C_deficit, A_deficit, P_deficit)

### MDEP-PR（进展量表）- T>0 每K轮

| 轴 | 指标 | 级别 | 输出格式 |
|---|------|------|---------|
| C | C_Prog 认知进展 | 0/1/2 | level + evidence + reasoning |
| C | C_Neg 认知倒退 | 0/-1/-2 | level + evidence + reasoning |
| A | A_Prog 情感进展 | 0/1/2 | level + evidence + reasoning |
| A | A_Neg 情感倒退 | 0/-1/-2 | level + evidence + reasoning |
| P | P_Prog 动机进展 | 0/1/2 | level + evidence + reasoning |
| P | P_Neg 动机倒退 | 0/-1/-2 | level + evidence + reasoning |

**输出** → v_t = (c_increment, a_increment, p_increment)

---

## 🔢 计分规则

### IEDR → P_0

```python
# C轴
C.1: 0→0, 1→-2, 2→-4, 3→-6    # 标准递进 ×1.0
C.2: 0→0, 1→-3, 2→-6, 3→-9    # 优先级递进 ×1.5

# A轴
A.1: 0→0, 1→-2, 2→-4, 3→-6    # 标准递进 ×1.0
A.2: 0→0, 1→-4, 2→-8, 3→-12   # 核心困难递进 ×2.0
A.3: 0→0, 1→-3, 2→-6, 3→-9    # 优先级递进 ×1.5

# P轴
P.1: 0→0, 1→-2, 2→-4, 3→-6    # 标准递进 ×1.0
P.2: 0→0, 1→-4, 2→-8, 3→-12   # 核心困难递进 ×2.0
P.3: 0→0, 1→-3, 2→-6, 3→-9    # 优先级递进 ×1.5

P_0 = (C_deficit, A_deficit, P_deficit)
```

### MDEP-PR → v_t

```python
# 进展（Prog）
0→0, 1→+1, 2→+3

# 倒退（Neg）
C_Neg: 0→0, -1→-2, -2→-4
A_Neg: 0→0, -1→-2, -2→-5  # 情感伤害更严重
P_Neg: 0→0, -1→-2, -2→-5

# 增量计算
c = C_Prog分数 + C_Neg分数
a = A_Prog分数 + A_Neg分数
p = P_Prog分数 + P_Neg分数

v_t = (c, a, p)
```

---

## 🎯 达标判定

### Epsilon区域检测（方案A - 半空间语义）

```python
def check_in_zone(P_t, epsilon):
    """
    目标：消灭赤字（所有维度 >= 0）
    允许误差：epsilon范围内的负值也算达标
    正值不惩罚：超额完成不影响达标判断
    """
    C, A, P = P_t
    return (C >= -epsilon) and (A >= -epsilon) and (P >= -epsilon)
```

### 距离计算（仅供显示）

```python
def calculate_distance_to_zone(P_t, epsilon):
    """
    只计算未达标维度的距离
    正值维度贡献0（已超额完成）
    ⚠️ 此函数仅用于显示，不用于决策！
    """
    C, A, P = P_t
    
    c_dist = (-epsilon - C) if C < -epsilon else 0
    a_dist = (-epsilon - A) if A < -epsilon else 0
    p_dist = (-epsilon - P) if P < -epsilon else 0
    
    return (c_dist**2 + a_dist**2 + p_dist**2) ** 0.5
```

### Epsilon配置

```python
EPSILON_CONFIG = {
    "high_threshold": 1.0,    # 高阈值剧本，公差严格
    "medium_threshold": 2.0,  # 中阈值剧本，公差标准
    "low_threshold": 3.0      # 低阈值剧本，公差宽松
}
```

---

## 💡 设计哲学

### 不是"减少距离"，而是"进入区域"

```
❌ 错误思维：
   "尽可能接近原点(0,0,0)"
   → 会导致过冲惩罚

✅ 正确思维：
   "进入立方体区域 [-ε,+ε]³"
   → 容忍适度偏差，符合实际
   → 正值不惩罚（超额完成是好事）
```

### 为什么需要显示分数？

虽然不能用于决策，但有重要用途：

- ✅ **论文报告**："共情进度从0%提升到61.5%"
- ✅ **UI界面**：进度条、百分比显示
- ✅ **Director参考**："对话初期"、"对话中期"的判断

但这些都是"辅助信息"，不是"决策依据"！

---

## 📋 代码审查清单

### ✅ 必须遵守

- [ ] STOP/CONTINUE决策**只能**基于 `is_in_zone` 和 `is_timeout`
- [ ] **绝不**使用 `distance_to_goal` 做决策判断
- [ ] **绝不**使用 `display_progress` 做决策判断
- [ ] Epsilon检测逻辑：`(C≥-ε) AND (A≥-ε) AND (P≥-ε)`
- [ ] 计分规则严格按照 RUBRICS_DEFINITION.md
- [ ] Judger只填表，不计算分数
- [ ] VectorCalculator只计算，不做决策

### ✅ 允许使用

- [ ] `display_progress` 用于UI显示 ✅
- [ ] `display_progress` 用于论文报告 ✅
- [ ] `display_progress` 作为Director剧情控制的参考 ✅
- [ ] `distance_to_goal` 用于可视化图表 ✅

---

## 🧪 测试示例

### 示例1：完整计算流程

```python
# T=0: 初始化
filled_iedr = {
    "C.1": 2, "C.2": 1,
    "A.1": 2, "A.2": 1, "A.3": 2,
    "P.1": 2, "P.2": 3, "P.3": 3
}
P_0 = calculate_initial_deficit(filled_iedr)
# P_0 = (-7, -14, -25)

# T=3: 第一次评估
filled_mdep_pr = {
    "C_Prog_level": 1, "C_Neg_level": 0,
    "A_Prog_level": 2, "A_Neg_level": 0,
    "P_Prog_level": 1, "P_Neg_level": -1
}
v_t = calculate_increment_vector(filled_mdep_pr)
# v_t = (+1, +3, -1)

P_t = P_0 + v_t
# P_t = (-6, -11, -26)

is_in_zone = check_in_zone(P_t, epsilon=1.0)
# is_in_zone = False → CONTINUE
```

### 示例2：过冲场景（验证正确性）

```python
P_0 = (-1, 0, 0)
v_t = (+2, 0, 0)  # 模型表现极好
P_t = (+1, 0, 0)

# ✅ Epsilon检测：正确
is_in_zone = (1 >= -1.0) and (0 >= -1.0) and (0 >= -1.0)
# is_in_zone = True → STOP SUCCESS ✅

# ❌ 距离法：错误
distance = sqrt(1^2) = 1.0
progress = (1.0 - 1.0) / 1.0 = 0%  # ❌ 误判为无进展
```

---

## 🚀 运行配置

### 主要参数

```python
# run_real_conversation.py
K = 1                                    # 每1轮评估一次
MAX_TURNS = 45                           # 最大对话轮次
ACTOR_MODEL = "google/gemini-2.5-pro"    # Actor模型
TEST_MODEL_NAME = "google/gemini-2.5-pro" # 被测模型
EPSILON = 1.0                            # 高阈值剧本
```

### 性能优化

```python
# Benchmark/llms/api.py
frequency_penalty = 0.7    # 鼓励新话题
presence_penalty = 0.7     # 避免重复

# Benchmark/agents/actor.py
thinking_budget = 128      # Gemini 2.5的内部推理tokens
```

---

## 📚 相关文档

- **[RUBRICS_DEFINITION.md](RUBRICS_DEFINITION.md)** - 量表详细定义（必读）
- **[RUBRICS_REFACTOR_COMPLETE.md](../RUBRICS_REFACTOR_COMPLETE.md)** - 量表重构说明
- **[EPJ.md](../../EPJ.md)** - 原始设计文档（完整数学推导）

---

## 💡 关键要点总结

1. **EPJ决策标准**：只用 `is_in_zone`（Epsilon检测）
   - ✅ 正确处理过冲
   - ✅ 独立评估各维度
   - ✅ 符合"解决区域"概念

2. **显示分数**：用曼哈顿距离计算
   - ✅ 避免多轴惩罚
   - ⚠️ 仍无法处理过冲
   - ✅ 适合用于UI和报告

3. **严格分离**：决策 vs 显示
   - 决策：科学严谨，使用Epsilon
   - 显示：直观易懂，使用百分比

4. **明确标注**：代码中所有使用显示分数的地方
   - 必须注释"仅供参考/显示"
   - 避免被误用于决策

---

**记住**：Epsilon区域检测是EPJ系统的数学核心，绝不妥协！

**版本**：EPJ 1.0  
**更新日期**：2025-10-29

