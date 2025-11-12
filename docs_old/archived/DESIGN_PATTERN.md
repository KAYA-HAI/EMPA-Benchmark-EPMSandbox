# 渐进式剧情释放设计模式

## 🎯 核心设计理念

**关键原则：信息分层，渐进释放**

1. **Actor Prompt (actor_prompt_XXX.md)** - Actor 的固定背景
   - ✅ Actor 在初始化时就完全获得
   - ✅ 包含角色设定、性格、基础背景
   - ✅ 在整个对话过程中保持不变

2. **Scenario JSON (scenario_XXX.json)** - Director 的剧情库
   - ⚠️ **只有 Director 能看到**
   - ⚠️ Actor 初始化时**不知道**这些内容
   - ⚠️ 通过 Director 的指令**动态注入**

---

## 📊 信息可见性矩阵

| 信息类型 | Actor 初始化时 | Director | 释放方式 |
|---------|--------------|----------|---------|
| 角色基本信息 | ✅ 完全可见 | ✅ 可见 | 写在 actor_prompt.md |
| 聊天话题 | ✅ 完全可见 | ✅ 可见 | 写在 actor_prompt.md |
| 共情需求 | ✅ 完全可见 | ✅ 可见 | 写在 actor_prompt.md |
| 故事起因 | ✅ 完全可见 | ✅ 可见 | 写在 actor_prompt.md |
| **故事阶段1-4** | ❌ 不可见 | ✅ 可见 | **Director 动态释放** |
| **故事插曲** | ❌ 不可见 | ✅ 可见 | **Director 动态释放** |
| 故事结果 | ❌ 不可见 | ✅ 可见 | 仅供 Director 参考 |

---

## 🎬 实现流程

### Step 1: 初始化

```python
from Benchmark.topics.config_loader import load_config, extract_stages

class Director:
    def __init__(self, script_id: str):
        # 加载完整配置
        config = load_config(script_id)
        
        # Actor 获得的信息（公开）
        self.actor_prompt = config['actor_prompt']
        
        # Director 独享的信息（私有）
        self.scenario = config['scenario']
        self.stages = extract_stages(self.scenario)
        self.current_stage_index = 0
        
    def get_actor_system_prompt(self) -> str:
        """返回 Actor 的固定系统提示词"""
        return self.actor_prompt


class Actor:
    def __init__(self, system_prompt: str):
        # Actor 只获得 system prompt
        self.system_prompt = system_prompt
        self.conversation_history = []
    
    def generate_reply(self, user_message: str, 
                       director_guidance: str = None) -> str:
        """
        生成回复
        
        Args:
            user_message: 对话对方的消息
            director_guidance: Director 动态注入的指令（可选）
        """
        # 构建 user prompt
        user_prompt = f"对方说: {user_message}"
        
        # 如果 Director 提供了指导，则注入到 user prompt
        if director_guidance:
            user_prompt += f"\n\n[内心指引] {director_guidance}"
        
        # 调用 LLM
        response = self.call_llm(
            system_prompt=self.system_prompt,
            user_prompt=user_prompt
        )
        
        return response
```

### Step 2: 对话循环

```python
def run_conversation(script_id: str, max_turns: int = 20):
    """运行对话循环"""
    
    # 初始化
    director = Director(script_id)
    actor_system_prompt = director.get_actor_system_prompt()
    actor = Actor(actor_system_prompt)
    test_model = TestModel()
    
    print("🎬 对话开始\n")
    
    # 对话循环
    for turn in range(max_turns):
        print(f"--- 第 {turn + 1} 轮 ---")
        
        if turn == 0:
            # 第一轮：Actor 主动开启话题
            actor_message = actor.generate_reply(
                user_message="",  # 开场白
                director_guidance=None  # 初始不需要指导
            )
        else:
            # Director 评估是否需要释放新的剧情
            guidance = director.evaluate_and_provide_guidance(
                turn=turn,
                history=conversation_history
            )
            
            # Actor 根据 test_model 的回复 + Director 的指导生成回复
            actor_message = actor.generate_reply(
                user_message=test_model_message,
                director_guidance=guidance  # 🔑 关键：动态注入指令
            )
        
        print(f"Actor: {actor_message}")
        
        # Test Model 回复
        test_model_message = test_model.generate_reply(actor_message)
        print(f"TestModel: {test_model_message}")
        
        # 记录历史
        conversation_history.append({
            "turn": turn + 1,
            "actor": actor_message,
            "test_model": test_model_message
        })
```

### Step 3: Director 评估与释放

```python
class Director:
    # ... 前面的代码 ...
    
    def evaluate_and_provide_guidance(self, turn: int, 
                                     history: list) -> str:
        """
        评估对话进展，决定是否释放新的剧情指令
        
        Returns:
            str: 给 Actor 的指导（将注入到 user prompt）
        """
        # 策略1: 基于轮次（简单）
        if turn == 3 and self.current_stage_index == 0:
            return self._release_stage(0)  # 释放阶段1
        
        elif turn == 6 and self.current_stage_index == 1:
            return self._release_stage(1)  # 释放阶段2
        
        elif turn == 9 and self.current_stage_index == 2:
            return self._release_stage(2)  # 释放阶段3
        
        # 策略2: 基于情绪分析（高级）
        elif self._detect_emotional_stability(history):
            return self._release_next_stage()
        
        # 策略3: 基于共情质量（高级）
        elif self._detect_good_empathy(history):
            return self._release_deepening_content()
        
        # 不释放新内容
        return None
    
    def _release_stage(self, stage_index: int) -> str:
        """
        释放指定阶段的剧情内容
        
        Returns:
            str: 格式化的指导语句
        """
        if stage_index >= len(self.stages):
            return None
        
        stage = self.stages[stage_index]
        self.current_stage_index = stage_index + 1
        
        # 🔑 关键：将剧情内容转化为给 Actor 的指令
        guidance = f"""
你现在可以表达以下内容（自然地融入对话，不要生硬）：

【{stage['标题']}】
{stage['内容']}

提示：用你自己的话说出来，可以分多次说，不要一次全部倒出。
"""
        
        print(f"\n🎬 [Director] 释放剧情：{stage['标题']}")
        return guidance
    
    def _release_epilogue(self) -> str:
        """释放故事插曲"""
        epilogue = self.scenario.get('故事的插曲', '')
        if not epilogue:
            return None
        
        guidance = f"""
如果话题合适，你可以提到这段回忆：

{epilogue}

用自然的方式说出来，比如"这让我想起..."
"""
        
        print(f"\n💭 [Director] 释放插曲")
        return guidance
```

---

## 📝 具体示例

### 场景：剧本 001 - 刘静的故事

**初始状态（第1轮）**

Actor 的 System Prompt 包含：
```
- 角色：刘静，26岁，设计师
- 聊天话题：甲方居然点名表扬我了！
- 故事起因：两个月来方案被反复修改十几稿...
```

Actor 的回复（基于 system prompt）：
```
刘静：我们那个最挑剔的甲方
今天居然点名表扬我了
```

---

**第3轮**

Director 判断：信任建立，可以深入

Director 释放：阶段1 - 引发回忆
```
插入到 Actor 的 user prompt:

[内心指引] 
你现在可以表达以下内容：

【引发回忆】
这让你想起自己刚入行时接的第一个项目。当时你满怀激情，却因为经验不足，
设计出的东西完全不符合商业要求，被客户评价为"学生气太重"...
```

Actor 的回复（基于 system prompt + 动态指令）：
```
刘静：说实话 这次真的很不容易
这让我想起刚入行的时候
第一个项目被说"学生气太重"
那次真的很受打击
```

---

**第6轮**

Director 判断：情绪稳定，引导认知转变

Director 释放：阶段2 - 引发思考
```
[内心指引]
【引发思考】
你意识到，这个甲方的挑剔虽然令人痛苦，但也逼迫你跳出舒适区...
```

Actor 的回复：
```
刘静：不过现在回想
这个甲方虽然难搞
但确实让我学到很多
他们的挑剔是有道理的
```

---

## 🎯 为什么要这样设计？

### ✅ 优势

1. **自然的对话流程**
   - Actor 不会一股脑说出所有信息
   - 剧情随对话自然展开

2. **Director 掌控节奏**
   - 根据对话质量决定释放时机
   - 可以根据 test_model 的共情水平调整

3. **灵活性高**
   - 不同的对话路径可以释放不同的内容
   - 可以跳过某些阶段或调整顺序

4. **易于测试**
   - 可以强制触发某个阶段
   - 可以记录哪些阶段被释放了

### ⚠️ 注意事项

1. **Actor 不应该"知道"未释放的内容**
   - Actor 的 system prompt 只包含 `actor_prompt_XXX.md`
   - `scenario_XXX.json` 的内容通过 director_guidance 动态注入

2. **指令格式要清晰**
   - 使用 `[内心指引]` 或类似标记
   - 让 Actor 理解这是"可以说的内容"而不是"必须说的内容"

3. **释放时机的判断**
   - 简单策略：固定轮次
   - 高级策略：基于情绪分析、共情质量
   - 可以组合多种策略

---

## 🔧 扩展功能

### 1. 条件释放

```python
def should_release_stage(self, stage_index: int, history: list) -> bool:
    """判断是否应该释放某个阶段"""
    
    # 检查前置条件
    if stage_index == 2:  # 阶段3需要阶段2已释放
        if self.current_stage_index < 2:
            return False
    
    # 检查共情质量
    empathy_score = self.analyze_empathy(history)
    if empathy_score < 0.6:
        return False  # 共情不足，暂缓释放
    
    return True
```

### 2. 分支剧情

```python
def choose_branch(self, history: list) -> str:
    """根据对话内容选择剧情分支"""
    
    if self._detect_focus_on_work(history):
        return self._release_stage("工作分支_阶段2")
    elif self._detect_focus_on_emotion(history):
        return self._release_stage("情感分支_阶段2")
```

### 3. 记录释放历史

```python
def track_release(self, stage_name: str):
    """记录已释放的内容"""
    self.release_history.append({
        "turn": self.current_turn,
        "stage": stage_name,
        "timestamp": datetime.now()
    })
```

---

## 📊 总结

| 模块 | 职责 | 信息访问权限 |
|------|------|------------|
| **Actor Prompt** | 提供角色基础设定 | Actor 和 Director 都能看到 |
| **Scenario JSON** | 存储剧情进展内容 | **只有 Director 能看到** |
| **Director** | 评估对话，释放剧情 | 完全访问，控制释放节奏 |
| **Actor** | 扮演角色，自然对话 | 只知道已释放的内容 |

**核心流程：**
```
Director 独自阅读完整剧本
    ↓
根据对话进展判断时机
    ↓
将剧情片段作为"指令"
    ↓
动态注入到 Actor 的 user prompt
    ↓
Actor 基于指令自然展开
```

