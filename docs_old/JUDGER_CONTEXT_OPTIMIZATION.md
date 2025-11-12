# Judger Context 性能优化

## 问题背景

在之前的实现中，每轮对话Judger都会接收完整的`actor_prompt`（约2730字符），并且**每轮都重复执行正则提取**来获取所需信息。

### 原有流程（低效）

```
第1轮: actor_prompt (2730字符) → 正则提取 → judger_context (1092字符)
第2轮: actor_prompt (2730字符) → 正则提取 → judger_context (1092字符)
第3轮: actor_prompt (2730字符) → 正则提取 → judger_context (1092字符)
...
第N轮: actor_prompt (2730字符) → 正则提取 → judger_context (1092字符)
```

**问题**：
1. ❌ 每轮重复执行正则提取（计算浪费）
2. ❌ 传递大量无用信息（tokens浪费）
3. ❌ Judger prompt过长（影响LLM性能）

## 优化方案

### 1. 提前提取一次（chat_loop_epj.py）

```python
# 🔧 优化：对话开始时提取一次
judger_context = _extract_judger_context(actor_prompt)

script_content = {
    "actor_prompt": actor_prompt,        # 完整版（仅给IEDR用）
    "judger_context": judger_context,    # 精简版（给MDEP-PR用）
    "scenario": scenario
}
```

### 2. 优先使用缓存（judger_prompts.py）

```python
# 🔧 优化：优先使用预提取的judger_context
if 'judger_context' in script_context:
    extracted_context = script_context['judger_context']  # 直接使用
elif 'actor_prompt' in script_context:
    extracted_context = _extract_judger_context(...)      # 向后兼容
```

### 新流程（高效）

```
初始化: actor_prompt (2730字符) → 正则提取 → judger_context (1092字符) ✓

第1轮: judger_context (1092字符) → 直接使用 ✓
第2轮: judger_context (1092字符) → 直接使用 ✓
第3轮: judger_context (1092字符) → 直接使用 ✓
...
第N轮: judger_context (1092字符) → 直接使用 ✓
```

## 优化效果

### 📊 内容精简

| 项目 | 优化前 | 优化后 | 改进 |
|------|--------|--------|------|
| **传入字符数** | 2730 | 1092 | **-60%** |
| **正则提取次数** | N次 | 1次 | **节省N-1次** |

### ✅ 保留的关键信息（1092字符）

1. **角色基本信息**（280字符）
   - 姓名、年龄、性别
   - 社交性格 vs. 内核性格
   - 输出格式、当前行为

2. **共情阈值**（150字符）
   - 共情阈值等级
   - 对共情质量的要求

3. **共情需求画像**（550字符）⭐ 最关键
   - 聊天话题
   - 想要倾诉的内容
   - **C/A/P优先级**（Judger打分的核心依据）

4. **成长脉络**（110字符）
   - 理解角色深层动机

### ❌ 去除的无用信息（1638字符）

- 🚨 禁止重复约束（给Actor的指令）
- 🚨 角色聊天策略（Judger不需要）
- 📖 详细的过往经历（用"成长脉络"概括）
- 🎬 scenario故事起因（对打分无影响）

## 性能收益

假设一次对话30轮：

| 指标 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| **正则提取次数** | 30次 | 1次 | **29次** |
| **传入Judger的总字符** | 81,900 | 32,760 | **-60%** |
| **传入LLM的tokens** | ~41,000 | ~16,400 | **-60%** |

**关键收益**：
- ✅ 更快的提取速度（29次正则计算被跳过）
- ✅ 更低的API成本（每次调用节省~1600 tokens）
- ✅ 更简洁的Judger prompt（LLM处理更快）
- ✅ 完全保留评估所需的所有信息

## 向后兼容

如果某些地方仍然传入完整的`actor_prompt`而不是`judger_context`，代码会自动回退到提取模式：

```python
elif 'actor_prompt' in script_context:
    # 向后兼容：临时提取一次
    extracted_context = _extract_judger_context(script_context['actor_prompt'])
```

## 实现文件

- `Benchmark/epj/judger_prompts.py`：
  - 新增 `_extract_judger_context()` 函数
  - 修改 `generate_mdep_pr_prompt()` 优先使用缓存

- `Benchmark/orchestrator/chat_loop_epj.py`：
  - 初始化阶段提前提取一次
  - `script_content` 中传递 `judger_context`

## 测试建议

运行单案例测试，观察输出：
```bash
python3 run_real_conversation.py
```

在初始化阶段会看到：
```
✅ 剧本配置加载完成
   剧本编号: ...
   Actor Prompt: 2730 字符
   Judger Context: 1092 字符 (压缩率: 40.0%)
```

每轮Judger评估时，不会再看到重复提取的日志。

