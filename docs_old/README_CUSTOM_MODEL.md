# 使用自定义模型运行EPJ Benchmark

## 📖 概述

`run_benchmark_custom_model.py` 脚本允许你使用自己训练并部署的模型来运行EPJ Benchmark评测，支持SGLang等各种自部署模型API。

## 🔧 配置你的自定义模型API

### 1. 编辑配置

打开 `run_benchmark_custom_model.py`，找到 `CUSTOM_API_CONFIG` 部分：

```python
CUSTOM_API_CONFIG = {
    "api_key": "EMPTY",                                 # API密钥
    "base_url": "http://115.190.74.46:57037/v1",       # API地址
    "model_name": "default",                            # 模型名称
    "max_tokens": 8192,                                 # 最大生成token数
    "temperature": 0.7,                                 # 温度参数
    "top_p": 0.8,                                       # top_p采样
    "presence_penalty": 1.5,                            # 出现惩罚
    "extra_body": {                                     # 额外参数（可选）
        "top_k": 20,
        "chat_template_kwargs": {"enable_thinking": False},
    }
}
```

### 2. 修改为你的API配置

根据你的实际部署情况修改：

```python
CUSTOM_API_CONFIG = {
    "api_key": "YOUR_API_KEY",              # 如果不需要认证，保持"EMPTY"
    "base_url": "http://YOUR_IP:PORT/v1",   # 你的模型API地址
    "model_name": "your_model_name",        # 你的模型名称
    # ... 其他参数根据需要调整
}
```

### 3. 调整评测参数（可选）

```python
MAX_TURNS = 15  # 每个对话最多轮次（建议10-20）
K = 1           # 每K轮评估一次EPJ（1表示每轮都评估）

# 🚀 并发配置 - 加速评测！
MAX_WORKERS = 3  # 并发线程数（建议2-5，太高可能触发API限流）

# 用于角色扮演和评估的模型（使用OpenRouter）
ACTOR_MODEL = "google/gemini-2.5-pro"
DIRECTOR_MODEL = "google/gemini-2.5-pro"
JUDGER_MODEL = "google/gemini-2.5-pro"
```

**⚡ 并发优化说明**:
- `MAX_WORKERS = 1`: 串行执行（最安全，但最慢）
- `MAX_WORKERS = 3`: **推荐配置**，速度提升3倍
- `MAX_WORKERS = 5`: 速度提升5倍，但可能触发API限流
- 建议根据你的API速率限制调整

## 🚀 运行评测

### 前置条件

确保已经生成了30个抽样案例：

```bash
python3 sample_benchmark_cases.py
```

这会生成 `results/sampled_benchmark_30_ids.txt` 文件。

### 开始评测

```bash
python3 run_benchmark_custom_model.py
```

## 📊 评测流程

对于每个测试案例，系统会：

1. **加载剧本配置** - 角色设定、故事背景等
2. **初始化Agents**:
   - Actor: 扮演用户角色（使用Gemini）
   - Director: 控制剧情发展（使用Gemini）
   - Judger: 评估共情表现（使用Gemini）
   - TestModel: **你的自定义模型**（被评测对象）

3. **运行EPJ对话循环**:
   - Actor发起话题
   - **你的模型**生成回复
   - Judger评估共情质量
   - 计算EPJ/EPM指标
   - Director根据评估结果调整剧情
   - 重复直到达到终止条件

4. **生成评测报告**:
   - 初始共情赤字（IEDR）
   - 每轮EPJ评估结果
   - 最终EPM得分
   - 对话历史记录

## 📂 结果文件

评测完成后，结果保存在：

```
results/benchmark_runs/run_YYYYMMDD_HHMMSS/
├── summary.json                    # 汇总报告
├── script_002_result.json          # 各个案例的详细结果
├── script_006_result.json
├── ...
└── script_273_result.json
```

### summary.json 结构

```json
{
  "run_timestamp": "20251104_123456",
  "custom_model_config": {
    "base_url": "http://115.190.74.46:57037/v1",
    "model_name": "default"
  },
  "evaluation_config": {
    "max_turns": 15,
    "K": 1,
    "actor_model": "google/gemini-2.5-pro",
    "director_model": "google/gemini-2.5-pro",
    "judger_model": "google/gemini-2.5-pro"
  },
  "total_cases": 30,
  "success_count": 30,
  "error_count": 0,
  "success_rate": 100.0,
  "results": [...]
}
```

### 单个案例结果结构

```json
{
  "script_id": "script_002",
  "status": "success",
  "timestamp": "2025-11-04T12:34:56",
  "iedr": {
    "C.1": 3, "C.2": 3, "C.3": 1,
    "A.1": 2, "A.2": 2, "A.3": 3,
    "P.1": 1, "P.2": 3, "P.3": 2
  },
  "history": [...],                 # 完整对话历史
  "final_report": {
    "final_epm_score": 85.5,        # 最终EPM得分
    "termination_reason": "...",
    "conversation_quality": "...",
    ...
  }
}
```

## 📈 评估指标说明

### EPJ（共情精度指标）
- **C轴**: 认知共情 - 被理解
- **A轴**: 情感共情 - 被共鸣
- **P轴**: 动机共情 - 被肯定/赋能

### EPM（共情精通度）
综合评估模型在整个对话过程中的共情能力：
- **Distance**: 共情赤字减少量
- **Direction**: 共情方向准确性
- **Energy**: 共情响应的充分性

## 🔍 API兼容性

脚本使用OpenAI兼容的API格式，支持：

✅ **SGLang**
✅ **vLLM**
✅ **Ollama** (需要OpenAI兼容模式)
✅ **LMStudio**
✅ **其他兼容OpenAI API的部署方案**

### 示例：其他API格式

#### vLLM

```python
CUSTOM_API_CONFIG = {
    "api_key": "EMPTY",
    "base_url": "http://localhost:8000/v1",
    "model_name": "your-model-name",
    ...
}
```

#### Ollama (需要启用OpenAI兼容)

```python
CUSTOM_API_CONFIG = {
    "api_key": "EMPTY",
    "base_url": "http://localhost:11434/v1",
    "model_name": "llama2",
    ...
}
```

## ⚠️ 注意事项

1. **API密钥配置**:
   - Actor/Director/Judger使用OpenRouter API，需要配置 `OPENROUTER_API_KEY`
   - 在 `config/api_config.py` 或 `.env` 文件中设置

2. **网络连接**:
   - 确保能访问你的自定义模型API
   - 确保能访问OpenRouter API

3. **耗时估算** ⚡:
   - **串行执行** (MAX_WORKERS = 1): 30个案例预计需要 **2.5-7.5小时**
   - **并发执行** (MAX_WORKERS = 3): 30个案例预计需要 **50分钟-2.5小时** ✨
   - **高并发** (MAX_WORKERS = 5): 30个案例预计需要 **30分钟-1.5小时** 🚀
   - 实际耗时取决于对话轮次、模型响应速度和API限流

4. **资源消耗**:
   - Actor/Director/Judger使用OpenRouter API（有费用）
   - 你的自定义模型运行在你自己的服务器上

5. **并发注意事项** ⚡:
   - 并发数量建议从3开始，逐步增加
   - 如果遇到频繁的API限流错误，降低 `MAX_WORKERS`
   - 自定义模型服务器性能足够才能充分利用并发
   - 每完成5个案例会自动保存进度，中途中断也不会丢失数据

## 🐛 故障排查

### 问题1：找不到案例列表文件

```
❌ 错误：找不到案例列表文件 results/sampled_benchmark_30_ids.txt
```

**解决**: 先运行 `python3 sample_benchmark_cases.py` 生成抽样案例

### 问题2：API连接失败

```
❌ API调用失败: Connection refused
```

**解决**:
- 检查 `base_url` 是否正确
- 确认模型服务是否正在运行
- 检查防火墙设置

### 问题3：OpenRouter API密钥未配置

```
!!! [API层] 配置错误: 未找到 'OPENROUTER_API_KEY' !!!
```

**解决**: 在 `config/api_config.py` 中设置 `OPENROUTER_API_KEY`

### 问题4：API限流错误

```
❌ API调用失败: Rate limit exceeded
```

**解决**:
- 降低 `MAX_WORKERS` 值（例如从5降到3）
- 增加 `timeout` 参数
- 检查OpenRouter或自定义模型的速率限制

### 问题5：并发执行时日志混乱

这是正常的，因为多个线程同时运行。主要关注：
- ✅ 成功/失败的统计信息
- 💾 进度保存提示
- 最终的summary文件

## 📞 获取帮助

如果遇到问题，请检查：
1. API配置是否正确
2. 模型服务是否正常运行
3. 网络连接是否正常
4. 查看详细的错误日志

---

**祝评测顺利！** 🚀

