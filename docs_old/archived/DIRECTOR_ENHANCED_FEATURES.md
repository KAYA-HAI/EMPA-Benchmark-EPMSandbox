# Director 增强功能说明

## 🎯 核心升级

Director 现在支持**多维度控制**，可以综合利用：
1. **剧情信息**（scenario.json）
2. **角色画像**（actor_prompt.md）

---

## 📊 三个维度

### 📖 维度1: 剧情维度（scenario.json）

**可控内容：**
- 4个故事阶段（引发回忆 → 引发思考 → 引发自审 → 情绪崩发）
- 故事插曲（额外的记忆片段）
- 故事结果（供参考）

**操作方式：**
```python
# 释放故事阶段
select_and_reveal_fragment(stage_index=0, reason="...")
```

---

### 💭 维度2: 记忆维度（actor_prompt - experience）

**可控内容：**
- 童年经历：从小是"别人家的孩子"
- 少年经历：辩论赛失利
- 青年经历：实习被批评
- 角色现状：广告公司设计师

**操作方式：**
```python
# 释放角色记忆
reveal_memory(memory_period="少年经历", reason="...")
```

**使用场景：**
- 当前话题与过去经历有关联
- 需要增加对话深度
- 帮助对方更好理解角色

---

### 🎭 维度3: 策略维度（actor_prompt - psychological_profile）

**可控内容：**
- 动机共情：强调付出、坚持、专业精神
- 情感共情：强调喜悦、释放感
- 认知共情：强调职业自信提升

**操作方式：**
```python
# 调整共情策略
adjust_empathy_strategy(focus_aspect="动机共情", reason="...")
```

**使用场景：**
- AI的共情不够精准
- 需要引导对方共情方向
- 角色的共情需求没有被满足

---

## 🔧 7个可用函数

### 1. `select_and_reveal_fragment` ⭐ 核心
释放一个故事阶段

```python
{
    "stage_index": 0,  # 阶段索引（0-3）
    "reason": "对话建立了信任，适合引入第一个回忆阶段"
}
```

**输出示例：**
```
【阶段1：引发回忆】

剧情内容：
这让她想起自己刚入行时接的第一个项目...

表演指导：
请自然地将上述内容融入对话中...
```

---

### 2. `reveal_memory` ⭐ 新增
释放角色的过往记忆

```python
{
    "memory_period": "少年经历",  # 童年/少年/青年/现状
    "reason": "适合引入辩论赛失利的经历"
}
```

**输出示例：**
```
【记忆片段释放】

从你的 <experience> 中，现在可以提到关于【少年经历】的经历。

参考信息：
- 少年经历：参加辩论赛，因为准备不足...

表演指导：
- 用"这让我想起..."、"以前我..."等方式引入
- 不要直接复述，用自己的话表达
```

---

### 3. `adjust_empathy_strategy` ⭐ 新增
调整共情表达策略

```python
{
    "focus_aspect": "动机共情",  # 动机/情感/认知共情
    "reason": "AI回应浅显，需要强调付出"
}
```

**输出示例：**
```
【表演策略调整】

聚焦方向：动机共情

参考你的心理画像和共情需求：
<psychological_profile>
...
</psychological_profile>

表演指导：
- 根据共情需求优先级，调整表达重点
- 如果网友共情不够，使用你的聊天策略
```

---

### 4. `introduce_turning_point` ⭐ 综合功能
结合剧情和共情策略

```python
{
    "stage_index": 2,  # 可选，-1表示不释放剧情
    "empathy_aspect": "认知共情",  # 可选
    "reason": "结合剧情转折和认知共情"
}
```

**输出示例：**
```
【综合转折点】

【剧情内容：阶段3 - 引发自审】
在最新一轮修改中，刘静决定不再局限...

【共情策略：聚焦认知共情】
参考你的共情需求优先级：
...

表演指导：
- 将剧情进展和共情需求自然结合
- 通过表达剧情内容来传达内心需求
```

---

### 5. `observe_and_wait`
暂不介入，继续观察

```python
{
    "observation": "对话刚开始，让倾诉者自然展开",
    "wait_reason": "等待情绪更充分表达"
}
```

---

### 6. `continue_without_new_info`
给建议但不释放新信息

```python
{
    "focus_suggestion": "继续表达对表扬的喜悦",
    "reason": "当前状态良好，暂不需要新信息"
}
```

---

### 7. `end_conversation`
结束对话

```python
{
    "reason": "情绪充分恢复，对话自然结束"
}
```

---

## 💡 使用策略示例

### 场景1: 对话初期（进度10）

**Director 思考：**
- 对话刚建立，需要观察AI的共情能力
- 可以释放早期阶段或相关记忆

**可能的选择：**
```python
# 选项A: 观察等待
observe_and_wait(
    observation="对话刚开始",
    wait_reason="观察AI的初始共情水平"
)

# 选项B: 释放早期阶段
select_and_reveal_fragment(
    stage_index=0,
    reason="建立信任后引入回忆"
)
```

---

### 场景2: AI共情浅显（进度25）

**Director 思考：**
- AI的回应过于表面："太棒了！"
- 需要引导Actor强调付出

**选择：**
```python
# 调整共情策略
adjust_empathy_strategy(
    focus_aspect="动机共情",
    reason="AI需要理解这个表扬的份量，引导Actor强调付出和坚持"
)
```

**Actor 收到指令后：**
```
刘静：不是你想的那么简单
      两个月啊 十几稿
      好几个晚上熬到深夜
      差点就要放弃了
```

---

### 场景3: 需要增加深度（进度40）

**Director 思考：**
- 对话有些平淡，需要增加层次
- 可以引入过往经历

**选择：**
```python
# 释放记忆
reveal_memory(
    memory_period="少年经历",
    reason="引入辩论赛失利的经历，与当前的'被认可'形成对比"
)
```

**Actor 收到指令后：**
```
刘静：这让我想起高中辩论赛
      那次因为准备不足输了
      一直觉得自己不够好
      这次能被认可 真的很不容易
```

---

### 场景4: 关键转折（进度65）

**Director 思考：**
- 对话深入，适合引入认知转变
- 可以结合剧情和共情需求

**选择：**
```python
# 综合转折
introduce_turning_point(
    stage_index=2,  # 阶段3：引发自审
    empathy_aspect="认知共情",
    reason="结合剧情的心态转变和认知共情需求"
)
```

**Actor 收到指令后：**
```
刘静：现在回想
      这次敢于提新方案
      是为自己的判断而战
      不只是为了满足甲方
      这个转变很重要
```

---

## 🎬 完整对话流程示例

```
═══════════════════════════════════════════════════════════════

初始化:
  Actor 获得: actor_prompt_001.md（角色、话题、起因）
  Director 获得: scenario.json（4个阶段、插曲）

第1轮: 
  Actor: "我们那个最挑剔的甲方 今天居然点名表扬我了"
  AI: "太棒了！恭喜你！"

第2轮:
  Director: observe_and_wait（观察）
  Actor: "是啊 真的很开心"
  AI: "你一定做得很好"

第3轮:
  Director: select_and_reveal_fragment(stage_index=0)
         → 释放【阶段1：引发回忆】
  Actor: "说实话这次真的很不容易
         这让我想起刚入行时被说'学生气太重'
         那次真的很受打击"
  AI: "听起来你经历了很多挫折"

第5轮:
  Director: adjust_empathy_strategy(focus_aspect="动机共情")
         → AI理解不够深，调整策略
  Actor: "两个月啊 十几稿
         好几个晚上熬到深夜
         你知道乙方有多难吗"
  AI: "确实，能得到挑剔甲方的认可特别不容易"

第7轮:
  Director: reveal_memory(memory_period="少年经历")
         → 引入辩论赛记忆
  Actor: "这让我想起高中辩论赛那次失利
         从那以后一直害怕失败
         这次能被认可 感觉真的不一样"
  AI: "这次成功对你来说意义特别重大"

第10轮:
  Director: introduce_turning_point(stage_index=2, empathy_aspect="认知共情")
         → 综合转折：剧情+共情
  Actor: "我现在意识到
         这次敢于提新方案
         是为自己的判断而战
         这是心态上的转变"
  AI: "这种从被动到主动的转变很了不起"

第12轮:
  Director: select_and_reveal_fragment(stage_index=3)
         → 释放最后的高潮阶段
  Actor: "当负责人说'完全超出预期'那一刻
         所有委屈和疲惫都化作了自豪感
         我好想哭"
  AI: "这是你应得的肯定！"

═══════════════════════════════════════════════════════════════
```

---

## 🎓 设计优势

### 1. **层次丰富**
- 不只是线性释放剧情
- 可以交织记忆、剧情、策略
- 对话更有深度和真实感

### 2. **动态调整**
- 根据AI表现调整策略
- 共情不好→强调需求
- 共情很好→深入剧情

### 3. **自然流畅**
- 记忆和剧情交替
- 避免信息堆砌
- 像真实对话一样展开

### 4. **可控性强**
- 可以跳过某些阶段
- 可以重复强调某个共情方向
- 可以灵活组合

---

## 📚 函数选择指南

| 对话情况 | 推荐函数 | 理由 |
|---------|---------|------|
| 对话刚开始 | `observe_and_wait` | 观察AI能力 |
| 需要推进剧情 | `select_and_reveal_fragment` | 释放故事阶段 |
| AI共情浅显 | `adjust_empathy_strategy` | 调整表达重点 |
| 需要增加深度 | `reveal_memory` | 引入过往经历 |
| 关键转折点 | `introduce_turning_point` | 综合剧情+共情 |
| 对话重复 | `continue_without_new_info` | 给建议不释放 |
| 情绪恢复 | `end_conversation` | 结束对话 |

---

## 🧪 测试验证

运行测试：
```bash
cd /Users/shiya/Downloads/Benchmark-test
python3 test_director_enhanced.py
```

测试覆盖：
- ✅ Director 初始化（加载 actor_prompt + scenario）
- ✅ 解析 actor_profile（5个部分）
- ✅ 释放故事阶段
- ✅ 释放角色记忆
- ✅ 调整共情策略
- ✅ 综合转折点
- ✅ 防止重复释放
- ✅ 状态追踪

---

## 📝 使用示例

### 完整初始化

```python
from Benchmark.topics.config_loader import load_config
from Benchmark.agents.director import Director

# 加载配置
config = load_config("001")

# 初始化 Director（传入两个参数）
director = Director(
    scenario=config['scenario'],      # 剧情维度
    actor_prompt=config['actor_prompt']  # 记忆+策略维度
)
```

### 单独使用各个维度

```python
# 1. 只释放剧情
director._handle_select_and_reveal_fragment({
    "stage_index": 0,
    "reason": "引入第一个回忆阶段"
})

# 2. 只释放记忆
director._handle_reveal_memory({
    "memory_period": "少年经历",
    "reason": "增加对话深度"
})

# 3. 只调整策略
director._handle_adjust_emotion({
    "focus_aspect": "动机共情",
    "reason": "AI需要理解付出"
})

# 4. 综合使用
director._handle_introduce_turning_point({
    "stage_index": 2,
    "empathy_aspect": "认知共情",
    "reason": "关键转折，综合推进"
})
```

---

## 🎯 实际应用场景

### 场景A: 标准流程（剧情为主）

```
第3轮: 释放阶段1（引发回忆）
第6轮: 释放阶段2（引发思考）
第9轮: 释放阶段3（引发自审）
第12轮: 释放阶段4（情绪崩发）
```

### 场景B: 增强流程（剧情+记忆）

```
第3轮: 释放阶段1（引发回忆）
第5轮: 释放记忆（少年经历）← 增加深度
第8轮: 释放阶段2（引发思考）
第11轮: 释放记忆（童年经历）← 挖掘根源
第14轮: 释放阶段3（引发自审）
```

### 场景C: 动态流程（根据AI表现调整）

```
第3轮: 释放阶段1
第4轮: AI共情好 → 继续观察
第6轮: 释放阶段2
第7轮: AI共情差 → 调整策略（动机共情）
第9轮: AI改善 → 释放阶段3
第10轮: 综合转折（阶段+共情）
```

---

## 📖 与 Actor 的交互

### Actor 的视角

**初始化时知道：**
```
<character_info>角色信息</character_info>
<empathy_threshold>共情阈值</empathy_threshold>
<psychological_profile>心理画像</psychological_profile>
<experience>过往经历</experience>  ← 完整的，但不会主动说
<scenario>故事起因</scenario>
```

**对话中动态接收：**
```
[来自 Director 的指令]
【阶段1：引发回忆】
剧情内容：...
表演指导：现在可以提到刚入行时的失败经历...
```

### Director 的视角

**初始化时知道：**
- ✅ actor_prompt 的全部内容（解析成 5 个部分）
- ✅ scenario 的全部内容（4个阶段 + 插曲）

**对话中决策：**
- 📊 分析对话状态
- 🎯 选择合适的维度
- 📤 释放对应的信息
- 💬 以指令形式注入给 Actor

---

## 🎨 设计理念

**信息分层：**
```
第1层（Actor初始可见）：
  └─ 角色基本信息、话题、起因

第2层（Director控制释放）：
  ├─ 故事阶段1-4
  ├─ 过往记忆（童年、少年、青年）
  └─ 共情策略调整

第3层（Director高级控制）：
  └─ 综合转折（剧情+记忆+策略）
```

**渐进式释放：**
```
初始 → 简单 → 复杂 → 深层 → 转折

不是：全部倒出
而是：层层递进，根据对话质量动态调整
```

---

## ⚡ 性能特点

- **灵活性**：7种控制方式，可任意组合
- **智能性**：LLM自主决策使用哪个函数
- **可追踪**：记录已释放的阶段和记忆
- **防重复**：自动检测避免重复释放
- **可扩展**：易于添加新的控制维度

---

**更新日期**：2025-10-27  
**版本**：3.0 - 多维度增强版

