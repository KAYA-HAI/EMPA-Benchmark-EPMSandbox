# 配置加载器使用示例

## 📚 快速开始

### 1. 加载完整配置（推荐）

```python
from Benchmark.topics.config_loader import load_config

# 加载剧本001的完整配置
config = load_config("001")

# 获取 Actor Prompt
actor_prompt = config['actor_prompt']
print(f"Actor Prompt 长度: {len(actor_prompt)} 字符")

# 获取剧本信息
scenario = config['scenario']
print(f"剧本编号: {scenario['剧本编号']}")
print(f"故事结果: {scenario['故事的结果']}")
```

### 2. 分别加载

```python
from Benchmark.topics.config_loader import load_actor_prompt, load_scenario

# 只加载 Actor Prompt
actor_prompt = load_actor_prompt("001")

# 只加载剧本配置
scenario = load_scenario("001")
```

### 3. 提取故事阶段

```python
from Benchmark.topics.config_loader import load_scenario, extract_stages

# 加载剧本
scenario = load_scenario("001")

# 提取所有故事阶段
stages = extract_stages(scenario)

for stage in stages:
    print(f"{stage['阶段名']}: {stage['标题']}")
    print(f"内容: {stage['内容'][:100]}...")
```

---

## 🎯 完整示例：Director 使用场景

```python
from Benchmark.topics.config_loader import load_config, extract_stages

class Director:
    def __init__(self, script_id: str):
        """初始化 Director 并加载剧本配置"""
        self.config = load_config(script_id)
        self.actor_prompt = self.config['actor_prompt']
        self.scenario = self.config['scenario']
        self.stages = extract_stages(self.scenario)
        self.current_stage = 0
        
        print(f"✅ Director 已加载剧本: {self.scenario['剧本编号']}")
        print(f"   - Actor Prompt: {len(self.actor_prompt)} 字符")
        print(f"   - 故事阶段: {len(self.stages)} 个")
    
    def get_actor_prompt(self) -> str:
        """获取 Actor 的完整系统提示词"""
        return self.actor_prompt
    
    def get_initial_context(self) -> dict:
        """获取初始对话上下文"""
        return {
            "剧本编号": self.scenario['剧本编号'],
            "故事结果": self.scenario['故事的结果'],
            "当前阶段": 0,
            "总阶段数": len(self.stages)
        }
    
    def advance_stage(self) -> dict:
        """推进到下一个故事阶段"""
        if self.current_stage < len(self.stages):
            stage = self.stages[self.current_stage]
            self.current_stage += 1
            
            return {
                "阶段名": stage['阶段名'],
                "标题": stage['标题'],
                "内容": stage['内容'],
                "是否最后阶段": self.current_stage >= len(self.stages)
            }
        else:
            return None
    
    def get_story_epilogue(self) -> str:
        """获取故事的插曲（额外信息）"""
        return self.scenario.get('故事的插曲', '')


# 使用示例
if __name__ == "__main__":
    # 初始化 Director
    director = Director("001")
    
    # 获取 Actor Prompt
    actor_prompt = director.get_actor_prompt()
    print(f"\n📄 Actor Prompt 前200字符:")
    print(actor_prompt[:200])
    
    # 获取初始上下文
    context = director.get_initial_context()
    print(f"\n📊 初始上下文:")
    print(f"   剧本: {context['剧本编号']}")
    print(f"   目标: {context['故事结果']}")
    
    # 推进故事阶段
    print(f"\n🎬 故事推进:")
    while True:
        stage = director.advance_stage()
        if stage is None:
            break
        
        print(f"\n[{stage['阶段名']}] {stage['标题']}")
        print(f"   {stage['内容'][:100]}...")
        print(f"   最后阶段: {'是' if stage['是否最后阶段'] else '否'}")
    
    # 获取插曲
    epilogue = director.get_story_epilogue()
    print(f"\n💭 故事插曲:")
    print(f"   {epilogue[:150]}...")
```

---

## 📝 Actor Prompt 结构说明

您的 Actor Prompt 包含以下部分：

### 1. `<character_info>` - 角色信息
```markdown
- 姓名：刘静
- 性别：女
- 年龄：26
- 社交性格：外向活泼
- 内核性格：需要独处
- 输出格式：不超过30个字
- 当前行为：和网友聊天
- 聊天原则：真实用户思维
- 聊天策略：多样化话术
```

### 2. `<empathy_threshold>` - 共情阈值
```markdown
共情阈值【低】
- 渴望任何形式的共情
- 几乎不挑剔
- 重视陪伴姿态
```

### 3. `<psychological_profile>` - 心理画像
```markdown
- 聊天话题：甲方表扬我了！
- 共情需求：分享喜悦和释放感
- 人物共情阈值：较高
- 当下共情需求优先级：
  1. 动机共情
  2. 情感共情
  3. 认知共情
```

### 4. `<experience>` - 角色经历
```markdown
- 过往经历：童年、少年、青年
- 隐形成长主线：建立自我评价体系
- 角色现状：广告公司设计师
- 人生目标：成为成熟设计师
- 人生愿景：作品被认可
```

### 5. `<scenario>` - 角色故事
```markdown
- 故事起因：团队接了难搞的客户
- 背景设定：方案被反复修改十几稿
```

---

## 🔄 剧本 JSON 结构说明

### 基本信息
```json
{
  "剧本编号": "script_001"
}
```

### 故事阶段
```json
{
  "故事的经过": {
    "阶段1": {
      "标题": "引发回忆",
      "内容": "..."
    },
    "阶段2": {
      "标题": "引发思考",
      "内容": "..."
    },
    "阶段3": {
      "标题": "引发自审",
      "内容": "..."
    },
    "阶段4": {
      "标题": "情绪崩发",
      "内容": "..."
    }
  }
}
```

### 结果和插曲
```json
{
  "故事的结果": "刘静现在想找人聊天分享自己的想法，寻找共鸣与情绪价值。",
  "故事的插曲": "她想起了大学毕业设计答辩时..."
}
```

---

## 🧪 测试配置

```bash
# 运行内置测试
cd /Users/shiya/Downloads/Benchmark-test
python3 -m Benchmark.topics.config_loader

# 输出示例：
# === 配置加载器测试 ===
# 
# 1. 可用的剧本:
#    找到 1 个剧本: ['001']
# 
# 2. 加载 Actor Prompt (001):
# ✅ [ConfigLoader] 已加载 Actor Prompt 001 (1657 字符)
#    Prompt 长度: 1657 字符
#    ...
```

---

## 💡 最佳实践

1. **使用 `load_config()` 一次性加载**
   - 避免重复I/O操作
   - 确保 Actor Prompt 和剧本配置匹配

2. **使用 `extract_stages()` 提取阶段**
   - 自动按阶段编号排序
   - 返回结构化数据

3. **错误处理**
   ```python
   try:
       config = load_config("001")
   except FileNotFoundError as e:
       print(f"配置文件不存在: {e}")
   ```

4. **列出所有可用剧本**
   ```python
   from Benchmark.topics.config_loader import list_scenarios
   
   available = list_scenarios()
   print(f"可用剧本: {available}")
   ```

---

## 📦 供其他模块使用

### Actor 模块
```python
from Benchmark.topics.config_loader import load_actor_prompt

class Actor:
    def __init__(self, script_id: str):
        self.system_prompt = load_actor_prompt(script_id)
```

### Director 模块
```python
from Benchmark.topics.config_loader import load_config, extract_stages

class Director:
    def __init__(self, script_id: str):
        config = load_config(script_id)
        self.stages = extract_stages(config['scenario'])
```

### Orchestrator 模块
```python
from Benchmark.topics.config_loader import load_config

def initialize_conversation(script_id: str):
    config = load_config(script_id)
    return {
        "actor_prompt": config['actor_prompt'],
        "scenario": config['scenario']
    }
```

