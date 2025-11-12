# 📚 文档索引

本目录包含 Benchmark 项目的架构设计和技术文档。

---

## 🏗️ 架构设计文档

### 核心机制

| 文档 | 说明 | 重要性 |
|------|------|--------|
| [DIRECTOR_FUNCTION_CALLING.md](./DIRECTOR_FUNCTION_CALLING.md) | Director 函数调用机制详解 | ⭐⭐⭐ |
| [FUNCTION_CALLING_VERIFIED.md](./FUNCTION_CALLING_VERIFIED.md) | 函数调用验证和测试结果 | ⭐⭐⭐ |
| [TERMINATION_SIMPLE.md](./TERMINATION_SIMPLE.md) | 对话终止机制设计 | ⭐⭐⭐ |

### 设计决策

| 文档 | 说明 | 重要性 |
|------|------|--------|
| [DIRECTOR_ANYTIME_DECISION.md](./DIRECTOR_ANYTIME_DECISION.md) | Director 随时决策设计 | ⭐⭐ |
| [ORCHESTRATOR_TRADEOFFS.md](./ORCHESTRATOR_TRADEOFFS.md) | Orchestrator 设计权衡分析 | ⭐⭐ |
| [JUDGER_DIRECTOR_DECOUPLED.md](./JUDGER_DIRECTOR_DECOUPLED.md) | Judger 和 Director 解耦说明 | ⭐⭐ |

### 使用示例

| 文档 | 说明 | 重要性 |
|------|------|--------|
| [DIRECTOR_USAGE_EXAMPLE.md](./DIRECTOR_USAGE_EXAMPLE.md) | Director 使用示例 | ⭐⭐ |
| [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) | 实现总结 | ⭐ |

---

## 📖 推荐阅读顺序

### 🚀 新手入门

1. **[../Benchmark/README.md](../Benchmark/README.md)** - 项目概述
2. **[../Benchmark/QUICK_START.md](../Benchmark/QUICK_START.md)** - 快速开始指南
3. **[../Benchmark/ARCHITECTURE_UPDATE.md](../Benchmark/ARCHITECTURE_UPDATE.md)** - 架构更新说明

### 🔧 深入理解

4. **[DIRECTOR_FUNCTION_CALLING.md](./DIRECTOR_FUNCTION_CALLING.md)** - 理解 Director 如何工作
5. **[TERMINATION_SIMPLE.md](./TERMINATION_SIMPLE.md)** - 理解对话如何终止
6. **[ORCHESTRATOR_TRADEOFFS.md](./ORCHESTRATOR_TRADEOFFS.md)** - 理解设计权衡

### 🎯 高级主题

7. **[JUDGER_DIRECTOR_DECOUPLED.md](./JUDGER_DIRECTOR_DECOUPLED.md)** - 组件解耦
8. **[DIRECTOR_ANYTIME_DECISION.md](./DIRECTOR_ANYTIME_DECISION.md)** - 决策机制

---

## 🔗 相关资源

- **测试文件**：[../tests/](../tests/) - 包含各种功能测试
- **源代码**：[../Benchmark/](../Benchmark/) - 主要代码实现

---

## 📝 文档维护

这些文档记录了项目的设计演进过程。如需了解最新实现，请参考：
- 源代码实现
- 代码注释
- 测试用例

