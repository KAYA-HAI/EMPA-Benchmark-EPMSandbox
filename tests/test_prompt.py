#!/usr/bin/env python3
"""
测试脚本：查看Actor的System Prompt
用于验证persona和scenario是否正确注入到prompt中
"""

from Benchmark.agents.actor import Actor
from Benchmark.agents.director import Director
from Benchmark.orchestrator.director_orchestrator import ConversationContext

def test_actor_prompt():
    """测试Actor的System Prompt生成"""
    
    print("=" * 70)
    print("🧪 测试：查看Actor的System Prompt")
    print("=" * 70)
    
    # 1. 创建Director和Actor
    director = Director()
    actor = Actor()
    
    print("\n📋 步骤1：Director生成配置")
    print("-" * 70)
    
    # 2. Director生成配置
    config = director.initialize_conversation_config()
    
    print("\n📋 步骤2：创建Orchestrator上下文")
    print("-" * 70)
    
    # 3. 创建上下文并传递配置
    context = ConversationContext()
    context.set_variables(
        persona=config['persona'],
        scenario=config['scenario']
    )
    
    print("✅ 配置已存入Orchestrator")
    
    print("\n📋 步骤3：Actor读取配置")
    print("-" * 70)
    
    # 4. Actor读取配置
    actor.request_and_load_config(context)
    
    print("\n📋 步骤4：查看System Prompt")
    print("-" * 70)
    
    # 5. 生成第一轮回复（会自动打印System Prompt）
    print("\n🔍 正在生成第一轮回复，System Prompt将在下方显示：\n")
    
    # 注意：这里不会真正调用API，因为我们只想看prompt
    # 所以我们直接调用prompt生成函数
    from Benchmark.prompts.actor_prompts import generate_actor_prompts_with_config
    
    system_prompt, user_prompt = generate_actor_prompts_with_config(
        history=[],
        persona=actor.persona,
        scenario=actor.scenario,
        topic=None
    )
    
    print("=" * 70)
    print("🔍 SYSTEM PROMPT（发送给LLM的角色设定）")
    print("=" * 70)
    print(system_prompt)
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("🔍 USER PROMPT（第一轮的用户输入）")
    print("=" * 70)
    print(user_prompt)
    print("=" * 70)
    
    print("\n" + "=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)
    
    print("\n📊 配置摘要：")
    print(f"  角色: {config['persona']['name']} ({config['persona']['persona_id']})")
    print(f"  场景: {config['scenario']['title']} ({config['scenario']['scenario_id']})")
    print(f"  角色特征: {', '.join(config['persona']['traits'])}")
    print(f"  场景情绪: {config['scenario']['initial_emotion']}")
    
    print("\n💡 提示：")
    print("  从上面的System Prompt中可以看到：")
    print("  ✓ Persona（角色设定）已注入")
    print("  ✓ Scenario（剧本信息）已注入")
    print("  ✓ 角色名称、描述、特征、沟通风格都已包含")
    print("  ✓ 场景标题、描述、情绪、冲突都已包含")

if __name__ == "__main__":
    test_actor_prompt()

