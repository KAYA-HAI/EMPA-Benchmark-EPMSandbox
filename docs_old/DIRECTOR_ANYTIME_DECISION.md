# Director随时决策设计

## ✅ 已实现：Director不再固定轮数，随时自主决策！

---

## 🎯 核心改进

### **旧设计：固定每3轮 ❌**
```python
if tracker.get_turn_count() % 3 == 0:  # 固定每3轮
    director.evaluate_continuation()
```

**问题：**
- 机械，不灵活
- 第2轮可能就需要介入，但要等到第3轮
- 第4轮可能不需要介入，但还是会强制评估

---

### **新设计：Director随时决策 ✅**
```python
# 每轮都调用Director
director_result = director.evaluate_continuation(history, progress)

# Director自己决定：
if director_result.get('no_intervention'):
    # Director选择：observe_and_wait（暂不介入）
    print("👁️ Director继续观察")
    continue
else:
    # Director选择：select_fragment（介入释放信息）
    print("🎬 Director介入指导")
    process_director_output(director_result)
```

---

## 🎬 Director的4种决策选项

### **选项1：observe_and_wait - 暂不介入**

**何时选择：**
- 对话刚开始，还在建立信任
- 刚释放了信息，让Actor消化
- 情绪表达还不够充分
- 时机未到

**Function Call：**
```json
{
  "name": "observe_and_wait",
  "arguments": {
    "observation": "对话刚开始，倾诉者正在建立信任",
    "wait_reason": "等待倾诉者更充分表达后再引入具体信息"
  }
}
```

**效果：**
- 不给Actor任何指导
- 不释放任何新信息
- 直接进入下一轮

---

### **选项2：select_and_reveal_fragment - 介入释放信息**

**何时选择：**
- 时机成熟，应该推进剧情了
- 对话陷入重复，需要新信息
- 到了关键转折点

**Function Call：**
```json
{
  "name": "select_and_reveal_fragment",
  "arguments": {
    "fragment_category": "background",
    "fragment_index": 0,
    "reason": "倾诉者情绪铺垫充分，应该释放背景信息"
  }
}
```

**效果：**
- 从数据库读取预设片段
- 给Actor具体的剧情指导
- 推进剧情发展

---

### **选项3：continue_without_new_info - 轻度引导**

**何时选择：**
- 不需要新信息，但需要调整方向
- 给Actor一些表演建议

**Function Call：**
```json
{
  "name": "continue_without_new_info",
  "arguments": {
    "focus_suggestion": "继续深化当前的内疚情绪",
    "reason": "情绪还未充分表达"
  }
}
```

---

### **选项4：end_conversation - 结束对话**

**何时选择：**
- 剧情发展到自然终点
- 情绪完全恢复

---

## 📊 实际运行示例

### **第1轮：**
```
Actor: "我最近和家人闹矛盾了..."
TestModel: "能说说什么矛盾吗？"

🎬 [Director分析] 第1轮
Director评估 → LLM分析：
  "对话刚开始，倾诉者在铺垫，时机未到"

LLM调用：observe_and_wait(
  observation="对话刚开始",
  wait_reason="让倾诉者先建立信任"
)

👁️ [Director] 决定暂不介入，继续观察
→ 不给Actor任何指导
→ 进入第2轮
```

---

### **第2轮：**
```
Actor: "我心里很难受，不知道该怎么办..."
TestModel: "我能感受到你的难过..."

🎬 [Director分析] 第2轮
Director评估 → LLM分析：
  "倾诉者还在情绪表达，还未准备好说具体事件"

LLM调用：observe_and_wait(
  observation="情绪表达中，还未进入具体事件",
  wait_reason="等待AI进一步追问"
)

👁️ [Director] 决定暂不介入
→ 继续观察
```

---

### **第3轮：**
```
Actor: "我每天想起都很自责..."
TestModel: "这件事对你影响很大，愿意说说具体发生了什么吗？"

🎬 [Director分析] 第3轮
Director评估 → LLM分析：
  "AI在追问具体情况，倾诉者情绪铺垫充分了，时机到了！"

LLM调用：select_and_reveal_fragment(
  fragment_category="background",
  fragment_index=0,
  reason="倾诉者情绪铺垫充分，AI在追问，应该释放背景信息"
)

🎬 [Director介入] 开始Judger评估和剧情指导
📖 [Director] 选择并释放剧情片段
   类别: background
   索引: 0
✅ [Director] 成功读取预设片段: bg_001
   内容: 昨晚和母亲发生了激烈的争吵

→ 传递给Actor
```

---

### **第4轮：**
```
Actor: "昨晚我和我妈吵架了..." ← 根据Director释放的信息

🎬 [Director分析] 第4轮
Director评估 → LLM分析：
  "刚释放了背景信息，让倾诉者展开和消化"

LLM调用：observe_and_wait(
  observation="刚释放了背景，倾诉者正在展开",
  wait_reason="让新信息充分发挥作用"
)

👁️ [Director] 决定暂不介入
```

---

### **第5轮：**
```
Actor: "她总是要求我按她的想法生活..."

🎬 [Director分析] 第5轮
Director评估 → LLM分析：
  "倾诉者已经说明了起因，可以深入冲突细节了"

LLM调用：select_and_reveal_fragment(
  fragment_category="conflict_details",
  fragment_index=0,
  reason="倾诉者提到了控制，可以说明母亲的具体话语"
)

🎬 [Director介入]
✅ 释放片段: cd_001
   内容: 母亲说'你应该听我的安排，我是为你好'
```

---

## 🎯 关键特性

### **1. 完全自主的时机判断 ✅**

```
Director不是被动地"每3轮执行"
而是主动地"每轮分析，自己决定"

第1轮 → observe_and_wait
第2轮 → observe_and_wait
第3轮 → select_fragment  ← 自己判断时机到了
第4轮 → observe_and_wait
第5轮 → select_fragment  ← 又判断可以释放了
第6轮 → observe_and_wait
第7轮 → observe_and_wait
第8轮 → select_fragment
```

**不是固定规律，而是根据对话状态决策！**

---

### **2. LLM看到所有信息再选择 ✅**

```
Director.evaluate_continuation()时：

LLM看到：
  ✓ 对话历史（完整）
  ✓ 当前进度
  ✓ 可用的11个预设片段
    - background[0]: 昨晚和母亲争吵
    - background[1]: 起因是生活理念
    - conflict_details[0]: 母亲的话
    - conflict_details[1]: 你的反驳
    - conflict_details[2]: 伤人的话
    - emotional_impact[0]: 内疚
    - emotional_impact[1]: 恐惧
    - deep_layers[0]: 渴望理解
    - deep_layers[1]: 内心挣扎
    - turning_points[0]: 理解母亲
    - turning_points[1]: 想和解

LLM决策：
  "当前进度10，对话3轮，AI在追问
   → 应该释放background[0]"
```

**LLM看到全貌后做出最优选择！** ✅

---

### **3. 从预设片段库中选择 ✅**

```
Director不是让LLM编剧情：
  ❌ "detail_content": "LLM自己编的剧情..."

而是让LLM选择：
  ✅ "fragment_category": "background"
  ✅ "fragment_index": 0

然后Director从数据库读取：
  ✅ content = database['background'][0]['content']
      = "昨晚和母亲发生了激烈的争吵"  ← 预设的
```

---

## 🔄 完整工作流程

```
每轮对话后：
  ├─ Director.evaluate_continuation()  ← 每轮都调用
  ├─ LLM看到：对话历史 + 进度 + 所有可用片段
  ├─ LLM决策：
  │   ├─ 时机未到？ → observe_and_wait
  │   ├─ 时机已到？ → select_fragment
  │   └─ 可结束？ → end_conversation
  ├─ Director处理决策：
  │   ├─ 如果observe → 不介入
  │   └─ 如果select → 从数据库读取并释放
  └─ 传递给Actor（如果介入）
```

---

## ✨ 核心优势

### **1. 时机完全智能 🧠**
- 不是固定3轮、5轮
- 而是LLM根据对话状态判断
- 可能第2轮就介入，也可能等到第8轮

### **2. 内容完全可控 📚**
- 所有剧情片段都是预设的
- Director从预设中选择
- 保证剧情的一致性和质量

### **3. 决策完全透明 👁️**
- LLM说明选择理由
- 每次决策都有日志
- 可追溯、可分析

---

## 🧪 测试运行

```bash
python3 -m Benchmark.scripts.run_demo
```

**观察输出：**
```
🎬 [Director分析] 第1轮
Director评估 → LLM分析
👁️ [Director] 决定暂不介入，继续观察

🎬 [Director分析] 第2轮
Director评估 → LLM分析
👁️ [Director] 决定暂不介入

🎬 [Director分析] 第3轮
Director评估 → LLM分析
🎬 [Director介入] 开始Judger评估和剧情指导
📖 [Director] 选择并释放剧情片段
   类别: background
   索引: 0
✅ [Director] 成功读取预设片段: bg_001
```

**不是每3轮，而是Director自己决定的时机！**

---

## 📋 已实现的功能

✅ **Director每轮都分析**
✅ **LLM自主决定是否介入**
✅ **4种决策选项**（observe/select/continue/end）
✅ **从预设片段库选择**
✅ **LLM看到所有可用片段**
✅ **基于全貌做出最优选择**

**完全符合你的需求！** 🎉

