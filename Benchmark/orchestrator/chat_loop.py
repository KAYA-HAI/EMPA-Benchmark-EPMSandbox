# Benchmark/orchestrator/chat_loop.py (Judger和Director完全解耦版)
from Benchmark.orchestrator.progress_tracker import ProgressTracker
from Benchmark.orchestrator.termination import check_termination
from Benchmark.orchestrator.director_orchestrator import (
    process_director_output, 
    process_judger_evaluation,
    process_final_evaluation,
    ConversationContext
)

def run_chat_loop(actor, director, judger, test_model, topic, max_turns=30, target_progress=100):
    """
    主Benchmark聊天循环（Judger和Director完全解耦版）
    
    设计原则：
    - Judger：固定每3轮评估一次，评估最近3轮的共情表现
    - Director：每轮都分析，自主决定是否介入
    - 两者完全独立，互不影响
    
    终止条件：
    1. 进度分数达到目标（≥target_progress）
    2. 达到最大回合数（max_turns）
    """
    tracker = ProgressTracker()
    history = []
    should_continue_conversation = True
    termination_reason = "对话正常结束"
    
    print(f"\n{'='*60}")
    print(f"🎭 Benchmark 开始")
    print(f"{'='*60}\n")

    # === 对话初始化流程 ===
    print(f"{'🎬'*20}")
    print(f"🎬 [初始化阶段] Actor请求Director生成配置...")
    print(f"{'🎬'*20}\n")
    
    # 1. Director生成配置（从角色库和剧本库抽取）
    conversation_config = director.initialize_conversation_config()
    
    # 2. 初始化上下文对象并存储配置
    context = ConversationContext()
    context.history = history
    context.topic = topic
    context.set_actors(actor=actor, director=director, judger=judger, test_model=test_model)
    
    # 3. 将Director生成的配置传递给Orchestrator（存入上下文）
    context.set_variables(
        persona=conversation_config['persona'],
        scenario=conversation_config['scenario']
    )
    
    print(f"\n{'📦'*20}")
    print(f"📦 [初始化阶段] Director配置已传递给Orchestrator")
    print(f"{'📦'*20}\n")
    
    # 4. Actor从Orchestrator读取配置
    actor_config_loaded = actor.request_and_load_config(context)
    
    if not actor_config_loaded:
        print(f"⚠️ [初始化] Actor配置加载失败，将使用降级模式")
    
    print(f"\n{'='*60}")
    print(f"✅ 初始化完成，开始对话")
    print(f"📋 角色: {conversation_config['persona']['name']}")
    print(f"📋 场景: {conversation_config['scenario']['title']}")
    print(f"🎯 评估机制:")
    print(f"   📊 Judger: 固定每3轮评估共情表现")
    print(f"   🎬 Director: 每轮分析，自主决定介入时机")
    print(f"⏱️  最大回合数: {max_turns}")
    print(f"🎯 目标分数: {target_progress}")
    print(f"{'='*60}\n")

    # 主循环
    while should_continue_conversation:
        current_turn = tracker.get_turn_count() + 1
        
        print(f"\n{'='*60}")
        print(f"🔄 回合 {current_turn}/{max_turns}")
        print(f"{'='*60}")
        
        # 1. Actor倾诉
        director_guidance = context.get_variable('latest_director_guidance', None)
        actor_reply = actor.generate_reply(history, topic, director_guidance)
        history.append({"role": "actor", "content": actor_reply})
        print(f"💬 倾诉者: {actor_reply}")
        
        # 2. TestModel共情回应
        test_model_reply = test_model.generate_reply(history)
        history.append({"role": "test_model", "content": test_model_reply})
        print(f"🤖 AI助手: {test_model_reply}")
        
        # 3. 更新回合数
        tracker.increment_turn()
        current_progress = tracker.get_progress()
        
        # 更新上下文
        context.history = history
        context.set_variables(
            turn_count=tracker.get_turn_count(),
            current_turn=current_turn,
            progress=current_progress
        )
        
        # ═══════════════════════════════════════════════════════════
        # 4. Judger独立评估（固定每3轮）
        # ═══════════════════════════════════════════════════════════
        if tracker.get_turn_count() % 3 == 0 and tracker.get_turn_count() > 0:
            print(f"\n{'📊'*20}")
            print(f"📊 [Judger评估] 第 {tracker.get_turn_count()} 轮（固定每3轮评估）")
            print(f"{'📊'*20}")
            
            # 获取最近3轮对话
            recent_turns = history[-6:] if len(history) >= 6 else history
            
            # Judger独立评估
            judger_result = process_judger_evaluation(recent_turns, current_progress, context)
            progress_increment = judger_result.get("progress_increment", 0)
            quality_score = judger_result.get("quality_score", 50)
            
            # 更新tracker进度
            tracker.update_score(progress_increment)
            updated_progress = tracker.get_progress()
            
            # 记录评估结果
            tracker.add_evaluation({
                "score_increment": progress_increment,
                "quality_score": quality_score,
                "emotion_trend": "好转" if progress_increment > 0 else "恶化" if progress_increment < 0 else "不变"
            })
            
            print(f"\n✅ Judger评估完成：")
            print(f"   进度增量: {progress_increment}")
            print(f"   质量分数: {quality_score}/100")
            print(f"   更新进度: {current_progress} → {updated_progress}\n")
            
            # 更新进度到context
            context.set_variables(progress=updated_progress)
            current_progress = updated_progress
        
        # ═══════════════════════════════════════════════════════════
        # 5. Director独立决策（每轮都分析，自主决定是否介入）
        # ═══════════════════════════════════════════════════════════
        print(f"\n{'🎬'*20}")
        print(f"🎬 [Director分析] 第 {tracker.get_turn_count()} 轮（随时决策）")
        print(f"{'🎬'*20}")
        
        # Director分析并决策
        director_result = director.evaluate_continuation(history, current_progress)
        
        # 检查Director是否选择介入
        if director_result.get('no_intervention'):
            # Director选择了observe_and_wait，暂不介入
            print(f"👁️  [Director] 决定暂不介入，继续观察\n")
            
        else:
            # Director选择了介入（释放剧情信息）
            print(f"\n✅ Director介入决策：")
            
            # 显示function call信息
            if 'function_call' in director_result:
                func_call = director_result['function_call']
                print(f"   🎬 调用函数: {func_call['name']}")
                if 'plot_action' in director_result:
                    print(f"   📖 剧情动作: {director_result['plot_action']}")
                if 'fragment_id' in func_call:
                    print(f"   📌 释放片段: {func_call['fragment_id']}")
            
            if director_result.get('guidance'):
                print(f"\n📝 传递给Actor的指导：")
                guidance_preview = director_result['guidance'].replace('\n', ' ')[:150]
                print(f"   {guidance_preview}...")
            
            print()
            
            # 编排器处理Director输出
            should_continue_conversation = process_director_output(director_result, context)
        
        # 6. 终止检查
        should_terminate, termination_reason = check_termination(
            tracker=tracker, 
            max_turns=max_turns, 
            target_progress=target_progress
        )
        
        if should_terminate:
            should_continue_conversation = False
            break
    
    # 7. 对话结束 - 最终整体质量评估
    print(f"\n{'🎯'*20}")
    print(f"🎯 [最终评估] 对话结束，进行整体质量评估...")
    print(f"{'🎯'*20}")
    
    overall_quality_score = process_final_evaluation(history, context)
    
    # 8. 生成最终结果
    final_progress = tracker.get_progress()
    is_fully_recovered = final_progress >= target_progress
    
    print(f"\n{'='*60}")
    print(f"🏁 对话终止: {termination_reason}")
    print(f"🔢 总回合数: {tracker.get_turn_count()}")
    print(f"📊 最终进度: {final_progress}/{target_progress}")
    print(f"🎯 整体质量: {overall_quality_score}/100")
    print(f"✅ 完全恢复: {'是' if is_fully_recovered else '否'}")
    print(f"{'='*60}\n")
    
    # 返回完整结果（包含配置信息）
    return {
        "total_turns": tracker.get_turn_count(),
        "termination_reason": termination_reason,
        "topic": topic,
        "history": history,
        "final_progress": final_progress,
        "is_fully_recovered": is_fully_recovered,
        "overall_quality_score": overall_quality_score,
        "quality_scores_history": context.get_variable('quality_scores_history', []),
        # 配置信息
        "persona": conversation_config['persona'],
        "scenario": conversation_config['scenario']
    }
