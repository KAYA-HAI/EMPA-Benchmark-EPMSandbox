# Director 代码清理计划

## 📋 清理目标

移除旧系统遗留代码，简化EPJ系统的调用流程

---

## 🎯 方案：简化Director调用

### 核心思想

**移除前**: 双重判断
```
should_intervene() → 简单规则判断（基于progress）
    ↓
evaluate_continuation() → 复杂智能分析（基于epj_state）
```

**移除后**: 单一智能判断
```
evaluate_continuation() → 唯一的智能分析（基于epj_state）
    ↓
返回: {should_continue, guidance, no_intervention}
```

---

## 📝 修改清单

### 1. 删除未使用的代码 ✅

**文件**: `Benchmark/agents/director.py`

**删除**:
- `_llm_quick_check()` 方法（第168-217行）- 从未使用

---

### 2. 标记旧系统方法为废弃 ✅

**文件**: `Benchmark/agents/director.py`

**标记为废弃**:
- `should_intervene()` 方法
- `_quick_intervention_check()` 方法

**添加装饰器和警告**:
```python
def should_intervene(self, history: list, current_turn: int, current_progress: int) -> bool:
    """
    【仅用于旧系统】Director判断是否需要介入
    
    ⚠️ 警告：此方法使用单一progress分数，不适合EPJ系统
    ⚠️ EPJ系统应直接调用 evaluate_continuation() 并传入完整的 epj_state
    ⚠️ 此方法仅为向后兼容性保留
    """
    print("⚠️ [Director] 警告：should_intervene() 是旧系统方法，EPJ系统不推荐使用")
    # ... 原有代码
```

---

### 3. 修改 EPJ Chat Loop ✅

**文件**: `Benchmark/orchestrator/chat_loop_epj.py`

**修改前** (第213-229行):
```python
# Director判断是否需要介入剧情控制
# 注意：should_intervene使用ref_progress仅作为触发参考
if director.should_intervene(history, turn_count, ref_progress):
    print(f"\n🎬 Director 介入剧情控制")
    
    # Director评估并决定剧情发展
    # 关键：传递完整的epj_state，而不是单一的progress数字
    director_result = director.evaluate_continuation(
        history=history,
        progress=None,  # 不使用单一分数
        epj_state=current_epj_state  # 传递完整的向量状态
    )
    
    if director_result.get('guidance'):
        # 将Director的剧情指导传递给Actor
        history[-1]['director_guidance'] = director_result['guidance']
        print(f"💡 Director剧情指导: {director_result['guidance'][:100]}...")
```

**修改后**:
```python
# Director基于EPJ状态评估并决策
# 完全依赖Director的智能分析，而不是预先的简单判断
director_result = director.evaluate_continuation(
    history=history,
    progress=None,  # 不使用单一分数
    epj_state=current_epj_state  # 传递完整的向量状态
)

# Director自己决定是否需要介入
# 通过返回no_intervention标志或guidance内容来控制
if director_result.get('guidance') and not director_result.get('no_intervention'):
    print(f"\n🎬 Director 介入剧情控制")
    # 将Director的剧情指导传递给Actor
    history[-1]['director_guidance'] = director_result['guidance']
    print(f"💡 Director剧情指导: {director_result['guidance'][:100]}...")
else:
    print(f"👁️  Director 观察中（未介入）")
```

---

### 4. 更新 Director 返回格式 ✅

确保 `evaluate_continuation()` 的返回值清晰表达是否介入。

**在 director.py 中**:

**`_handle_observe_and_wait()` 方法已经正确**:
```python
return {
    "should_continue": True,
    "guidance": None,  # 不给任何指导
    "no_intervention": True  # ✅ 标记为不介入
}
```

**确保其他handler也返回正确的标志**。

---

## 🧪 测试验证

### 测试1: EPJ系统是否正常工作

```bash
python3 -m Benchmark.scripts.run_demo_epj
```

**预期**:
- ✅ Director不再调用 should_intervene()
- ✅ Director直接分析EPJ状态并决策
- ✅ 观察时正确返回 no_intervention=True

---

### 测试2: 确认旧方法有警告

```python
# 测试旧方法调用
director = Director(scenario, actor_prompt)
result = director.should_intervene(history, turn=5, current_progress=30)
```

**预期**:
- ⚠️ 打印警告信息
- ✅ 仍然可以工作（向后兼容）

---

## 📊 清理效果

### 代码行数变化

| 文件 | 修改前 | 修改后 | 变化 |
|------|--------|--------|------|
| director.py | 1007行 | ~950行 | -57行（删除_llm_quick_check） |
| chat_loop_epj.py | 280行 | ~280行 | 逻辑简化，行数相近 |

### 代码质量提升

**优点**:
1. ✅ **消除矛盾**: 不再有"压缩判断"vs"完整分析"
2. ✅ **简化流程**: Director只需调用一次
3. ✅ **提高一致性**: 完全基于EPJ向量
4. ✅ **易于维护**: 减少了复杂的条件逻辑

**向后兼容**:
- ✅ 旧系统方法保留（标记废弃）
- ✅ 有明确的警告信息
- ✅ 不影响现有的旧系统代码

---

## ✅ 实施步骤

1. [  ] 删除 `_llm_quick_check()` 方法
2. [  ] 标记 `should_intervene()` 和 `_quick_intervention_check()` 为废弃
3. [  ] 添加废弃警告
4. [  ] 修改 `chat_loop_epj.py` 移除对 `should_intervene()` 的调用
5. [  ] 测试EPJ系统是否正常工作
6. [  ] 更新文档

---

## 🎉 预期结果

清理后的EPJ系统：

```
对话循环
  ↓
每轮调用: director.evaluate_continuation(epj_state=完整向量)
  ↓
Director基于EPJ向量智能分析
  ↓
返回: {guidance, no_intervention}
  ↓
Chat Loop根据返回决定是否应用guidance
```

**特点**:
- ✅ 简单清晰
- ✅ 完全基于EPJ向量
- ✅ Director拥有完全的控制权
- ✅ 符合三层架构设计

---

**创建日期**: 2025-10-27  
**状态**: 📝 计划制定完成，等待执行

