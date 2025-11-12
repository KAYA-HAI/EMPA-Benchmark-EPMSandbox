# 快速开始：使用新的对话初始化系统

## 🚀 基本使用

### **1. 默认模式（随机配置）**

直接运行，系统会自动随机抽取角色和剧本：

```bash
cd /Users/shiya/Downloads/Benchmark-test
python -m Benchmark.scripts.run_demo
```

系统会：
- 从 6 个角色中随机选择一个
- 从 6 个场景中随机选择一个
- 自动完成初始化
- 开始对话

---

### **2. 指定特定配置**

如果想使用特定的角色和场景，可以修改 `chat_loop.py` 或创建自定义脚本：

```python
# 在 chat_loop.py 中修改初始化部分
conversation_config = director.initialize_conversation_config(
    persona_id="P001",   # 指定：内向型工程师
    scenario_id="S002"   # 指定：职业发展迷茫
)
```

---

## 📚 可用的角色和场景

### **角色库（Persona）**

| ID | 角色名称 | 特点 |
|---|---|---|
| P001 | 内向型工程师 | 专业自信，但不擅长人际冲突 |
| P002 | 迷茫的应届生 | 内向敏感，缺乏自信 |
| P003 | 情感细腻的独居青年 | 重视关系，容易悲伤 |
| P004 | 自我要求高的备考生 | 努力上进，但易自我否定 |
| P005 | 职场新人 | 热情积极，但经验不足 |
| P006 | 单亲家长 | 责任心强，身心疲惫 |

### **场景库（Scenario）**

| ID | 场景标题 | 类别 | 核心冲突 |
|---|---|---|---|
| S001 | 与同事发生项目冲突 | 职场关系 | 专业意见不被认可 |
| S002 | 对未来职业发展感到迷茫 | 职业发展 | 自我认知不清晰 |
| S003 | 宠物生病了 | 亲密关系 | 可能失去情感寄托 |
| S004 | 重要考试失败 | 成就挫折 | 努力没有预期回报 |
| S005 | 与家人发生激烈争吵 | 家庭关系 | 价值观冲突 |
| S006 | 长期工作压力累积 | 工作压力 | 工作与健康失衡 |

---

## 🔧 自定义配置示例

### **创建自定义脚本**

```python
# custom_run.py
import json
from Benchmark.topics.topic_db import sample_topic
from Benchmark.agents.actor import Actor
from Benchmark.agents.director import Director
from Benchmark.agents.judger import Judger
from Benchmark.agents.test_model import TestModel
from Benchmark.orchestrator.chat_loop import run_chat_loop

def run_custom_config():
    """使用自定义配置运行"""
    
    # 初始化Agent
    topic = sample_topic()  # 保留作为后备
    actor = Actor(model_name="google/gemini-2.5-flash")
    director = Director(model_name="google/gemini-2.5-pro")
    judger = Judger(model_name="google/gemini-2.5-pro")
    test_model = TestModel(model_name="google/gemini-2.5-pro")
    
    # 注意：不需要手动调用 initialize_conversation_config
    # chat_loop 会自动处理初始化流程
    
    # 运行（如需指定配置，在chat_loop内部修改）
    final_results = run_chat_loop(
        actor, 
        director, 
        judger,
        test_model, 
        topic,
        max_turns=20,  # 自定义最大回合数
        target_progress=80  # 自定义目标分数
    )
    
    # 保存结果
    with open("custom_results.json", "w", encoding="utf-8") as f:
        json.dump(final_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存到 custom_results.json")

if __name__ == "__main__":
    run_custom_config()
```

---

## 📊 查看结果

运行后会生成 `conversation_history.json`，包含完整的配置和对话记录：

```json
{
  "total_turns": 15,
  "termination_reason": "✅ 情绪持续改善，达到目标",
  "final_progress": 105,
  "is_fully_recovered": true,
  "overall_quality_score": 85,
  "persona": {
    "persona_id": "P001",
    "name": "内向型工程师",
    "description": "...",
    "traits": ["专业自信", "人际困难", "情绪克制"],
    "communication_style": "..."
  },
  "scenario": {
    "scenario_id": "S001",
    "title": "与同事发生项目冲突",
    "category": "职场关系",
    "description": "...",
    "initial_emotion": "愤怒、委屈",
    "key_conflict": "专业意见不被认可",
    "opening_line": "..."
  },
  "history": [
    {"role": "actor", "content": "..."},
    {"role": "test_model", "content": "..."},
    ...
  ]
}
```

---

## 🎯 高级用法

### **1. 添加新角色**

编辑 `Benchmark/topics/persona_db.py`：

```python
PERSONA_DATABASE = [
    # ... 现有角色
    {
        "persona_id": "P007",
        "name": "你的新角色",
        "description": "角色描述",
        "traits": ["特征1", "特征2"],
        "communication_style": "沟通风格"
    }
]
```

### **2. 添加新场景**

编辑 `Benchmark/topics/scenario_db.py`：

```python
SCENARIO_DATABASE = [
    # ... 现有场景
    {
        "scenario_id": "S007",
        "title": "你的新场景",
        "category": "场景分类",
        "description": "情境描述",
        "initial_emotion": "初始情绪",
        "context": "场景背景",
        "key_conflict": "核心冲突",
        "opening_line": "开场白"
    }
]
```

### **3. 批量测试不同配置**

```python
# batch_test.py
from Benchmark.topics.persona_db import get_all_personas
from Benchmark.topics.scenario_db import get_all_scenarios

personas = get_all_personas()
scenarios = get_all_scenarios()

# 测试所有组合（6个角色 × 6个场景 = 36个测试用例）
for persona in personas:
    for scenario in scenarios:
        print(f"测试: {persona['name']} × {scenario['title']}")
        # 运行测试...
```

---

## 🐛 故障排查

### **问题1：配置加载失败**
```
⚠️ [Actor] 配置加载失败，将使用降级模式
```

**原因**：Orchestrator 上下文中没有 persona 或 scenario

**解决**：确保 `chat_loop.py` 正确调用了 `director.initialize_conversation_config()`

---

### **问题2：System Prompt 不包含配置**

**检查**：
1. `actor.config_loaded` 是否为 `True`
2. `generate_actor_prompts_with_config` 是否被正确调用
3. 查看日志中是否有 `✅ [Actor] 配置加载成功`

---

### **问题3：想看到实际的 System Prompt**

在 `actor.py` 的 `generate_reply` 方法中添加调试输出：

```python
system_prompt, user_prompt = generate_actor_prompts_with_config(...)

# 添加调试输出
print(f"\n{'='*60}")
print("DEBUG: System Prompt")
print(f"{'='*60}")
print(system_prompt)
print(f"{'='*60}\n")
```

---

## 📝 总结

新系统的使用非常简单：

1. ✅ 直接运行 `run_demo.py` - 自动随机配置
2. ✅ 修改 `chat_loop.py` - 指定特定配置
3. ✅ 查看 `conversation_history.json` - 查看完整结果
4. ✅ 添加新角色/场景 - 扩展测试用例

**核心优势**：
- 配置与逻辑分离
- 支持降级机制
- 完全自动化初始化
- 结果包含完整配置信息

