# Director 文件关系分析

## 🔍 问题

用户发现 `director.py` 和 `director_prompts.py` 很像，询问它们的关系。

---

## 📊 文件对比

### director.py (875行)

**职责**: Director类的实现（代码逻辑）

**主要内容**:
1. Director类定义 (20个方法)
2. 剧情控制逻辑 (`evaluate_continuation()`)
3. 9个Function Handlers (处理LLM调用的函数)
4. EPJ决策逻辑 (`make_epj_decision()`)
5. 向量分析逻辑 (`_generate_guidance_from_vector()`)

**关键方法**:
```python
class Director:
    def evaluate_continuation(history, epj_state) -> dict:
        """调用LLM，获取决策"""
        prompt = generate_director_prompt(...)  # 调用prompts.py
        response = get_llm_response(prompt)
        return self._process_function_call_response(response)
    
    def make_epj_decision(state_packet) -> dict:
        """EPJ终止决策"""
        # 分析向量，生成给Actor的指导
        guidance = self._generate_guidance_from_vector(v_t, P_t, distance)
        return {"decision": "CONTINUE", "guidance": guidance}
```

---

### director_prompts.py (241行)

**职责**: 生成Director LLM的prompt（文本生成）

**主要内容**:
1. DIRECTOR_PROMPT_TEMPLATE (模板)
2. generate_director_prompt() (唯一的公开函数)

**关键函数**:
```python
def generate_director_prompt(epj_state, history, ...) -> str:
    """生成Director LLM看到的prompt"""
    
    # 1. 格式化历史对话
    # 2. 格式化故事阶段信息
    # 3. 格式化Actor画像信息
    # 4. 生成EPJ向量信息（如果有）
    # 5. 生成决策指南
    
    return 完整的prompt字符串
```

---

## 🤔 它们的相似之处

### 相似点1: 都处理EPJ向量

**director_prompts.py** (第131-153行):
```python
# 解析向量（使用共享工具）
from Benchmark.epj.vector_utils import parse_vector_string

P_0_vec = parse_vector_string(P_0)
P_t_vec = parse_vector_string(P_t)
v_t_vec = parse_vector_string(v_t)

# 生成进度信息（EPJ向量）
progress_info = f"""
当前共情状态（EPJ三维向量）:
  • 起点赤字 P_0: {P_0}
  • 当前位置 P_t: {P_t}
  • 最近进展 v_t: {v_t}
  ...
"""
```

**director.py** (第787-875行):
```python
def _parse_vector_string(self, vector_str: str) -> Tuple[int, int, int]:
    from Benchmark.epj.vector_utils import parse_vector_string
    return parse_vector_string(vector_str)

def _generate_guidance_from_vector(self, v_t, P_t_str, distance) -> str:
    c, a, p = v_t
    
    # 分析各维度
    if c < -1:
        guidance_parts.append("在认知层面，...")
    elif c >= 2:
        guidance_parts.append("在认知层面，...")
    ...
    
    return guidance
```

---

### 相似点2: 都生成"决策指南"

**director_prompts.py** (第159-199行):
```python
# 生成基于向量的决策指南（给Director LLM看）
decision_guidelines = f"""
### 基于EPJ向量的剧情控制策略

**根据v_t（最近进展）判断：**

1. **v_t全面正向** (如 v_t=(+2,+3,+2))：
   - 说明：AI在三个维度都提供了良好共情
   - 策略：可以深入剧情，释放中后期阶段或引入转折
   ...

**根据P_t（当前位置）判断：**
...
"""
```

**director.py** (第800-875行):
```python
# 生成基于向量的指导（给Actor看）
def _generate_guidance_from_vector(v_t, P_t_str, distance):
    """
    根据EPJ文档的建议：
    - 如果v_t有强烈负值 → 表达失望
    - 如果v_t有强烈正值 → 表达喜悦/被肯定
    ...
    """
    
    guidance = f"""
【EPJ指导】根据共情向量分析：
当前位置：{P_t_str}
本轮增量：c={c}, a={a}, p={p}
具体指导：
...
    """
    return guidance
```

---

## ⚠️ 核心问题

### 问题: 职责重叠

两个文件都在做"基于向量生成文本指导"的工作：

| 文件 | 职责 | 目标受众 | 内容性质 |
|------|------|----------|----------|
| director_prompts.py | 生成prompt | **Director LLM** | 决策指南（教Director如何思考） |
| director.py | 生成guidance | **Actor** | 具体指导（告诉Actor怎么做） |

**看起来不同，但本质相似**：
- 都是"基于向量分析生成文本"
- 都包含C轴、A轴、P轴的判断逻辑
- 都根据v_t和P_t的值给出建议

---

## 💡 为什么会这样？

### 原因: 两个不同的使用场景

#### 场景1: Director的剧情控制（每轮）

```
chat_loop_epj.py
    ↓
director.evaluate_continuation(epj_state)
    ↓
generate_director_prompt(epj_state)  ← 使用 director_prompts.py
    ↓
Director LLM 看到EPJ向量信息和决策指南
    ↓
Director LLM 调用函数 (如 select_and_reveal_fragment)
    ↓
返回给Actor的剧情指导
```

**目的**: 让Director LLM基于EPJ状态选择剧情动作

---

#### 场景2: EPJ终止决策（每K轮）

```
chat_loop_epj.py
    ↓
director.make_epj_decision(state_packet)  ← 使用 director.py
    ↓
_parse_vector_string(v_t)
    ↓
_generate_guidance_from_vector(v_t, P_t, distance)
    ↓
返回给Actor的EPJ反馈指导
```

**目的**: 基于EPJ向量生成给Actor的反馈指导（不通过LLM）

---

## 🎯 本质区别

### director_prompts.py

**性质**: Prompt工程（文本模板）

**作用**: 
- 生成给**Director LLM**看的prompt
- 包含"如何思考"的指南
- 是LLM的**输入**

**示例内容**:
```
根据v_t判断：
1. v_t全面正向 → 策略：可以深入剧情
2. v_t某轴≤0 → 策略：调整策略
```

**受众**: Director LLM（教它如何决策）

---

### director.py

**性质**: 代码逻辑（Python函数）

**作用**:
- Director类的实现
- `_generate_guidance_from_vector()` 生成给**Actor**的指导
- 是EPJ决策的**输出**

**示例内容**:
```python
if c >= 2:
    guidance = "在认知层面，对方理解了你，你可以表达被理解的感觉"
```

**受众**: Actor（告诉它怎么表演）

---

## ✅ 它们应该分开吗？

### 答案: 是的，应该分开！

虽然看起来相似，但它们的职责完全不同：

| 维度 | director_prompts.py | director.py |
|------|---------------------|-------------|
| **文件类型** | Prompt模板 | 代码逻辑 |
| **输出对象** | Director LLM的prompt | Actor的guidance |
| **调用时机** | 每轮（剧情控制） | 每K轮（EPJ决策） |
| **内容来源** | 静态模板+动态数据 | 代码逻辑+向量分析 |
| **是否调用LLM** | 是（生成prompt后调LLM） | 否（直接生成文本） |

---

## 📐 正确的架构

```
┌──────────────────────────────────────────────────────────────┐
│  director_prompts.py (Prompt工程)                             │
├──────────────────────────────────────────────────────────────┤
│  generate_director_prompt(epj_state)                          │
│     ↓                                                         │
│  返回: "你是导演...当前EPJ状态是...请根据v_t判断..."         │
│     ↓                                                         │
│  Director LLM 接收这个prompt                                 │
│     ↓                                                         │
│  Director LLM 决定: 调用 select_and_reveal_fragment(stage=2) │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  director.py (代码逻辑)                                       │
├──────────────────────────────────────────────────────────────┤
│  make_epj_decision(state_packet)                              │
│     ↓                                                         │
│  _generate_guidance_from_vector(v_t)                          │
│     ↓                                                         │
│  返回: {"guidance": "在认知层面，对方理解了你..."}            │
│     ↓                                                         │
│  Actor 接收这个guidance                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## ⚠️ 但是有问题

### 问题: `_generate_guidance_from_vector()` 应该在哪里？

**当前位置**: director.py (第800-875行)

**问题**:
1. 这是一个"文本生成"函数，更像是prompt工程
2. 它包含了硬编码的决策规则
3. 它与 director_prompts.py 的决策指南有重复的逻辑

**两处重复的逻辑**:

**director_prompts.py** (给Director LLM的指南):
```
v_t某轴≤0 → 策略：针对性释放该轴相关的记忆或调整策略
示例：
  * C轴≤0 → 释放记忆帮助理解
  * A轴≤0 → 释放情感记忆
  * P轴≤0 → 释放动机相关记忆
```

**director.py** (给Actor的指导):
```python
if c < -1:
    guidance_parts.append("在认知层面，对方似乎误解了你...")
if a < -2:
    guidance_parts.append("在情感层面，对方的回应让你感到...")
if p < -2:
    guidance_parts.append("在动机层面，对方削弱了你的能动性...")
```

---

## 💡 优化建议

### 方案A: 移动 `_generate_guidance_from_vector()` 到 prompts.py

**理由**:
- 它是文本生成函数
- 它包含决策规则（类似prompt中的决策指南）
- director.py应该专注于"调用LLM"和"处理响应"

**实现**:
```python
# director_prompts.py
def generate_epj_guidance(v_t, P_t, distance) -> str:
    """基于EPJ向量生成给Actor的指导"""
    # 移动原来的逻辑
    ...

# director.py
def make_epj_decision(state_packet, history):
    from Benchmark.prompts.director_prompts import generate_epj_guidance
    guidance = generate_epj_guidance(v_t_values, P_t, distance)
    ...
```

---

### 方案B: 保持现状（推荐）

**理由**:
- 虽然相似，但职责确实不同
- director_prompts.py: 给Director LLM的"教学指南"
- director.py: 给Actor的"执行指导"
- 两者的受众和目的不同

**但需要明确文档**:
- 在两个文件顶部添加清晰的职责说明
- 说明为什么它们看起来相似但应该分开

---

## 📚 推荐的文档说明

### director.py 顶部应添加:

```python
"""
Director Agent - 剧情控制和EPJ决策

职责划分：
1. 剧情控制 (evaluate_continuation):
   - 调用 director_prompts.py 生成prompt
   - 调用 LLM 获取决策
   - 处理 LLM 返回的函数调用
   - 执行具体的剧情动作

2. EPJ终止决策 (make_epj_decision):
   - 基于EPJ向量直接判断STOP/CONTINUE
   - 生成给Actor的反馈指导（不调用LLM）
   - 用于每K轮的终止检查

相关文件：
- director_prompts.py: 生成Director LLM的prompt
- director_function_schemas_selector.py: 定义可用的函数
"""
```

---

### director_prompts.py 顶部应添加:

```python
"""
Director Prompt Generator - 为Director LLM生成prompt

职责：
生成Director LLM看到的prompt，包含：
1. 角色信息和可用函数说明
2. 对话历史和EPJ向量状态
3. 基于向量的决策指南（教Director如何思考）
4. 可用的故事阶段和角色画像

注意：
- 此文件生成的是"输入"给Director LLM的文本
- director.py 处理LLM的响应并执行具体动作
- 虽然都涉及EPJ向量分析，但受众不同（LLM vs Actor）
"""
```

---

## ✅ 总结

### 关系说明

```
director_prompts.py (文本工程)
    ↓ 生成prompt
Director LLM (智能决策)
    ↓ 返回function call
director.py (代码逻辑)
    ↓ 执行function
Actor (接收指导)
```

### 为什么看起来相似？

因为它们都涉及"EPJ向量分析"：
- **director_prompts.py**: 教Director LLM**如何分析**
- **director.py**: **直接分析**并输出结果

### 是否需要合并？

**不需要**，因为：
1. ✅ 职责不同（prompt生成 vs 代码逻辑）
2. ✅ 受众不同（Director LLM vs Actor）
3. ✅ 时机不同（每轮 vs 每K轮）

### 需要改进什么？

1. ✅ 添加清晰的文档说明（避免混淆）
2. ✅ 明确两者的分工和协作关系
3. ✅ 保持代码简洁和职责单一

---

**分析日期**: 2025-10-27  
**结论**: ✅ 应该分开，但需要更清晰的文档

