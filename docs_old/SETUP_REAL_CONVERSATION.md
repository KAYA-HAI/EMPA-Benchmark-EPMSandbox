# 运行真实EPJ对话 - 快速开始

## ✅ 系统已准备就绪

所有测试已通过，系统可以运行！

### 已验证的组件

- ✅ 配置加载: actor_prompt_001.md + scenario_001.json
- ✅ Director: 剧情控制 + EPJ决策
- ✅ Judger: 量表填写（读取剧本）
- ✅ EPJ Orchestrator: 向量计算
- ✅ EPJ Chat Loop: 对话循环

### 案例剧本

- 角色: 刘静，26岁设计师
- 话题: 被挑剔甲方点名表扬
- 共情需求: 动机>情感>认知
- 初始赤字: P_0 = (-7, -14, -27)

---

## 🚀 运行步骤

### 步骤1: 配置API Key

创建配置文件：
```bash
cd /Users/shiya/Downloads/Benchmark-test/Benchmark/topics/
touch .env
```

编辑 `.env` 文件，添加：
```
OPENROUTER_API_KEY=your_api_key_here
```

获取API Key:
- 访问: https://openrouter.ai/keys
- 注册并获取免费API key

---

### 步骤2: 运行对话

```bash
cd /Users/shiya/Downloads/Benchmark-test
python3 run_real_conversation.py
```

---

## 📊 预期输出

### 1. EPJ初始化（T=0）
```
EPJ 初始化 (T=0)
═══ Judger填写IEDR量表 ═══
✅ P_0 = (-7, -14, -27)
   动机需求(-27) > 情感需求(-14) > 认知需求(-7)
```

### 2. 对话过程
```
第1轮:
  刘静: 我们那个最挑剔的甲方，今天居然点名表扬我了
  AI助手: [LLM生成的回复]
  
第2轮:
  ...
  
第3轮:
  ...
  ═══ EPJ评估 ═══
  v_t = (+1, +3, +1)
  P_t = (-6, -11, -26)
  Director决策: CONTINUE
```

### 3. 对话结束
```
终止原因: 达到Epsilon区域 / 超时
最终位置: P_final
完整轨迹: [...]
结果保存: epj_conversation_result.json
```

---

## 🎯 观察要点

运行时请观察：

1. **Judger的量表填写**
   - 是否真正读取了actor_prompt和scenario
   - IEDR的值是否符合剧本特点
   - P_0是否反映共情需求优先级

2. **EPJ向量计算**
   - P_0初始赤字是否合理
   - v_t增量是否反映AI的共情质量
   - P_t是否正确更新

3. **Director的决策**
   - 剧情控制是否基于完整的epj_state
   - 终止决策是否基于is_in_zone
   - 是否有"有损压缩"的progress判断

4. **对话质量**
   - Actor的表现是否符合刘静的性格
   - AI助手的共情是否合适
   - Director的剧情释放是否恰当

---

## ⚠️ 可能的问题

### 问题1: API Key错误
```
❌ API调用失败: Invalid API key
```

解决: 检查 .env 文件中的API key是否正确

---

### 问题2: 网络问题
```
❌ Connection timeout
```

解决: 检查网络连接，可能需要代理

---

### 问题3: LLM返回格式错误
```
❌ JSON解析失败
```

解决: 正常现象，代码有容错处理

---

## 📚 相关文档

- `test_epj_with_real_script.py` - Mock测试（已成功）
- `run_real_conversation.py` - 真实对话脚本
- `Benchmark/orchestrator/chat_loop_epj.py` - EPJ对话循环
- `EPJ.md` - EPJ系统完整文档

---

**创建日期**: 2025-10-27  
**状态**: ✅ 准备就绪，等待API key
