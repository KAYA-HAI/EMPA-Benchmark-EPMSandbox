# Benchmark项目结构说明

## 📁 项目目录结构

```
Benchmark-test/
├── Benchmark/                      # 核心代码
│   ├── agents/                     # Agent实现
│   │   ├── actor.py                # Actor（倾诉者）
│   │   ├── director.py             # Director（导演）
│   │   ├── judger.py               # Judger（评估员）
│   │   └── test_model.py           # TestModel（被测AI）
│   │
│   ├── epj/                        # EPJ系统
│   │   ├── rubrics.py              # 量表定义（IEDR, MDEP-PR）
│   │   ├── scoring.py              # 计分规则（IED-SK, MDEP-SK）
│   │   ├── vector_calculator.py    # 向量计算器
│   │   ├── vector_utils.py         # 向量工具函数
│   │   ├── display_metrics.py      # 显示指标（曼哈顿距离）
│   │   ├── judger_prompts.py       # Judger的量表填写prompts
│   │   └── README.md               # EPJ系统说明
│   │
│   ├── orchestrator/               # 编排器
│   │   ├── chat_loop_epj.py        # EPJ对话循环（推荐）
│   │   ├── epj_orchestrator.py     # EPJ编排器
│   │   ├── chat_loop.py            # 旧系统对话循环
│   │   └── ...                     # 其他编排器
│   │
│   ├── prompts/                    # Prompt模板
│   │   ├── actor_prompts.py        # Actor的prompts
│   │   ├── director_prompts.py     # Director的prompts
│   │   ├── director_function_schemas_selector.py  # Director的函数定义
│   │   ├── judger_prompts.py       # Judger的prompts（旧系统）
│   │   └── test_model_prompts.py   # TestModel的prompts
│   │
│   ├── topics/                     # 剧本配置
│   │   ├── config_loader.py        # 配置加载器
│   │   └── data/                   # 剧本数据
│   │       ├── actor_prompt_001.md          # Actor提示词
│   │       └── scenarios/
│   │           └── scenario_001.json        # 剧本场景
│   │
│   ├── llms/                       # LLM API
│   │   └── api.py                  # OpenRouter API封装
│   │
│
├── config/                         # 配置文件（新增）
│   ├── api_config.py               # API密钥配置
│   └── README.md                   # 配置说明
│
├── docs/                           # 文档
│   ├── epj/                        # EPJ相关文档
│   │   ├── EPJ.md                  # EPJ完整设计文档
│   │   ├── EPJ_IMPLEMENTATION_COMPLETE.md
│   │   └── EPJ_PROGRESS_FINAL.md
│   │
│   ├── director/                   # Director相关文档
│   │   ├── DIRECTOR_CLEANUP_COMPLETE.md
│   │   ├── DIRECTOR_FILES_RELATIONSHIP.md
│   │   └── ...
│   │
│   ├── SETUP_REAL_CONVERSATION.md  # 运行设置指南
│   └── README.md                   # 文档索引
│
├── tests/                          # 测试文件
│   ├── integration/                # 集成测试（新增）
│   │   ├── test_epj_system.py
│   │   ├── test_epj_with_real_script.py
│   │   └── ...
│   │
│   └── test_*.py                   # 单元测试
│
├── results/                        # 运行结果（新增）
│   ├── epj_conversation_result.json
│   └── epj_run_log.txt
│
├── run_real_conversation.py        # 主运行脚本
└── README.md                       # 项目总说明
```

---

## ⚙️ 配置位置

### 1. API密钥

**位置**: `config/api_config.py`

```python
OPENROUTER_API_KEY = "sk-or-v1-你的key"
```

### 2. 使用的模型

**位置**: `run_real_conversation.py` (第46-50行)

```python
ACTOR_MODEL = "openai/gpt-4o-mini"
DIRECTOR_MODEL = "openai/gpt-4o-mini"  
JUDGER_MODEL = "openai/gpt-4o-mini"
TEST_MODEL_NAME = "openai/gpt-4o-mini"
```

### 3. 运行参数

**位置**: `run_real_conversation.py` (第41-43行)

```python
SCRIPT_ID = "001"      # 使用哪个剧本
MAX_TURNS = 15         # 最大对话轮数
K = 3                  # 每K轮评估一次EPJ
```

### 4. 剧本数据

**位置**: `Benchmark/topics/data/`

- `actor_prompt_001.md` - Actor的角色设定
- `scenarios/scenario_001.json` - 故事阶段

---

## 🚀 快速开始

### 1. 配置API key

编辑 `config/api_config.py`，填入你的key

### 2. 选择模型（可选）

编辑 `run_real_conversation.py`，修改模型名称

### 3. 运行对话

```bash
python3 run_real_conversation.py
```

---

## 📚 文档位置

- **EPJ系统**: `docs/epj/EPJ.md`
- **Director说明**: `docs/director/`
- **配置指南**: `config/README.md`
- **运行设置**: `docs/SETUP_REAL_CONVERSATION.md`

---

## 🧪 测试

**位置**: `tests/integration/`

```bash
# 测试EPJ系统
python3 tests/integration/test_epj_system.py

# 测试真实剧本
python3 tests/integration/test_epj_with_real_script.py
```

---

**更新日期**: 2025-10-27  
**版本**: 整理后v1.0

