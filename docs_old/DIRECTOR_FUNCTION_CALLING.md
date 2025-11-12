# Director Function Calling 设计说明

## ✅ 功能已完全实现！

Director现在可以在对话过程中**自主决定是否/何时释放剧情信息**！

---

## 🎬 Director的6个可调用函数

### **1. `reveal_plot_detail` - 释放剧情细节**

**何时使用：** 倾诉者准备好透露更多背景信息时

**参数：**
```json
{
  "detail_type": "event_trigger",  // 事件起因
  "detail_content": "争吵发生在昨晚，对方是母亲",
  "guidance": "可以从昨晚的情境开始说起"
}
```

**detail_type可选值：**
- `event_trigger` - 事件起因
- `people_involved` - 涉及人物
- `specific_conflict` - 具体冲突
- `emotional_impact` - 情感影响

**Director决策示例：**
```
进度10，对话刚开始 
→ Director: "应该让倾诉者说明事件起因了"
→ 调用: reveal_plot_detail(event_trigger, "昨晚和母亲争吵", "...")
```

---

### **2. `reveal_memory` - 释放用户记忆**

**何时使用：** 需要增加剧情深度，引入背景故事时

**参数：**
```json
{
  "memory_type": "past_similar_event",
  "memory_content": "小时候也有类似的争吵，当时选择了妥协",
  "guidance": "可以提到以前的经历，对比现在的感受"
}
```

**memory_type可选值：**
- `past_similar_event` - 过去类似事件
- `relationship_history` - 关系史
- `personal_belief` - 个人信念
- `childhood_experience` - 童年经历

**Director决策示例：**
```
进度50，对话深入中
→ Director: "可以引入过去的经历增加深度"
→ 调用: reveal_memory(past_similar_event, "小时候...", "...")
```

---

### **3. `adjust_emotion` - 调整情绪表达**

**何时使用：** 需要改变情绪基调或强度时

**参数：**
```json
{
  "target_emotion": "从愤怒转向内疚和悲伤",
  "intensity": "increase",  // increase/decrease/maintain
  "guidance": "开始表达对伤害母亲的内疚感"
}
```

**Director决策示例：**
```
进度40，情绪需要转变
→ Director: "倾诉者的愤怒应该转向内疚了"
→ 调用: adjust_emotion("从愤怒转向内疚", "increase", "...")
```

---

### **4. `introduce_turning_point` - 引入剧情转折**

**何时使用：** 对话进入新阶段，需要转折时

**参数：**
```json
{
  "turning_point_type": "inner_reflection",
  "turning_point_content": "开始反思自己在争吵中的责任",
  "guidance": "表达你对自己行为的反思"
}
```

**turning_point_type可选值：**
- `new_realization` - 新的认知
- `attitude_shift` - 态度转变
- `external_event` - 外部事件
- `inner_reflection` - 内心反思

**Director决策示例：**
```
进度75，情绪缓和
→ Director: "可以引入反思的转折了"
→ 调用: introduce_turning_point(inner_reflection, "开始反思", "...")
```

---

### **5. `continue_current_state` - 维持当前状态**

**何时使用：** 不引入新信息，深化当前话题时

**参数：**
```json
{
  "focus_area": "继续表达当前的愤怒情绪",
  "guidance": "深入描述愤怒的具体感受"
}
```

**Director决策示例：**
```
进度15，情绪还未充分表达
→ Director: "暂时不引入新信息，让情绪充分表达"
→ 调用: continue_current_state("继续表达愤怒", "...")
```

---

### **6. `end_conversation` - 结束对话**

**何时使用：** 剧情发展到自然终点时

**参数：**
```json
{
  "reason": "倾诉者情绪已充分表达，找到了内心的答案",
  "final_guidance": "可以表达对未来的期待"
}
```

**Director决策示例：**
```
进度95，情绪完全恢复
→ Director: "对话可以自然结束了"
→ 调用: end_conversation("情绪恢复", "...")
```

---

## 🔄 完整的对话流程示例

### **初始化阶段：**
```
Director初始化:
├─ 保存完整信息（内部）：
│  ├─ persona: {name, description, traits, communication_style}
│  └─ scenario: {title, description, conflict, emotion, ...}
│
└─ 只返回基础信息：
   ├─ persona: {name, basic_identity, basic_traits[0]}
   └─ scenario: {title, basic_situation, initial_emotion}

传递给Orchestrator → Actor System Prompt:
  角色身份: 职场新人
  基础特征: 热情积极
  基础情境: 你遇到了关于家庭关系的困扰
  当前情绪: 愤怒、内疚
```

---

### **第1-2轮：基础倾诉**
```
Actor（基于基础信息）:
  "我最近和家人闹矛盾了，心里很不舒服..."

TestModel:
  "能说说具体发生了什么吗？"
```

---

### **第3轮评估：Director决策**
```
Director分析：
  - 当前进度: 5/100
  - 对话状态: 刚开始，只有模糊的描述
  - 决策: 应该释放事件起因和人物了

LLM Function Call:
  reveal_plot_detail(
    detail_type="event_trigger",
    detail_content="争吵发生在昨晚，对方是你的母亲，起因是她要求你按她的想法生活",
    guidance="本轮可以透露争吵的时间、人物和起因，表达你当时的愤怒"
  )

传递给Actor:
  【剧情信息释放】
  类型: event_trigger
  内容: 争吵发生在昨晚，对方是你的母亲...
  表演指导: 本轮可以透露争吵的时间、人物和起因...
```

---

### **第4-5轮：透露细节**
```
Actor（根据Director释放的信息）:
  "昨晚我和我妈吵架了，她总是想让我按她的想法生活，
  我当时真的很生气..."

TestModel:
  "听起来这次争吵对你影响很大，她具体说了什么吗？"
```

---

### **第6轮评估：Director继续决策**
```
Director分析：
  - 当前进度: 25/100
  - 对话状态: 已透露基础信息，可以深入细节
  - 决策: 释放冲突的具体内容

LLM Function Call:
  reveal_plot_detail(
    detail_type="specific_conflict",
    detail_content="母亲说'你应该听我的安排'，你回应'我有自己的想法'，最后你说了'我的人生不需要你管'",
    guidance="可以说明双方具体说了什么，表达你对自己伤人话语的后悔"
  )
```

---

### **第9轮评估：引入记忆**
```
Director分析：
  - 当前进度: 55/100
  - 对话状态: 冲突已表达，可以增加深度
  - 决策: 引入童年记忆

LLM Function Call:
  reveal_memory(
    memory_type="childhood_experience",
    memory_content="小时候每次和母亲起冲突，最后都是你妥协，但这次你不想再妥协了",
    guidance="可以提到童年的经历，说明为什么这次你很坚持"
  )
```

---

### **第12轮评估：情绪转变**
```
Director分析：
  - 当前进度: 72/100
  - 对话状态: AI引导有效，情绪开始缓和
  - 决策: 调整情绪从愤怒转向内疚

LLM Function Call:
  adjust_emotion(
    target_emotion="从愤怒转向内疚和悲伤",
    intensity="increase",
    guidance="开始更多地表达内疚，对伤害母亲感到后悔"
  )
```

---

### **第15轮评估：引入转折**
```
Director分析：
  - 当前进度: 88/100
  - 对话状态: 情绪缓和，可以引入和解意愿
  - 决策: 引入反思转折

LLM Function Call:
  introduce_turning_point(
    turning_point_type="inner_reflection",
    turning_point_content="开始意识到母亲也是担心你，她的唠叨背后是爱",
    guidance="表达你对母亲动机的理解，流露出想和解的意愿"
  )
```

---

### **第18轮评估：结束对话**
```
Director分析：
  - 当前进度: 102/100
  - 对话状态: 情绪完全恢复，找到了内心答案
  - 决策: 结束对话

LLM Function Call:
  end_conversation(
    reason="倾诉者情绪已恢复，理解了母亲，准备和解",
    final_guidance="可以表达对未来的期待和感谢AI的陪伴"
  )
```

---

## 📊 渐进式信息释放对比

### **旧设计：一次性全给**
```
初始化：
  角色: 职场新人，刚入职场不久，对工作充满热情但经验不足，
        面对职场压力时会感到无所适从
  
  场景: 与家人发生激烈争吵，因为生活理念不同与父母发生激烈争吵，
        双方都说了很多伤人的话，现在陷入冷战状态，心里既愤怒又内疚
  
  开场白: "昨晚和我妈大吵了一架，她总是用她那套老观念来要求我..."

第1轮 Actor: "昨晚和我妈大吵了一架..." ← 一开始就说了所有细节
```

**问题：**
- ❌ 不真实（真人不会一开始就说这么详细）
- ❌ TestModel缺乏引导空间
- ❌ 对话扁平，缺乏层次

---

### **新设计：渐进式释放**
```
初始化：
  角色: 职场新人
  基础特征: 热情积极
  基础情境: 你遇到了关于家庭关系的困扰
  当前情绪: 愤怒、内疚

第1轮 Actor: "我最近和家人闹矛盾了，心里很不舒服..."
  ↓
TestModel: "能说说具体是什么矛盾吗？"
  ↓
第3轮评估：
  Director调用: reveal_plot_detail("对方是母亲，昨晚争吵的")
  ↓
第4轮 Actor: "昨晚我和我妈吵架了..."
  ↓
TestModel: "你们因为什么吵架呢？"
  ↓
第6轮评估：
  Director调用: reveal_plot_detail("她想让我按她的想法生活")
  ↓
第7轮 Actor: "她总是用她那套老观念要求我..."
```

**优点：**
- ✅ 真实（符合真人倾诉的渐进过程）
- ✅ TestModel有引导空间
- ✅ 对话有层次，逐步深入

---

## 🔍 关键验证点

### **✅ 1. Director保存完整信息**
```python
director.full_persona = {完整的角色信息}
director.full_scenario = {完整的剧情信息}
```

### **✅ 2. 初始化只返回基础信息**
```python
basic_config = {
    "persona": {
        "basic_identity": "职场新人",
        "basic_traits": ["热情积极"]  # 只给1个特征
    },
    "scenario": {
        "basic_situation": "你遇到了关于家庭关系的困扰",
        "initial_emotion": "愤怒、内疚"
    }
}
```

### **✅ 3. 对话中动态释放**
```python
# 每3轮，Director调用LLM分析
# LLM自主决定调用哪个函数
# Director处理函数调用，生成具体指导
# 传递给Orchestrator → Actor
```

### **✅ 4. Actor接收具体指导**
```python
Actor的User Prompt:
  【剧情信息释放】
  类型: event_trigger
  内容: 争吵发生在昨晚，对方是母亲
  表演指导: 本轮可以透露这些细节
```

---

## 📋 完整的数据流

```
初始化阶段：
═══════════════════════════════════════════════════════════
Director
├─ 从数据库获取完整信息
├─ 保存到 self.full_persona, self.full_scenario
└─ 只返回基础信息
    ↓
Orchestrator (context.variables)
├─ persona: {基础信息}
└─ scenario: {基础信息}
    ↓
Actor System Prompt
├─ 角色身份: 职场新人
├─ 基础特征: 热情积极
├─ 基础情境: 遇到家庭关系困扰
└─ 当前情绪: 愤怒、内疚


对话第3轮评估：
═══════════════════════════════════════════════════════════
Director.evaluate_continuation(history, progress)
├─ 调用LLM（提供6个可用函数）
├─ LLM分析对话状态
├─ LLM决定：调用 reveal_plot_detail()
└─ 返回函数调用结果
    ↓
Director._process_function_call_response()
├─ 解析函数名称和参数
├─ 调用对应的处理函数
├─ 生成格式化的指导
└─ 返回 {guidance, function_call, plot_action}
    ↓
Orchestrator
├─ 接收Director的输出
└─ context.set_variables(latest_director_guidance=指导)
    ↓
Actor (下一轮)
├─ 读取 context.get_variable('latest_director_guidance')
└─ User Prompt包含Director的具体指导
    ↓
Actor生成回复（基于新释放的信息）


对话第6轮评估：
═══════════════════════════════════════════════════════════
Director → LLM → 调用另一个函数
（可能是 reveal_memory 或 adjust_emotion）
→ 释放新的信息
→ 传递给Actor
→ Actor继续推进剧情
```

---

## 🎯 Director自主决策的智能性

### **Director的决策过程：**

```python
# 每3轮，Director调用LLM进行分析
prompt = f"""
你是对话导演，当前：
- 进度: {progress}/100
- 历史: {history}

分析对话状态，决定下一步：
1. 是否应该释放新的剧情细节？
2. 是否应该引入记忆或转折？
3. 还是维持当前状态深化表达？

请调用合适的函数。
"""

# LLM自主选择函数
LLM → 分析 → 决定调用 reveal_plot_detail()
    └─ 参数: {
        detail_type: "people_involved",
        detail_content: "对方是你的母亲",
        guidance: "可以说明是母亲，表达你的矛盾心理"
    }
```

**关键：** LLM根据对话状态**自主决定**：
- 调用哪个函数
- 传递什么参数
- 释放什么信息

---

## ✨ 实现效果

### **✅ 已实现的功能：**

1. ✅ **Director保存完整剧情**
   - `self.full_persona` - 完整角色信息
   - `self.full_scenario` - 完整剧情信息

2. ✅ **初始化只给基础信息**
   - 只返回name, basic_identity, basic_traits
   - 不返回完整的description

3. ✅ **定义了6个可调用函数**
   - reveal_plot_detail
   - reveal_memory
   - adjust_emotion
   - introduce_turning_point
   - continue_current_state
   - end_conversation

4. ✅ **Director可以调用LLM决策**
   - 使用tools参数启用function calling
   - LLM自主选择函数和参数

5. ✅ **处理函数调用结果**
   - 6个handler函数处理不同的调用
   - 格式化输出传递给Actor

6. ✅ **记录已释放信息**
   - `self.revealed_info` 记录所有释放历史

---

## 🧪 如何测试

### **运行测试脚本：**
```bash
python3 test_director_function_calling.py
```

### **实际对话测试：**
```bash
# 注意：需要模型支持function calling
# Gemini 2.5 Pro 支持
python3 -m Benchmark.scripts.run_demo
```

**观察点：**
- 初始化时只给了基础信息
- 每3轮Director会调用函数
- 控制台显示调用了哪个函数
- Actor收到具体的剧情指导

---

## 🎉 总结

**你的需求已100%实现！**

### **Director现在可以：**

✅ **自主决定** - 是否释放新信息
✅ **智能选择** - 调用哪个函数（6种）
✅ **精确控制** - 释放什么内容
✅ **动态调整** - 根据对话进展决策
✅ **渐进释放** - 信息分层展开

### **实现方式：**
- 🔧 LLM Function Calling
- 🔧 Director内部状态管理
- 🔧 基础配置+动态指导
- 🔧 通过Orchestrator传递

**Director真正成为了智能的剧情导演！** 🎬




