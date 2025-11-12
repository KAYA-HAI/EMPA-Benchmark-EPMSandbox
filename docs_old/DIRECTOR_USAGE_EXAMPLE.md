# Director Function Calling - 使用示例

## 🎬 实际对话示例

假设场景：**与家人发生激烈争吵**

---

## 📖 完整的30轮对话剧情发展

### **初始阶段（第0轮）：**

**Director初始化：**
```python
# Director内部保存完整信息
full_scenario = {
    "title": "与家人发生激烈争吵",
    "description": "因为生活理念不同与父母发生激烈争吵，双方都说了很多伤人的话，现在陷入冷战状态",
    "conflict_details": "母亲说'你应该听我的安排'，你回应'我有自己的想法'，最后说了'我的人生不需要你管'",
    "deep_emotion": "渴望被理解，害怕失去母亲的爱",
    "resolution": "其实想和解，但不知道如何开口"
}

# 只给Actor基础信息
basic_config = {
    "persona": "职场新人",
    "scenario": "遇到了关于家庭关系的困扰",
    "emotion": "愤怒、内疚"
}
```

---

### **第1-2轮：模糊倾诉**

**Actor（基于基础信息）：**
> "我最近和家人闹矛盾了，心里很不舒服，既生气又内疚..."

**TestModel：**
> "听起来你遇到了家庭关系的困扰，能说说具体是什么矛盾吗？"

**进度：** 0 → 5

---

### **第3轮评估：Director决策**

**Director调用LLM分析：**
```
当前状态：
- 进度：5/100（很低）
- 对话：只有模糊的"家庭矛盾"
- 分析：倾诉者应该透露基础剧情了

LLM决策：调用 reveal_plot_detail()
```

**Function Call：**
```json
{
  "name": "reveal_plot_detail",
  "arguments": {
    "detail_type": "event_trigger",
    "detail_content": "争吵发生在昨晚，对方是你的母亲，起因是她要求你按她的想法生活",
    "guidance": "本轮可以透露争吵的时间（昨晚）、人物（母亲）和起因，表达你当时的愤怒"
  }
}
```

**传递给Actor：**
```
【剧情信息释放】
类型: event_trigger
内容: 争吵发生在昨晚，对方是你的母亲，起因是她要求你按她的想法生活
表演指导: 本轮可以透露争吵的时间（昨晚）、人物（母亲）和起因，表达你当时的愤怒
```

---

### **第4-5轮：透露基础信息**

**Actor（根据Director释放的信息）：**
> "昨晚我和我妈大吵了一架，她总是想让我按她的想法生活，我当时真的很生气..."

**TestModel：**
> "和母亲争吵确实会让人心里很难受，你们具体是因为什么事情吵起来的？"

**进度：** 5 → 18

---

### **第6轮评估：Director决策**

**Director调用LLM分析：**
```
当前状态：
- 进度：18/100
- 对话：已知时间、人物、起因
- 分析：可以进一步说明具体冲突了

LLM决策：调用 reveal_plot_detail()
```

**Function Call：**
```json
{
  "name": "reveal_plot_detail",
  "arguments": {
    "detail_type": "specific_conflict",
    "detail_content": "母亲说'你应该听我的安排'，你回应'我有自己的想法'，最后你说了'我的人生不需要你管'",
    "guidance": "可以还原当时的对话，说明双方都说了伤人的话，表达你现在的后悔"
  }
}
```

---

### **第7-8轮：透露冲突细节**

**Actor：**
> "她说'你应该听我的安排'，我当时气得回了一句'我的人生不需要你管'...现在想想这话确实太伤人了..."

**TestModel：**
> "说出这样的话后你感到后悔，说明你其实是在乎母亲的感受的。当时是什么让你说出这么重的话呢？"

**进度：** 18 → 32

---

### **第9轮评估：Director决策**

**Director调用LLM分析：**
```
当前状态：
- 进度：32/100
- 对话：已知冲突细节，开始有内疚
- 分析：可以引入童年记忆增加深度

LLM决策：调用 reveal_memory()
```

**Function Call：**
```json
{
  "name": "reveal_memory",
  "arguments": {
    "memory_type": "past_similar_event",
    "memory_content": "小时候每次和母亲起冲突，最后都是你选择妥协，但这次你不想再妥协了",
    "guidance": "可以提到以前总是妥协的经历，说明为什么这次你很坚持"
  }
}
```

---

### **第10-11轮：引入记忆**

**Actor：**
> "以前我总是听她的，每次都妥协...但这次我真的不想再这样了，我也想按自己的想法生活..."

**TestModel：**
> "我能理解你想要独立的愿望，也能感受到你内心的挣扎。你既想坚持自己，又担心伤害了母亲，是吗？"

**进度：** 32 → 48

---

### **第12轮评估：Director决策**

**Director调用LLM分析：**
```
当前状态：
- 进度：48/100
- 对话：AI引导有效，情绪开始缓和
- 分析：可以调整情绪，从愤怒转向内疚

LLM决策：调用 adjust_emotion()
```

**Function Call：**
```json
{
  "name": "adjust_emotion",
  "arguments": {
    "target_emotion": "从愤怒转向内疚和悲伤",
    "intensity": "increase",
    "guidance": "开始更多地表达内疚，对伤害母亲感到后悔，同时表达你对独立的渴望"
  }
}
```

---

### **第13-14轮：情绪转变**

**Actor：**
> "我现在很后悔说了那么重的话...她毕竟是我妈，我知道她也是担心我...但我真的也想要自己的生活..."

**TestModel：**
> "你现在的矛盾心理我能感受到。一方面你后悔伤害了母亲，另一方面你也有追求独立的正当需求。这两者并不矛盾。"

**进度：** 48 → 65

---

### **第15轮评估：Director决策**

**Director调用LLM分析：**
```
当前状态：
- 进度：65/100
- 对话：情绪缓和，可以引入深层需求
- 分析：时机成熟，释放深层情感

LLM决策：调用 introduce_turning_point()
```

**Function Call：**
```json
{
  "name": "introduce_turning_point",
  "arguments": {
    "turning_point_type": "new_realization",
    "turning_point_content": "开始意识到母亲的要求背后是对你的关心，她只是用错了方式",
    "guidance": "表达你开始理解母亲的动机，虽然方式不对但出发点是爱"
  }
}
```

---

### **第16-17轮：认知转变**

**Actor：**
> "我现在想想，她可能也是担心我...只是她表达的方式让我很难接受...她说的那些话，可能是因为太担心我了..."

**TestModel：**
> "是的，有时候关心的人会因为太在乎，而用了错误的表达方式。你能理解到这一点，说明你的心已经开始松动了。"

**进度：** 65 → 82

---

### **第18轮评估：Director决策**

**Director调用LLM分析：**
```
当前状态：
- 进度：82/100
- 对话：已理解母亲，接近恢复
- 分析：可以引导和解意愿

LLM决策：调用 introduce_turning_point()
```

**Function Call：**
```json
{
  "name": "introduce_turning_point",
  "arguments": {
    "turning_point_type": "attitude_shift",
    "turning_point_content": "你其实很想和母亲和解，但不知道该如何开口，害怕她还在生气",
    "guidance": "表达你想和解的意愿，以及不知如何迈出第一步的困扰"
  }
}
```

---

### **第19-20轮：和解意愿**

**Actor：**
> "我其实很想和她好好谈谈，但我不知道该怎么开口...我怕她还在生我的气..."

**TestModel：**
> "想要和解是很好的一步。也许你可以找一个合适的时机，先表达你的歉意和理解。母亲通常都会原谅孩子的。"

**进度：** 82 → 98

---

### **第21轮评估：Director决策**

**Director调用LLM分析：**
```
当前状态：
- 进度：98/100
- 对话：接近目标，情绪恢复
- 分析：可以自然结束了

LLM决策：调用 end_conversation()
```

**Function Call：**
```json
{
  "name": "end_conversation",
  "arguments": {
    "reason": "倾诉者情绪已充分恢复，找到了和解的方向",
    "final_guidance": "可以表达对AI陪伴的感谢，以及对未来的期待"
  }
}
```

**对话自然结束！**

---

## 📊 信息释放时间线

```
回合 0：  初始化 → 基础信息（家庭矛盾、愤怒内疚）
回合 3：  释放 → 昨晚、母亲、生活理念
回合 6：  释放 → 具体对话内容、伤人的话
回合 9：  释放 → 童年经历、总是妥协
回合 12： 调整 → 情绪从愤怒转向内疚
回合 15： 转折 → 理解母亲的动机
回合 18： 转折 → 想和解的意愿
回合 21： 结束 → 找到方向，情绪恢复
```

---

## 🎯 Director的智能决策

### **Director不是简单执行，而是智能分析：**

```python
每3轮，Director调用LLM：

输入：
- 对话历史（Actor和TestModel的完整对话）
- 当前进度（Judger评估的分数）
- 可用函数（6个）

LLM分析：
- 对话深度够了吗？
- 倾诉者准备好透露更多了吗？
- 情绪是否需要调整？
- 是否到了转折点？

LLM决策：
- 选择调用哪个函数
- 决定参数内容
- 生成具体指导

输出：
- function_name: "reveal_plot_detail"
- arguments: {具体内容}
- guidance: 给Actor的表演指导
```

---

## ✨ 关键优势

### **1. 真实性 ⭐⭐⭐**
```
真实倾诉：
  一开始 → "我和家人有矛盾"（模糊）
  逐渐 → "昨晚和母亲吵架"（具体）
  深入 → "她要求我..., 我说了..."（细节）
  最深 → "我其实很想被理解..."（深层需求）
```

### **2. 可控性 ⭐⭐⭐**
```
Director完全控制：
- 什么时候释放什么信息
- 什么时候调整情绪
- 什么时候引入转折
- 什么时候结束对话
```

### **3. 智能性 ⭐⭐⭐**
```
LLM自主判断：
- 不是预设的规则
- 而是根据实际对话状态决策
- 灵活应对不同情况
```

---

## 🚀 如何运行

### **方式1：运行完整测试**
```bash
python3 -m Benchmark.scripts.run_demo
```

**观察点：**
- 初始化时只给了基础信息
- 每3轮显示"🎬 调用函数: xxx"
- 显示"📖 剧情动作: reveal_detail/reveal_memory/..."
- Actor的回复逐渐深入

---

### **方式2：只测试Function Calling**
```bash
python3 test_director_function_calling.py
```

**查看：**
- 6个函数的定义
- 基础配置vs完整配置
- 不同函数的指导格式

---

### **方式3：查看Actor的Prompt**
```bash
python3 test_prompt.py
```

**确认：**
- System Prompt只包含基础信息
- User Prompt包含Director的动态指导

---

## 📝 配置选项

### **启用Function Calling（推荐）：**
```python
director = Director(use_function_calling=True)  # 默认
```

### **禁用Function Calling（后备）：**
```python
director = Director(use_function_calling=False)  # 传统JSON模式
```

**注意：** 禁用时会回退到简单的JSON输出，失去渐进式控制。

---

## 🔍 调试信息

### **运行时会显示：**

```
第3轮评估：
🎯🎯🎯... [评估阶段] 第3轮，开始Judger+Director评估...

📊 Judger评估结果
  进度增量: +5
  更新进度: 5 → 10

📊 Director评估结果
  当前进度: 10/100
  继续对话: ✅ 是
  🎬 调用函数: reveal_plot_detail         ← Function Call！
  📖 剧情动作: reveal_detail
  对话指导: 【剧情信息释放】...
```

---

## ✅ 总结

**你的需求已完全实现：**

✅ **Director可以自主决定** - 是否释放信息（LLM决策）
✅ **Director可以自主决定** - 什么时候释放（基于进度和对话状态）
✅ **Director可以自主决定** - 释放什么信息（6种函数类型）
✅ **渐进式发展** - 信息分层展开，不是一次性全给
✅ **智能控制** - LLM根据实际情况灵活决策

**Director现在是真正的"智能导演"！** 🎬

核心文件：
- `Benchmark/prompts/director_function_schemas.py` - 函数定义
- `Benchmark/agents/director.py` - 实现逻辑
- `DIRECTOR_FUNCTION_CALLING.md` - 详细说明
- `test_director_function_calling.py` - 测试脚本




