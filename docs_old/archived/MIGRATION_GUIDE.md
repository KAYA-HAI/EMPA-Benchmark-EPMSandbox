# Topics 系统迁移指南

## 📋 变更概述

从**随机抽卡系统**迁移到**基于文件的配置系统**。

---

## 🔄 主要变更

### 1. 数据存储方式

| 旧系统 | 新系统 |
|--------|--------|
| Python 字典硬编码 | JSON 文件 |
| 代码中定义数据 | 文件系统存储 |
| 难以扩展 | 易于扩展 |

### 2. 加载方式

| 旧系统 | 新系统 |
|--------|--------|
| 随机抽取 | 指定 ID 加载 |
| `sample_persona()` | `load_scenario("001")` |
| 角色和场景分离 | 整合在一个配置中 |

### 3. 文件结构

**旧结构：**
```
topics/
├── persona_db.py           # 角色数据库
├── scenario_db_layered.py  # 场景数据库
└── topic_db.py             # 主题数据库
```

**新结构：**
```
topics/
├── data/
│   ├── actor_prompt.md      # Actor 系统提示词
│   └── scenarios/
│       ├── scenario_001.json
│       └── scenario_002.json
├── config_loader.py         # 新的加载器
└── README.md                # 使用说明
```

---

## 🔧 代码迁移示例

### 旧代码（废弃）

```python
from Benchmark.topics.persona_db import sample_persona
from Benchmark.topics.scenario_db_layered import sample_scenario_layered

# 随机抽取角色
persona = sample_persona()
print(persona['name'])
print(persona['description'])

# 随机抽取场景
scenario = sample_scenario_layered()
print(scenario['title'])
print(scenario['basic_info']['opening_line'])

# 获取剧情片段
fragments = scenario['plot_fragments']['background']
```

### 新代码（推荐）

```python
from Benchmark.topics.config_loader import load_actor_prompt, load_scenario

# 加载 Actor 基础 Prompt
actor_prompt = load_actor_prompt()

# 加载指定场景（包含角色信息）
scenario = load_scenario("001")

# 访问角色信息
persona = scenario['persona']
print(persona['name'])
print(persona['description'])

# 访问场景信息
print(scenario['title'])
print(scenario['basic_info']['opening_line'])

# 获取剧情片段（结构相同）
fragments = scenario['plot_fragments']['background']
```

---

## 📝 Director 集成

### 旧的初始化方式

```python
def initialize_conversation_config(self, persona_id=None, scenario_id=None):
    """旧方式：从 Python 模块导入"""
    from Benchmark.topics.persona_db import sample_persona, get_persona_by_id
    from Benchmark.topics.scenario_db_layered import sample_scenario_layered, get_scenario_layered_by_id
    
    if persona_id:
        persona = get_persona_by_id(persona_id)
    else:
        persona = sample_persona()
    
    if scenario_id:
        scenario = get_scenario_layered_by_id(scenario_id)
    else:
        scenario = sample_scenario_layered()
    
    # 角色和场景是分离的
    return {
        "persona": persona,
        "scenario": scenario
    }
```

### 新的初始化方式

```python
def initialize_conversation_config(self, scenario_id=None):
    """新方式：从文件加载（角色和场景已整合）"""
    from Benchmark.topics.config_loader import load_scenario, list_scenarios
    
    if scenario_id is None:
        # 如果需要，可以列出所有场景并选择
        available = list_scenarios()
        scenario_id = available[0]  # 或实现其他选择逻辑
    
    # 加载场景（包含角色信息）
    scenario = load_scenario(scenario_id)
    
    # 角色信息已整合在场景中
    return {
        "scenario": scenario,
        "persona": scenario['persona']  # 从场景中提取角色
    }
```

---

## ➕ 添加新场景

### 旧方式（需要修改代码）

1. 编辑 `persona_db.py`，添加新角色到 `PERSONA_DATABASE`
2. 编辑 `scenario_db_layered.py`，添加新场景到 `SCENARIO_LAYERED_DATABASE`
3. 需要重启程序才能生效

### 新方式（只需添加文件）

1. 在 `data/scenarios/` 创建新文件：`scenario_003.json`
2. 填写配置（参考现有文件）
3. 立即可用，无需重启

**示例：**

```bash
# 复制模板
cd Benchmark/topics/data/scenarios/
cp scenario_001.json scenario_003.json

# 编辑内容
# 修改 scenario_id, title, category, persona, plot_fragments 等字段

# 测试
python3 -m Benchmark.topics.config_loader
```

---

## 🧪 测试迁移

### 1. 测试新的加载器

```bash
cd /Users/shiya/Downloads/Benchmark-test
python3 -m Benchmark.topics.config_loader
```

**期望输出：**
```
=== 配置加载器测试 ===

1. 可用的场景:
   找到 2 个场景: ['001', '002']

2. 加载 Actor Prompt:
✅ [ConfigLoader] 已加载 Actor Prompt (507 字符)

3. 加载场景配置 (001):
✅ [ConfigLoader] 已加载场景: 与同事发生项目冲突 (ID: 001)
```

### 2. 测试旧代码（会有警告）

```python
from Benchmark.topics.persona_db import sample_persona

# 会输出警告：
# DeprecationWarning: persona_db.py 已废弃，请使用 config_loader.py
```

---

## 📊 迁移检查清单

- [ ] 阅读新的 [README.md](./README.md)
- [ ] 测试 `config_loader.py` 是否正常工作
- [ ] 更新 Director 的 `initialize_conversation_config()` 方法
- [ ] 更新 Actor 的配置加载逻辑
- [ ] 更新 Orchestrator 的初始化流程
- [ ] 测试完整的对话流程
- [ ] 检查是否有其他地方使用了旧的导入
- [ ] 添加新场景（可选）
- [ ] 更新相关文档

---

## 🎯 迁移优势

1. **数据与代码分离** - 配置存储在 JSON 文件中，易于维护
2. **可版本控制** - JSON 文件更易于 Git 管理
3. **易于扩展** - 添加场景无需修改代码
4. **明确指定** - 不再依赖随机，可明确选择场景
5. **整合配置** - 角色和场景在同一个文件中
6. **结构清晰** - 文件夹结构更加直观

---

## ⚠️ 注意事项

1. **向后兼容**：旧的 `persona_db.py` 等文件暂时保留，但会输出警告
2. **逐步迁移**：可以逐步更新代码，不必一次性全部修改
3. **测试充分**：在迁移后测试所有功能是否正常
4. **文档更新**：相关文档也需要同步更新

---

## 📞 需要帮助？

- 查看 [README.md](./README.md) 了解详细用法
- 运行 `python3 -m Benchmark.topics.config_loader` 查看示例
- 参考 `data/scenarios/scenario_001.json` 了解配置格式

---

**迁移日期：** 2025-10-27  
**版本：** 2.0

