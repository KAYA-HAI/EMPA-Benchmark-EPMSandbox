# Director 更新总结

## 🎯 更新目标

适配新的配置加载系统，使 Director 能够：
1. 从 `config_loader` 加载剧本配置
2. 独享完整的故事阶段信息
3. 渐进式地释放阶段内容给 Actor

---

## ✅ 已完成的更新

### 1. **director.py** - 核心逻辑更新

#### 删除的内容：
- ❌ 删除了对 `persona_db` 和 `scenario_db_layered` 的导入
- ❌ 删除了 `initialize_conversation_config()` 方法（647行）

#### 修改的内容：
- ✅ 构造函数改为接收 `scenario` 参数
  ```python
  def __init__(self, scenario: dict, model_name: str = ...)
  ```

- ✅ 使用 `extract_stages()` 从 scenario 提取阶段
  ```python
  self.stages = extract_stages(scenario)
  ```

- ✅ 追踪已释放的阶段
  ```python
  self.revealed_stages = []  # 已释放的阶段索引列表
  self.current_stage_index = 0
  ```

#### 新增的内容：
- ✅ `release_epilogue()` - 释放故事插曲
- ✅ `get_story_result()` - 获取故事结果
- ✅ `get_remaining_stages()` - 获取未释放的阶段

#### 重写的方法：
- ✅ `evaluate_continuation()` - 使用新的 stages 结构
- ✅ `_handle_select_and_reveal_fragment()` - 适配阶段释放逻辑

---

### 2. **director_function_schemas_selector.py** - Function Schemas 更新

#### 修改的内容：
- ✅ 更新 `select_and_reveal_fragment` 函数定义
  - 旧参数：`fragment_category`, `fragment_index`
  - 新参数：`stage_index`
  
```python
{
    "name": "select_and_reveal_fragment",
    "parameters": {
        "stage_index": {
            "type": "integer",
            "description": "要释放的故事阶段索引（从0开始）"
        },
        "reason": {
            "type": "string"
        }
    }
}
```

---

### 3. **director_prompts.py** - Prompts 更新

#### 修改的内容：
- ✅ 更新 `DIRECTOR_PROMPT_TEMPLATE`
  - 强调 Director 独享故事阶段信息
  - 说明渐进式释放的设计
  - 更新决策建议

- ✅ 更新 `generate_director_prompt()` 函数
  - 旧参数：`available_fragments: dict`
  - 新参数：`available_stages: list`, `revealed_stages: list`

```python
def generate_director_prompt(
    progress: int, 
    history: list, 
    available_stages: list = None,  # 新
    revealed_stages: list = None    # 新
) -> str:
```

---

## 📊 新旧对比

### 旧的初始化方式（已废弃）
```python
# 旧方式
director = Director()
config = director.initialize_conversation_config(
    persona_id="P001",
    scenario_id="S001"
)
```

### 新的初始化方式（推荐）
```python
# 新方式
from Benchmark.topics.config_loader import load_scenario

scenario = load_scenario("001")
director = Director(scenario=scenario)
```

---

## 🔄 数据结构变化

### 旧的剧情结构
```json
{
  "plot_fragments": {
    "background": [
      {"id": "bg_001", "content": "..."}
    ],
    "conflict_details": [...],
    "emotional_impact": [...],
    "deep_layers": [...],
    "turning_points": [...]
  }
}
```

### 新的剧情结构
```json
{
  "剧本编号": "script_001",
  "故事的经过": {
    "阶段1": {
      "标题": "引发回忆",
      "内容": "..."
    },
    "阶段2": {
      "标题": "引发思考",
      "内容": "..."
    },
    ...
  },
  "故事的结果": "...",
  "故事的插曲": "..."
}
```

---

## 💡 使用示例

### 完整的初始化和使用流程

```python
from Benchmark.topics.config_loader import load_config
from Benchmark.agents.director import Director
from Benchmark.agents.actor import Actor

# 1. 加载配置
config = load_config("001")

# 2. 初始化 Actor（获得 actor_prompt）
actor = Actor(system_prompt=config['actor_prompt'])

# 3. 初始化 Director（获得 scenario）
director = Director(scenario=config['scenario'])

# 4. 对话循环
for turn in range(20):
    # Director 评估是否介入
    if director.should_intervene(history, turn, progress):
        # Director 决定释放哪个阶段
        result = director.evaluate_continuation(history, progress)
        
        if result.get('guidance'):
            # 将指令注入到 Actor 的 user prompt
            actor_message = actor.generate_reply(
                user_message=test_model_message,
                director_guidance=result['guidance']  # 动态注入
            )
```

---

## 🎬 释放机制说明

### Director 如何释放阶段

1. **LLM 选择阶段**
   ```python
   # LLM 调用函数
   select_and_reveal_fragment(
       stage_index=0,  # 选择第0个阶段
       reason="对话建立了信任，可以引入回忆"
   )
   ```

2. **Director 读取预设内容**
   ```python
   stage = self.stages[0]
   # {
   #   "阶段名": "阶段1",
   #   "标题": "引发回忆",
   #   "内容": "这让她想起自己刚入行时..."
   # }
   ```

3. **组装指令**
   ```python
   full_guidance = f"""
   【阶段1：引发回忆】
   
   剧情内容：
   {stage['内容']}
   
   表演指导：
   请自然地将上述内容融入对话中...
   """
   ```

4. **注入到 Actor**
   ```python
   # Actor 的 user prompt 包含：
   # 1. test_model 的回复
   # 2. Director 的指令（动态注入）
   actor.generate_reply(
       user_message=test_model_reply,
       director_guidance=full_guidance
   )
   ```

---

## 🔧 待办事项

- [ ] 更新 `chat_loop.py` 以使用新的 Director 初始化方式
- [ ] 更新 `run_demo.py` 以使用 config_loader
- [ ] 测试完整的对话流程
- [ ] 更新相关文档

---

## ⚠️ 破坏性变更

### 对现有代码的影响

1. **Director 构造函数签名变更**
   - 旧：`Director(model_name="...")`
   - 新：`Director(scenario=..., model_name="...")`
   - **影响**：所有创建 Director 实例的代码都需要更新

2. **删除的方法**
   - `initialize_conversation_config()` 已删除
   - **影响**：依赖此方法的代码需要改用 `config_loader`

3. **Function Call 参数变更**
   - 旧：`fragment_category`, `fragment_index`
   - 新：`stage_index`
   - **影响**：LLM 的响应格式会变化

---

## ✅ 兼容性

- ✅ 保留了 `use_function_calling` 参数
- ✅ 保留了 `should_intervene()` 方法
- ✅ 保留了 `evaluate_continuation()` 方法签名（参数相同）
- ✅ 返回的数据格式保持一致

---

**更新日期**：2025-10-27  
**版本**：2.0 - 适配新配置系统

