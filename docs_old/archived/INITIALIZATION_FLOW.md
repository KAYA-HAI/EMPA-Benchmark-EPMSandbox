# 对话初始化流程详解

## 🎯 核心需求实现

> **你的需求**：在对话开始时，user agent（Actor）需要请求 director agent 调取话题库和角色库抽取角色和剧本信息，director agent 会根据抽取结果生成角色和剧本，并传递给 orchestrator；然后 user agent 从 orchestrator 读取角色（persona变量）和剧本（scenario变量），将这些变量内容放置在 user agent 的 system prompt 里。

✅ **已完整实现！**

---

## 📊 详细流程图

```
┌────────────────────────────────────────────────────────────────┐
│                      1. 系统启动阶段                             │
│                   run_demo.py 执行                              │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│                   2. 创建 Agent 实例                            │
│  actor = Actor()                                               │
│  director = Director()                                         │
│  judger = Judger()                                             │
│  test_model = TestModel()                                      │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│                   3. 进入 chat_loop                             │
│                   run_chat_loop(...) 开始执行                   │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│         🎬 [初始化阶段] - 对话配置生成                          │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────┐
         │  4. Actor 隐式请求 Director       │
         │     （在 chat_loop 中触发）       │
         └───────────────┬───────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────────────────┐
         │  5. Director 生成配置                          │
         │     director.initialize_conversation_config()  │
         └───────────────┬───────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ↓                               ↓
┌────────────────────┐        ┌──────────────────────┐
│  从角色库抽取       │        │  从剧本库抽取         │
│  persona_db.py     │        │  scenario_db.py      │
│                    │        │                      │
│  sample_persona()  │        │  sample_scenario()   │
└────────┬───────────┘        └──────────┬───────────┘
         │                               │
         └───────────────┬───────────────┘
                         ↓
         ┌───────────────────────────────────┐
         │  6. Director 返回配置字典          │
         │  {                                │
         │    "persona": {...},              │
         │    "scenario": {...}              │
         │  }                                │
         └───────────────┬───────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────────┐
         │  7. 配置传递给 Orchestrator            │
         │     context.set_variables(             │
         │       persona=...,                     │
         │       scenario=...                     │
         │     )                                  │
         └───────────────┬───────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────────────┐
         │  8. Actor 从 Orchestrator 读取配置        │
         │     actor.request_and_load_config(context)│
         │                                           │
         │     self.persona = context.get('persona') │
         │     self.scenario = context.get('scenario')│
         └───────────────┬───────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│         ✅ [初始化完成] - 配置已加载                            │
│         Actor 已获取:                                          │
│         - persona（角色）变量                                   │
│         - scenario（剧本）变量                                  │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ↓
┌────────────────────────────────────────────────────────────────┐
│         🎭 [对话阶段] - 开始对话循环                           │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────────┐
         │  9. Actor 生成回复                     │
         │     actor.generate_reply(history)      │
         └───────────────┬───────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────────────────┐
         │  10. 生成 Prompt（包含配置）                   │
         │      generate_actor_prompts_with_config(       │
         │        history=history,                        │
         │        persona=self.persona,  ← 从配置读取     │
         │        scenario=self.scenario ← 从配置读取     │
         │      )                                         │
         └───────────────┬───────────────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────────────────┐
         │  11. System Prompt 包含 Persona & Scenario    │
         │                                               │
         │  ## 你的角色设定（Persona）                    │
         │  角色名称: {persona['name']}                  │
         │  角色描述: {persona['description']}           │
         │  性格特征: {persona['traits']}                │
         │  沟通风格: {persona['communication_style']}   │
         │                                               │
         │  ## 你当前的情境（Scenario）                   │
         │  场景: {scenario['title']}                    │
         │  情境描述: {scenario['description']}          │
         │  当前情绪: {scenario['initial_emotion']}      │
         │  核心冲突: {scenario['key_conflict']}         │
         └───────────────┬───────────────────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────┐
         │  12. 发送给 LLM API                │
         │      get_llm_response(messages)    │
         └───────────────┬───────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────┐
         │  13. Actor 返回回复                │
         └───────────────┬───────────────────┘
                         │
                         ↓
         ┌───────────────────────────────────┐
         │  14. 对话继续（循环）              │
         └───────────────────────────────────┘
```

---

## 🔍 关键代码路径

### **初始化阶段代码追踪**

#### **1️⃣ 入口：`chat_loop.py`**
```python
def run_chat_loop(actor, director, judger, test_model, topic, ...):
    # === 初始化阶段 ===
    
    # Step 1: Director 生成配置
    conversation_config = director.initialize_conversation_config()
    # 返回: {"persona": {...}, "scenario": {...}}
    
    # Step 2: 传递给 Orchestrator
    context = ConversationContext()
    context.set_variables(
        persona=conversation_config['persona'],
        scenario=conversation_config['scenario']
    )
    
    # Step 3: Actor 读取配置
    actor.request_and_load_config(context)
```

#### **2️⃣ Director：`director.py`**
```python
def initialize_conversation_config(self, persona_id=None, scenario_id=None):
    # 从角色库抽取
    persona = sample_persona() if not persona_id else get_persona_by_id(persona_id)
    
    # 从剧本库抽取
    scenario = sample_scenario() if not scenario_id else get_scenario_by_id(scenario_id)
    
    return {
        "persona": persona,
        "scenario": scenario,
        "initialized_at": "conversation_start"
    }
```

#### **3️⃣ Actor：`actor.py`**
```python
def request_and_load_config(self, orchestrator_context):
    # 从 Orchestrator 上下文读取
    self.persona = orchestrator_context.get_variable('persona')
    self.scenario = orchestrator_context.get_variable('scenario')
    self.config_loaded = True
```

#### **4️⃣ Prompt 生成：`actor_prompts.py`**
```python
def generate_actor_prompts_with_config(history, persona, scenario, ...):
    # === System Prompt：将 persona 和 scenario 注入 ===
    system_prompt = ACTOR_SYSTEM_PROMPT_WITH_CONFIG.format(
        persona_name=persona['name'],
        persona_description=persona['description'],
        persona_traits='、'.join(persona['traits']),
        persona_communication_style=persona['communication_style'],
        scenario_title=scenario['title'],
        scenario_description=scenario['description'],
        scenario_emotion=scenario['initial_emotion'],
        scenario_conflict=scenario['key_conflict']
    )
    
    return system_prompt, user_prompt
```

---

## 📦 数据流图

```
┌─────────────┐
│ persona_db  │──┐
│  (角色库)   │  │
└─────────────┘  │
                 │
┌─────────────┐  │    ┌──────────────┐
│ scenario_db │──┼───→│   Director   │
│  (剧本库)   │  │    │   抽取配置   │
└─────────────┘  │    └──────┬───────┘
                 │           │
                 │           ↓
                 │    ┌──────────────────┐
                 │    │  config = {      │
                 │    │    persona: {},  │
                 │    │    scenario: {}  │
                 └───→│  }               │
                      └──────┬───────────┘
                             │
                             ↓
                      ┌──────────────────┐
                      │  Orchestrator    │
                      │  (ConversationContext)│
                      │                  │
                      │  variables = {   │
                      │    persona: {...}│
                      │    scenario: {...}│
                      │  }               │
                      └──────┬───────────┘
                             │
                             ↓
                      ┌──────────────────┐
                      │     Actor        │
                      │  request_and_load_config()│
                      │                  │
                      │  self.persona    │
                      │  self.scenario   │
                      └──────┬───────────┘
                             │
                             ↓
                      ┌──────────────────┐
                      │  System Prompt   │
                      │  包含:            │
                      │  - Persona 信息  │
                      │  - Scenario 信息 │
                      └──────────────────┘
```

---

## 🎨 System Prompt 示例

### **最终生成的 System Prompt 内容：**

```markdown
## 你的角色设定（Persona）

**角色名称**: 内向型工程师
**角色描述**: 一个对自己专业能力很自信，但不太擅长处理人际冲突的初级工程师。性格内向，表达情绪时会比较克制。

**性格特征**: 专业自信、人际困难、情绪克制
**沟通风格**: 理性但偶尔会流露出委屈和无助

## 你当前的情境（Scenario）

**场景**: 与同事发生项目冲突
**类别**: 职场关系
**情境描述**: 在工作会议上，因为项目设计方案与同事产生了激烈争执，对方完全不听自己的想法，导致自己感到既生气又委屈。

**你当前的情绪**: 愤怒、委屈
**核心冲突**: 专业意见不被认可

## 你的任务

你是一个真实的、有情绪困扰的人，正在向AI助手倾诉你的烦恼。
请根据你的角色设定和当前情境，自然地表达你的情感和想法。

**重要原则**：
- 保持角色一致性，按照你的性格特征和沟通风格来表达
- 真实地体现当前的情绪状态
- 回复要简洁自然，每次不超过100字
- 不要使用括号或动作描写
- 随着对话进展，情绪可以逐渐变化
```

---

## ✅ 验证清单

### **确认你的需求已实现：**

- ✅ **User Agent（Actor）请求 Director**
  - 在 `chat_loop.py` 中调用 `director.initialize_conversation_config()`
  
- ✅ **Director 调取话题库和角色库**
  - `director.py` 中调用 `sample_persona()` 和 `sample_scenario()`
  
- ✅ **Director 生成角色和剧本**
  - 返回包含 `persona` 和 `scenario` 的配置字典
  
- ✅ **配置传递给 Orchestrator**
  - 通过 `context.set_variables()` 存储到 `ConversationContext`
  
- ✅ **Actor 从 Orchestrator 读取配置**
  - 调用 `actor.request_and_load_config(context)`
  - 读取 `persona` 和 `scenario` 变量
  
- ✅ **配置放置在 System Prompt**
  - `generate_actor_prompts_with_config()` 将配置注入 System Prompt

---

## 🚀 运行示例

运行时会看到如下输出：

```
============================================================
🎭 Benchmark 开始
============================================================

🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬
🎬 [初始化阶段] Actor请求Director生成配置...
🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬🎬

--- [Director] 正在初始化对话配置... ---
✅ [Director] 配置生成完成:
   角色: 内向型工程师 (P001)
   场景: 与同事发生项目冲突 (S001)

📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦
📦 [初始化阶段] Director配置已传递给Orchestrator
📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦📦

--- [Actor] 正在从Orchestrator请求配置... ---
✅ [Actor] 配置加载成功:
   角色: 内向型工程师
   场景: 与同事发生项目冲突

============================================================
✅ 初始化完成，开始对话
📋 角色: 内向型工程师
📋 场景: 与同事发生项目冲突
🎯 目标: 通过Director+Judger指导优化共情对话质量
⏱️  最大回合数: 30
============================================================
```

---

## 📝 总结

整个流程完全按照你的需求实现：

1. ✅ User Agent（Actor）在对话开始时请求 Director
2. ✅ Director 从角色库和剧本库抽取配置
3. ✅ Director 生成 persona 和 scenario
4. ✅ 配置通过 Orchestrator 传递
5. ✅ Actor 从 Orchestrator 读取 persona 和 scenario 变量
6. ✅ 这些变量被放置在 Actor 的 System Prompt 中

**核心实现文件：**
- `topics/persona_db.py` - 角色库
- `topics/scenario_db.py` - 剧本库
- `agents/director.py` - 配置生成
- `orchestrator/chat_loop.py` - 流程编排
- `agents/actor.py` - 配置读取
- `prompts/actor_prompts.py` - Prompt 注入

