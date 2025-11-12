# 🧪 测试文件

本目录包含 Benchmark 项目的测试脚本。

---

## 📋 测试文件列表

| 测试文件 | 用途 | 运行方法 |
|---------|------|---------|
| [test_prompt.py](./test_prompt.py) | 查看 Actor 的 System Prompt | `python test_prompt.py` |
| [test_history_flow.py](./test_history_flow.py) | 测试对话历史传递流程 | `python test_history_flow.py` |
| [test_director_function_calling.py](./test_director_function_calling.py) | 测试 Director 函数调用机制 | `python test_director_function_calling.py` |

---

## 🚀 如何运行测试

### 1. 查看 Actor Prompt
```bash
cd /Users/shiya/Downloads/Benchmark-test
python tests/test_prompt.py
```

### 2. 测试对话历史
```bash
python tests/test_history_flow.py
```

### 3. 测试 Director 函数调用
```bash
python tests/test_director_function_calling.py
```

---

## 📝 注意事项

- 运行测试前，请确保已安装所需依赖
- 测试可能需要配置 API 密钥
- 某些测试会调用实际的 LLM API，可能产生费用

---

## 🔗 相关文档

- [函数调用验证文档](../docs/FUNCTION_CALLING_VERIFIED.md)
- [Director 使用示例](../docs/DIRECTOR_USAGE_EXAMPLE.md)

