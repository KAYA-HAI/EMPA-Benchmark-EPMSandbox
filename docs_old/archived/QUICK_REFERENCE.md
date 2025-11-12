# Director 功能快速参考

## 🚀 快速开始

```python
from Benchmark.topics.config_loader import load_config
from Benchmark.agents.director import Director

# 加载配置
config = load_config("001")

# 初始化 Director（需要两个参数）
director = Director(
    scenario=config['scenario'],
    actor_prompt=config['actor_prompt']
)
```

---

## 📊 三个维度一览

| 维度 | 来源 | 可控内容 | 函数 |
|------|------|---------|------|
| 📖 **剧情** | scenario.json | 4个故事阶段 + 插曲 | `select_and_reveal_fragment` |
| 💭 **记忆** | actor_prompt - experience | 童年/少年/青年/现状 | `reveal_memory` |
| 🎭 **策略** | actor_prompt - psychological_profile | 动机/情感/认知共情 | `adjust_empathy_strategy` |

---

## 🔧 7个函数速查

### 核心功能（⭐）

```python
# 1. 释放故事阶段
select_and_reveal_fragment(stage_index=0, reason="...")

# 2. 释放角色记忆（新）
reveal_memory(memory_period="少年经历", reason="...")

# 3. 调整共情策略（新）
adjust_empathy_strategy(focus_aspect="动机共情", reason="...")

# 4. 综合转折（增强）
introduce_turning_point(
    stage_index=2,  # 剧情阶段（-1=不释放）
    empathy_aspect="认知共情",  # 共情方向
    reason="..."
)
```

### 控制功能

```python
# 5. 暂不介入
observe_and_wait(observation="...", wait_reason="...")

# 6. 给建议不释放
continue_without_new_info(focus_suggestion="...", reason="...")

# 7. 结束对话
end_conversation(reason="...")
```

---

## 💡 常用场景

| 场景 | 使用函数 | 参数示例 |
|------|---------|---------|
| 对话刚开始 | `observe_and_wait` | - |
| 建立信任后 | `select_and_reveal_fragment` | `stage_index=0` |
| AI共情浅显 | `adjust_empathy_strategy` | `focus_aspect="动机共情"` |
| 需要增加深度 | `reveal_memory` | `memory_period="少年经历"` |
| 关键转折 | `introduce_turning_point` | `stage_index=2, empathy_aspect="认知共情"` |
| 挖掘根源 | `reveal_memory` | `memory_period="童年经历"` |
| 情绪恢复 | `end_conversation` | - |

---

## 📖 故事阶段（script_001）

| 索引 | 阶段名 | 标题 | 时机 |
|------|--------|------|------|
| 0 | 阶段1 | 引发回忆 | 对话初期（进度10-30） |
| 1 | 阶段2 | 引发思考 | 对话中期（进度30-50） |
| 2 | 阶段3 | 引发自审 | 对话深入（进度50-70） |
| 3 | 阶段4 | 情绪崩发 | 情绪高潮（进度70-90） |

---

## 💭 记忆时期（actor_prompt - experience）

| 时期 | 内容 | 适用场景 |
|------|------|---------|
| 童年经历 | 别人家的孩子，习惯被表扬 | 挖掘深层动因 |
| 少年经历 | 辩论赛失利，害怕失败 | 失败与成功的对比 |
| 青年经历 | 实习被批评，自我苛刻 | 职场挫折的共鸣 |
| 角色现状 | 广告公司设计师 | 当前状况说明 |

---

## 🎭 共情方向（psychological_profile）

| 方向 | 重点 | 使用时机 |
|------|------|---------|
| 动机共情 | 付出、坚持、专业精神 | AI共情浅显时 |
| 情感共情 | 喜悦、释放感、情绪 | 需要情感共鸣时 |
| 认知共情 | 成长、转变、自信提升 | 对话深入时 |

---

## 🎬 典型流程

### 标准流程（4阶段）
```
第3轮: 阶段1（引发回忆）
第6轮: 阶段2（引发思考）
第9轮: 阶段3（引发自审）
第12轮: 阶段4（情绪崩发）
```

### 增强流程（阶段+记忆）
```
第3轮: 阶段1
第5轮: 记忆（少年）← 增加深度
第8轮: 阶段2
第11轮: 记忆（童年）← 挖掘根源
第14轮: 阶段4
```

### 动态流程（根据AI调整）
```
第3轮: 阶段1
第4轮: AI好 → 观察
第6轮: 阶段2
第7轮: AI差 → 策略（动机共情）
第10轮: 综合转折（阶段3 + 认知共情）
```

---

## ⚡ 快速决策指南

### 对话初期（进度 < 30）
- ✅ `observe_and_wait` - 观察
- ✅ `select_and_reveal_fragment(0)` - 阶段1
- ⚠️ 暂不用记忆和策略调整

### 对话中期（进度 30-60）
- ✅ `select_and_reveal_fragment(1-2)` - 阶段2-3
- ✅ `reveal_memory("少年/青年")` - 增加深度
- ✅ `adjust_empathy_strategy` - 如果AI共情不够

### 对话深入（进度 60-90）
- ✅ `introduce_turning_point` - 综合转折
- ✅ `reveal_memory("童年")` - 挖掘根源
- ✅ `select_and_reveal_fragment(3)` - 阶段4（高潮）

### 接近结束（进度 > 90）
- ✅ `release_epilogue` - 故事插曲
- ✅ `end_conversation` - 结束

---

## 🧪 测试命令

```bash
# 测试增强功能
python3 test_director_enhanced.py

# 测试配置加载
python3 -m Benchmark.topics.config_loader
```

---

## 📚 完整文档

- **[DIRECTOR_ENHANCED_FEATURES.md](./DIRECTOR_ENHANCED_FEATURES.md)** - 详细功能说明
- **[CONVERSATION_FLOW_EXAMPLE.md](./CONVERSATION_FLOW_EXAMPLE.md)** - 完整对话案例
- **[DESIGN_PATTERN.md](./DESIGN_PATTERN.md)** - 设计模式
- **[USAGE_EXAMPLE.md](./USAGE_EXAMPLE.md)** - 使用示例

---

## 🎯 记住这些要点

1. **scenario.json 只有 Director 能看到**
2. **actor_prompt.md 两方都能看，但 Director 能利用其决策**
3. **Director 通过 user prompt 动态注入指令**
4. **可以灵活组合三个维度**
5. **根据 AI 表现动态调整**

---

**版本**：3.0 - 多维度增强版  
**更新日期**：2025-10-27

