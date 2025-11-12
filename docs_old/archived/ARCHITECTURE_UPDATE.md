# 架构更新说明：对话初始化流程

## 📋 更新概述

本次更新实现了新的对话初始化机制，引入了 **角色库（Persona）** 和 **剧本库（Scenario）** 的概念，使得User Agent（Actor）在对话开始前通过Director从库中获取配置。

---

## 🔄 新的初始化流程

### **完整流程图**

```
1. run_demo启动
   ↓
2. 创建所有Agent实例
   ↓
3. 进入chat_loop
   ↓
4. [初始化阶段开始]
   ├─ Actor 隐式请求 Director
   ├─ Director 调用 initialize_conversation_config()
   │  ├─ 从 persona_db 抽取角色
   │  └─ 从 scenario_db 抽取剧本
   ├─ Director 生成配置并返回
   ├─ Orchestrator 接收配置存入 ConversationContext
   │  ├─ persona 变量
   │  └─ scenario 变量
   └─ Actor 调用 request_and_load_config(context)
      └─ 从 context 读取 persona 和 scenario
   ↓
5. [对话阶段开始]
   └─ Actor 使用配置生成带有角色设定的回复
```

---

## 📦 新增文件

### **1. 角色库：`Benchmark/topics/persona_db.py`**

定义了6种不同的用户人设：

- **P001**: 内向型工程师
- **P002**: 迷茫的应届生
- **P003**: 情感细腻的独居青年
- **P004**: 自我要求高的备考生
- **P005**: 职场新人
- **P006**: 单亲家长

**数据结构**：
```python
{
    "persona_id": "P001",
    "name": "内向型工程师",
    "description": "角色的详细描述",
    "traits": ["特征1", "特征2", ...],
    "communication_style": "沟通风格描述"
}
```

**主要函数**：
- `sample_persona()` - 随机采样角色
- `get_persona_by_id(persona_id)` - 根据ID获取角色
- `get_all_personas()` - 获取所有角色

---

### **2. 剧本库：`Benchmark/topics/scenario_db.py`**

定义了6种不同的情境场景：

- **S001**: 与同事发生项目冲突
- **S002**: 对未来职业发展感到迷茫
- **S003**: 宠物生病了
- **S004**: 重要考试失败
- **S005**: 与家人发生激烈争吵
- **S006**: 长期工作压力累积

**数据结构**：
```python
{
    "scenario_id": "S001",
    "title": "场景标题",
    "category": "场景分类",
    "description": "情境描述",
    "initial_emotion": "初始情绪",
    "context": "场景背景",
    "key_conflict": "核心冲突",
    "opening_line": "开场白"
}
```

**主要函数**：
- `sample_scenario()` - 随机采样场景
- `get_scenario_by_id(scenario_id)` - 根据ID获取场景
- `get_scenarios_by_category(category)` - 按类别获取
- `get_all_scenarios()` - 获取所有场景

---

## 🔧 修改的文件

### **1. `Benchmark/agents/director.py`**

**新增方法**：
```python
def initialize_conversation_config(
    self, 
    persona_id: str = None, 
    scenario_id: str = None
) -> dict:
    """
    初始化对话配置：从角色库和剧本库中抽取配置
    
    Returns:
        dict: {
            "persona": {...},
            "scenario": {...},
            "initialized_at": "conversation_start"
        }
    """
```

**功能**：
- 从 `persona_db` 抽取角色（支持指定ID或随机）
- 从 `scenario_db` 抽取剧本（支持指定ID或随机）
- 返回包含两者的配置字典

---

### **2. `Benchmark/agents/actor.py`**

**新增属性**：
```python
self.persona = None          # 角色配置
self.scenario = None         # 剧本配置
self.config_loaded = False   # 配置加载状态
```

**新增方法**：
```python
def request_and_load_config(self, orchestrator_context) -> bool:
    """从Orchestrator读取Director生成的配置"""
```

**修改方法**：
```python
def generate_reply(self, history: list, topic: dict = None) -> str:
    """使用从Orchestrator加载的persona和scenario生成回复"""
```

**功能变化**：
- Actor不再被动接收topic，而是主动从Orchestrator读取配置
- 回复生成时使用 persona 和 scenario 而非 topic

---

### **3. `Benchmark/prompts/actor_prompts.py`**

**新增函数**：
```python
def generate_actor_prompts_with_config(
    history: list,
    persona: dict = None,
    scenario: dict = None,
    task_guidance: str = None,
    topic: dict = None
) -> tuple:
    """使用Persona和Scenario配置生成Actor的prompts"""
```

**新增模板**：
- `ACTOR_SYSTEM_PROMPT_WITH_CONFIG` - 包含persona和scenario的system prompt
- `ACTOR_USER_PROMPT_WITH_CONFIG` - 包含对话历史和开场白的user prompt

**关键改进**：
✅ **Persona 和 Scenario 被放入 System Prompt**：
```
## 你的角色设定（Persona）
**角色名称**: {persona_name}
**角色描述**: {persona_description}
**性格特征**: {persona_traits}
**沟通风格**: {persona_communication_style}

## 你当前的情境（Scenario）
**场景**: {scenario_title}
**情境描述**: {scenario_description}
**你当前的情绪**: {scenario_emotion}
**核心冲突**: {scenario_conflict}
```

---

### **4. `Benchmark/orchestrator/chat_loop.py`**

**新增初始化流程**：
```python
# 1. Director生成配置
conversation_config = director.initialize_conversation_config()

# 2. 配置传递给Orchestrator（存入上下文）
context.set_variables(
    persona=conversation_config['persona'],
    scenario=conversation_config['scenario']
)

# 3. Actor从Orchestrator读取配置
actor_config_loaded = actor.request_and_load_config(context)
```

**修改返回结果**：
```python
return {
    ...,
    "persona": conversation_config['persona'],
    "scenario": conversation_config['scenario']
}
```

---

### **5. `Benchmark/scripts/run_demo.py`**

**更新报告输出**：
- 显示角色配置信息
- 显示剧本配置信息
- 配置信息保存到 `conversation_history.json`

---

## 🎯 核心改进点

### **1. 配置驱动的对话初始化**
- ✅ 从被动接收 topic 改为主动请求配置
- ✅ 通过 Director 统一管理配置生成
- ✅ 通过 Orchestrator 作为配置中转站

### **2. 角色和剧本分离**
- ✅ **Persona（角色）**：定义"谁在说话"
  - 性格特征、沟通风格、心理状态
- ✅ **Scenario（剧本）**：定义"在什么情况下说话"
  - 具体情境、情绪状态、冲突点

### **3. System Prompt增强**
- ✅ Persona 和 Scenario 直接注入 System Prompt
- ✅ Actor 可以保持更一致的角色扮演
- ✅ 对话更加自然和真实

### **4. 降级机制**
- ✅ 如果配置加载失败，自动降级到旧的 topic 模式
- ✅ 保证系统的鲁棒性

---

## 📊 对比：旧流程 vs 新流程

### **旧流程**
```python
# run_demo.py
topic = sample_topic()  # 直接采样
run_chat_loop(..., topic)

# chat_loop.py
actor.generate_reply(history, topic)  # 被动接收

# actor_prompts.py
system_prompt = f"你的困扰主题: {topic['title']}"
```

### **新流程**
```python
# chat_loop.py (初始化阶段)
config = director.initialize_conversation_config()
context.set_variables(persona=..., scenario=...)
actor.request_and_load_config(context)

# actor.py
self.persona = context.get_variable('persona')
self.scenario = context.get_variable('scenario')

# actor_prompts.py
system_prompt = f"""
## 你的角色设定（Persona）
{persona['name']}, {persona['description']}
## 你当前的情境（Scenario）  
{scenario['title']}, {scenario['description']}
"""
```

---

## 🚀 使用方式

### **基本用法（随机配置）**
```python
python -m Benchmark.scripts.run_demo
```

系统会自动：
1. 从角色库随机抽取一个角色
2. 从剧本库随机抽取一个场景
3. 将配置传递给Actor
4. 开始对话

### **指定配置（扩展）**
如需指定特定角色或场景，可以修改 `chat_loop.py`：

```python
# 指定角色和场景
conversation_config = director.initialize_conversation_config(
    persona_id="P001",  # 内向型工程师
    scenario_id="S001"  # 项目冲突
)
```

---

## 🔍 调试信息

运行时会输出以下日志：

```
🎬🎬🎬... [初始化阶段] Actor请求Director生成配置...

--- [Director] 正在初始化对话配置... ---
✅ [Director] 配置生成完成:
   角色: 内向型工程师 (P001)
   场景: 与同事发生项目冲突 (S001)

📦📦📦... [初始化阶段] Director配置已传递给Orchestrator

--- [Actor] 正在从Orchestrator请求配置... ---
✅ [Actor] 配置加载成功:
   角色: 内向型工程师
   场景: 与同事发生项目冲突

============================================================
✅ 初始化完成，开始对话
📋 角色: 内向型工程师
📋 场景: 与同事发生项目冲突
============================================================
```

---

## 📝 总结

本次更新实现了完整的"请求-生成-传递-读取"配置流程：

1. ✅ **Actor 请求** Director 生成配置
2. ✅ **Director 调用** 角色库和剧本库抽取配置
3. ✅ **Director 传递** 配置给 Orchestrator
4. ✅ **Actor 读取** Orchestrator 中的配置
5. ✅ **配置注入** Actor 的 System Prompt

整个流程清晰、模块化，符合您的需求！

