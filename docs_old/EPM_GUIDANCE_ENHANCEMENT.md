# EPM综合指导增强

## 修复概览

本次修复解决了两个关键问题：

### 问题1：Director的EPJ指导缺乏EPM参数分析

**问题描述**：
- Director传给Actor的指导只使用了基础EPJ向量（P_t, v_t），没有利用EPM v2.0的能量动力学数据
- 指导内容过于简单，无法准确诊断问题和提供针对性建议
- 用户需要更综合的分析，包括：
  - 哪根轴偏离
  - 共情方向不对的原因
  - 进度很小的原因

**修复方案**：
完全重写了`Director._generate_guidance_from_vector()`方法，现在它：

1. **接收EPM数据**：增加`epm_summary`参数
2. **三层诊断分析**：
   - **方向性分析**（基于EPM）：
     - `alignment < -0.3`：方向严重偏离
     - `alignment < 0.3`：方向轻微偏离
     - `delta_E < 0`：负向能量（情况恶化）
   
   - **各轴赤字分析**（基于P_t）：
     - C/A/P轴 < -10：该维度需求未被满足
     - 自动识别最深赤字轴
   
   - **增量分析**（基于v_t）：
     - 识别哪些轴出现倒退（< -1）
     - 提供具体问题描述

3. **策略建议**：
   - 基于最深赤字轴提供聚焦建议
   - 基于负向增量提供纠正建议
   - 基于EPM能量状态提供警告或鼓励

4. **输出格式**：
```
【EPM综合分析与指导】

📍 **当前位置**：P_t=(-21, -24, -14)，距离目标=33.14
📈 **本轮增量**：v_t=(-1, 1, 1)
⚡ **能量状态**：累计E=2.25/31.97，本轮ΔE=+0.56

🔍 **问题诊断**：
  • ⚠️ **方向轻微偏离**：AI的回应方向不够准确（对齐度=0.32）
  • 📊 **当前核心缺失**：A轴（情感）赤字深（-24）；C轴（认知）赤字深（-21）
  • ❌ **本轮问题**：C轴倒退（-1）：AI曲解了Actor的意思

💡 **策略建议**：
  • 🎯 **聚焦情感共情**：直接表达你的情绪，寻求情感验证
  • 💡 纠正AI的理解偏差，明确指出'你理解错了...'
```

### 问题2：Director API错误处理不当

**问题描述**：
- API返回空字符串或错误时，Director只打印`⚠️ [Director] API返回了错误字符串:`，没有显示具体错误
- 导致调试困难，无法定位问题根源

**修复方案**：

1. **API层增强错误检查**（`Benchmark/llms/api.py`）：
```python
# 🔧 检查content是否为空
if not reply_content or reply_content.strip() == "":
    print(f"⚠️ [API层] 警告：API返回了空内容")
    print(f"   Finish reason: {finish_reason}")
    print(f"   Message对象: {message}")
    return "（错误：API返回空响应，请重试）"
```

2. **Director层增强错误处理**（`Benchmark/agents/director.py`）：
```python
if isinstance(response, str):
    # 如果是字符串，说明API调用出错
    if not response or response.strip() == "":
        print(f"⚠️ [Director] API返回了空字符串")
    else:
        print(f"⚠️ [Director] API返回了错误信息: {response[:200]}")
    
    return {
        "should_continue": True,
        "guidance": f"API调用失败（{response[:50] if response else '空响应'}），继续对话",
        "error": True,
        "error_message": response
    }
```

## 数据流确认

### EPM参数传递链路

1. **EPJOrchestrator** → `state_packet`（包含`epm_summary`）
2. **chat_loop_epj** → `current_epj_state`（包含`trajectory`和`epm_summary`）
3. **Director.evaluate_continuation** → `generate_director_prompt(epj_state=...)`（传递到LLM）
4. **Director.make_epj_decision** → `_generate_guidance_from_vector(..., epm_summary=...)`（生成指导）

### 确认清单

- [x] EPM参数从`VectorCalculator`计算并存储
- [x] EPM参数通过`state_packet`传递到`chat_loop`
- [x] EPM参数包含在`current_epj_state`中
- [x] EPM参数传递给`Director.evaluate_continuation`（via `generate_director_prompt`）
- [x] EPM参数传递给`Director.make_epj_decision`（via `state_packet`）
- [x] EPM参数用于生成综合指导（`_generate_guidance_from_vector`）

## 测试验证

预期结果：
1. **EPM指导增强**：每轮Director指导应显示完整的问题诊断和策略建议
2. **错误处理改进**：API错误时应显示详细的错误信息，而不是空字符串

## 后续优化建议

1. **Director Prompt优化**：确保LLM在决策时也能看到并利用EPM参数
2. **可视化增强**：考虑在控制台输出中用更醒目的方式展示EPM关键指标
3. **自适应阈值**：根据不同场景动态调整`alignment`和`delta_E`的判断阈值

