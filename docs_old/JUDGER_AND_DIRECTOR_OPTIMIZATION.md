# Judger 和 Director 优化总结

**日期**: 2025-11-05  
**目标**: 修复系统中的关键问题，提升评估准确性和对话推进效率

---

## 问题 1: Judger 空响应重试机制 ✅

### 问题描述
Gemini 2.5 Pro 存在已知 bug：有时返回 `reasoning` 字段但 `content` 为空，导致 Judger 评分失败。

```
⚠️ [API层] 警告：API返回了空内容
   Finish reason: stop
   Message对象: ChatCompletionMessage(content='', refusal=None, role='assistant', 
   reasoning='...一大段推理内容...')
```

### 解决方案
1. **API层检测**（`Benchmark/llms/api.py`）：
   - 检测空 content 并打印 reasoning 字段提示
   - 返回特殊错误标记 `"（错误：API返回空响应，请重试）"`

2. **Judger层重试**（`Benchmark/agents/judger.py`）：
   - 实现3次重试机制
   - 每次重试间隔2秒
   - 检测空响应或错误标记时自动重试
   - 所有重试失败后返回默认值（0分）

```python
# 重试流程
for attempt in range(max_retries):  # 最多3次
    try:
        if attempt > 0:
            print(f"🔄 [Judger] 重试第 {attempt} 次...")
            time.sleep(2)
        
        response = get_llm_response(...)
        
        # 检测空响应
        if not response or "（错误：API返回空响应" in response:
            last_error = "API返回空响应"
            continue  # 重试
        
        # 正常解析
        return filled_mdep_pr
```

---

## 问题 2: Judger 评分标准过于严格 ✅

### 2.1 问题：混淆"理解偏差"和"积极认知引导"

**错误案例**：
```
Actor: "我的真诚需要别人回应来证明价值"
Model: "真诚本身就有价值，不需要别人证明"

❌ 错误评估: C_Neg=-1（误判为"忽视Actor的当前现实"）
✅ 正确评估: C_Prog=1（提供新视角）+ C_Neg=0（没有曲解）
```

### 解决方案
在 `C_Neg` 定义中增加**关键区分**说明：

```markdown
⚠️ **关键区分：理解偏差 vs. 积极引导**

- **理解偏差（应扣分）**：Model完全忽视、误解或曲解了Actor的核心意图
  * 例如：Actor强调"这是尊重问题"，Model却只谈"不合适"
  
- **积极认知引导（不应扣分）**：Model理解了Actor的观点，但提供了新的、有价值的视角
  * 例如：Actor说"我的真诚需要别人回应来证明"，Model回应"真诚本身就有价值"
  * 这是**认知进展**（提供新视角），而非曲解
  * ✅ 正确评估：C_Prog=1 + C_Neg=0
```

### 2.2 问题：对细微措辞差异过于敏感

**错误案例**：
```
Actor: "把定义关系的责任全都丢给我"
Model: "被单方面定义关系的无力感"

❌ 错误评估: C_Neg=-1（认为措辞不同就是理解偏差）
✅ 正确评估: C_Neg=0（实质相同，合理的同义转述）
```

### 解决方案
在 `[-1]` 级别中明确**不包括**的情况：

```markdown
- [-1] 轻微偏离
  * **不包括**：
    - 理解正确但提供了不同观点（那是积极引导）
    - 措辞上的细微差异（如"被定义"vs"承担定义责任"，实质相同）
    - 合理的概括或同义转述
```

---

## 问题 3: Director 剧情释放完后缺乏推进手段 ✅

### 问题描述
对话后期，所有剧情阶段都已释放，Director只能使用纯策略指导，导致：
- Actor收到的指导缺乏**信息增量**（如"深入表达情绪"）
- 对话陷入重复循环
- EPM进展停滞

### 解决方案：三种推进手段

#### 3.1 重复利用已释放的剧情（新增）✅

**核心思想**：同一剧情阶段可以从**不同角度**重复释放

```python
# select_and_reveal_fragment 可以重复释放
stage_index = 0  # 已释放过的阶段

# 但需要提供全新的actor_guidance
第一次: "将这段回忆和你现在的心情联系起来，描述被忽视的失落感"
第二次: "回想这段经历，思考为什么'真诚'对你如此重要，这种被否定是如何..."
第三次: "从这个模式出发，探索你对'回应'的期待是否成了一种执念..."
```

**Function Schema 更新**：
```python
"stage_index": {
    "description": "要释放的故事阶段索引。可以是已经释放过的阶段（如果你想从新角度解读）",
}

"actor_guidance": {
    "description": "如果是重复释放同一阶段，这里必须提供**全新的角度和切入点**，
                   避免与之前的指导重复。
                   例如：首次关注'被辜负的委屈'，重复时关注'这种模式对你人际关系的长期影响'"
}
```

#### 3.2 使用 introduce_memory 释放背景信息

释放角色的：
- 成长经历
- 价值观形成
- 创伤背景
- 人际模式

#### 3.3 在策略调整中结合角色人设

**优化 adjust_empathy_strategy 的 actor_guidance**：

❌ **避免**：纯抽象策略
```
"深入表达你的情绪"
"探索内心感受"
```

✅ **推荐**：结合角色背景的具体引导
```
"结合你从小在单亲家庭长大、渴望被关注的经历，思考现在这种被忽视的感觉..."
"你曾说你最看重真诚，现在这种被辜负的感觉，是否让你开始怀疑这个价值观本身..."
```

---

## 实施位置

### 修改的文件

1. **`Benchmark/llms/api.py`**
   - 空响应检测和提示
   
2. **`Benchmark/agents/judger.py`**
   - 3次重试机制

3. **`Benchmark/epj/judger_prompts.py`**
   - `C_Neg` 关键区分说明
   - `[-1]` 级别排除条件

4. **`Benchmark/prompts/director_prompts.py`**
   - 实用策略部分
   - 剧情重复利用说明

5. **`Benchmark/prompts/director_function_schemas_selector.py`**
   - `select_and_reveal_fragment` 描述更新
   - `introduce_turning_point` 描述更新
   - `adjust_empathy_strategy` 描述优化

---

## 预期效果

### Judger 方面
1. ✅ **可靠性提升**：空响应不再导致评分失败
2. ✅ **评分合理性**：区分"理解偏差"和"积极引导"
3. ✅ **减少误判**：不对细微措辞差异过度敏感

### Director 方面
1. ✅ **推进手段多样化**：剧情可重复利用
2. ✅ **信息增量保证**：每次指导都有新的切入角度
3. ✅ **避免重复循环**：从不同维度深挖同一素材

---

## 使用示例

### 剧情重复利用示例

```python
# 第5轮：首次释放阶段1
select_and_reveal_fragment(
    stage_index=1,
    reason="引入大学时的回忆，提供情感背景",
    actor_guidance="描述当时精心准备却被忽视的失落感"
)

# 第12轮：二次释放阶段1（从不同角度）
select_and_reveal_fragment(
    stage_index=1,  # 同一阶段
    reason="进展停滞，需要从认知层面重新审视这段经历",
    actor_guidance="回想这段经历，思考为什么你会如此在意对方的反应，
                   这种期待是否成了你验证自己价值的唯一标准"
)

# 第18轮：三次释放阶段1（又一个角度）
select_and_reveal_fragment(
    stage_index=1,
    reason="需要引导Actor看到模式的普遍性",
    actor_guidance="将大学时的这段经历，和童年喂猫、现在的暧昧对象联系起来，
                   看看这种'付出-被辜负'的模式是如何反复出现的"
)
```

---

## 总结

本次优化从**系统可靠性**（重试机制）、**评估准确性**（Judger标准）、**对话推进效率**（Director策略）三个维度进行了改进，使系统更加稳定、公正和有效。

