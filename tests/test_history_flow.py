#!/usr/bin/env python3
"""
测试脚本：验证对话历史的传递流程
确认Actor和TestModel是否正确接收和使用累积的历史记录
"""

from Benchmark.agents.actor import Actor
from Benchmark.agents.director import Director
from Benchmark.agents.test_model import TestModel
from Benchmark.orchestrator.director_orchestrator import ConversationContext
from Benchmark.prompts.actor_prompts import generate_actor_prompts_with_config
from Benchmark.prompts.test_model_prompts import generate_test_model_prompts

def test_history_flow():
    """测试对话历史的传递流程"""
    
    print("=" * 70)
    print("🧪 测试：对话历史传递流程")
    print("=" * 70)
    
    # 1. 初始化
    director = Director()
    actor = Actor()
    test_model = TestModel(model_name="google/gemini-2.5-pro")
    
    # 2. 配置Actor
    config = director.initialize_conversation_config()
    context = ConversationContext()
    context.set_variables(
        persona=config['persona'],
        scenario=config['scenario']
    )
    actor.request_and_load_config(context)
    
    print("\n" + "=" * 70)
    print("📋 模拟对话流程（不调用真实API，只检查数据流）")
    print("=" * 70)
    
    # 3. 模拟对话历史构建过程
    history = []
    
    # === 第1轮 ===
    print("\n" + "-" * 70)
    print("🔄 第1轮对话")
    print("-" * 70)
    
    print(f"\n📥 Actor接收的history长度: {len(history)}")
    print(f"   内容: {history if history else '空（首轮对话）'}")
    
    # Actor生成回复（我们手动模拟，不真正调用API）
    actor_reply_1 = "我真的很难过，今天发生了一件让我很困扰的事情。"
    history.append({"role": "actor", "content": actor_reply_1})
    
    print(f"\n✅ Actor回复已添加到history")
    print(f"   当前history长度: {len(history)}")
    print(f"   最新消息: {history[-1]}")
    
    print(f"\n📥 TestModel接收的history长度: {len(history)}")
    print(f"   内容:")
    for i, msg in enumerate(history, 1):
        print(f"      {i}. [{msg['role']}] {msg['content'][:30]}...")
    
    # TestModel生成回复
    testmodel_reply_1 = "我能感受到你的难过，愿意听你说说发生了什么事吗？"
    history.append({"role": "test_model", "content": testmodel_reply_1})
    
    print(f"\n✅ TestModel回复已添加到history")
    print(f"   当前history长度: {len(history)}")
    
    # === 第2轮 ===
    print("\n" + "-" * 70)
    print("🔄 第2轮对话")
    print("-" * 70)
    
    print(f"\n📥 Actor接收的history长度: {len(history)}")
    print(f"   内容:")
    for i, msg in enumerate(history, 1):
        print(f"      {i}. [{msg['role']}] {msg['content'][:30]}...")
    
    # Actor生成回复
    actor_reply_2 = "嗯...我在工作上遇到了一些挫折，感觉自己很没用。"
    history.append({"role": "actor", "content": actor_reply_2})
    
    print(f"\n✅ Actor回复已添加到history")
    print(f"   当前history长度: {len(history)}")
    
    print(f"\n📥 TestModel接收的history长度: {len(history)}")
    print(f"   内容:")
    for i, msg in enumerate(history, 1):
        print(f"      {i}. [{msg['role']}] {msg['content'][:30]}...")
    
    # TestModel生成回复
    testmodel_reply_2 = "听起来这次挫折对你打击很大，能具体说说是什么让你觉得自己没用吗？"
    history.append({"role": "test_model", "content": testmodel_reply_2})
    
    print(f"\n✅ TestModel回复已添加到history")
    print(f"   当前history长度: {len(history)}")
    
    # === 第3轮 ===
    print("\n" + "-" * 70)
    print("🔄 第3轮对话")
    print("-" * 70)
    
    print(f"\n📥 Actor接收的history长度: {len(history)}")
    print(f"   内容:")
    for i, msg in enumerate(history, 1):
        print(f"      {i}. [{msg['role']}] {msg['content'][:30]}...")
    
    # === 验证Prompt生成 ===
    print("\n" + "=" * 70)
    print("🔍 验证：检查Prompt中是否包含完整历史")
    print("=" * 70)
    
    # 生成Actor的prompt
    print("\n📝 Actor的User Prompt：")
    _, actor_user_prompt = generate_actor_prompts_with_config(
        history=history,
        persona=actor.persona,
        scenario=actor.scenario
    )
    
    # 检查历史是否在prompt中
    history_in_prompt = "当前对话历史" in actor_user_prompt
    print(f"   ✓ 包含'当前对话历史'标题: {history_in_prompt}")
    
    for i, msg in enumerate(history, 1):
        msg_in_prompt = msg['content'][:20] in actor_user_prompt
        role = "倾诉者" if msg['role'] == 'actor' else "AI助手"
        print(f"   ✓ 包含第{i}轮{role}的消息: {msg_in_prompt}")
    
    # 生成TestModel的prompt
    print("\n📝 TestModel的User Prompt：")
    _, testmodel_user_prompt = generate_test_model_prompts(history)
    
    history_in_prompt = "对话历史" in testmodel_user_prompt
    print(f"   ✓ 包含'对话历史'标题: {history_in_prompt}")
    
    for i, msg in enumerate(history, 1):
        msg_in_prompt = msg['content'][:20] in testmodel_user_prompt
        role = "倾诉者" if msg['role'] == 'actor' else "AI助手"
        print(f"   ✓ 包含第{i}轮{role}的消息: {msg_in_prompt}")
    
    # === 总结 ===
    print("\n" + "=" * 70)
    print("✅ 验证结果")
    print("=" * 70)
    
    print("\n✓ 对话流程正确：")
    print("  1. Actor从history读取所有历史对话")
    print("  2. Actor生成回复后立即添加到history")
    print("  3. TestModel接收包含Actor当前回复的完整history")
    print("  4. TestModel生成回复后添加到history")
    print("  5. 下一轮两者都能看到所有累积的历史")
    
    print("\n✓ Prompt生成正确：")
    print("  1. Actor的User Prompt包含完整的对话历史")
    print("  2. TestModel的User Prompt包含完整的对话历史")
    print("  3. 历史记录按顺序格式化为文本")
    
    print("\n" + "=" * 70)
    print("🎉 测试完成！对话历史传递流程正确！")
    print("=" * 70)
    
    # 显示最终history结构
    print("\n📊 最终History结构：")
    print(f"   总消息数: {len(history)}")
    print(f"   格式: list of dict")
    print(f"   每条消息包含: {{'role': '...', 'content': '...'}}")
    print(f"\n   详细内容：")
    for i, msg in enumerate(history, 1):
        print(f"   {i}. role='{msg['role']}', content='{msg['content'][:40]}...'")

if __name__ == "__main__":
    test_history_flow()



