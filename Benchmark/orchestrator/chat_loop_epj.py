# Benchmark/orchestrator/chat_loop_epj.py
"""
基于EPJ系统的对话循环

EPJ三层架构：
1. Judger (传感器) - 填写心理量表
2. Orchestrator (计算器) - 计算向量和生成状态数据包
3. Director (决策者) - 基于状态数据包做决策
"""

from Benchmark.orchestrator.epj_orchestrator import EPJOrchestrator


def run_chat_loop_epj(actor, director, judger, test_model, script_id: str, max_turns=30, K=3, test_model_name: str = None):
    """
    基于EPJ系统的对话循环
    
    Args:
        actor: Actor实例
        director: Director实例
        judger: Judger实例
        test_model: TestModel实例
        script_id: 剧本ID（如"001"）
        max_turns: 最大轮次
        K: 评估周期（每K轮评估一次）
        test_model_name: 被测试模型名称（可选，用于结果记录）
    
    Returns:
        dict: 对话结果
    """
    from Benchmark.topics.config_loader import load_config
    
    print(f"\n{'='*70}")
    print(f"🎭 EPJ Benchmark 开始")
    print(f"{'='*70}\n")
    
    # ═══════════════════════════════════════════════════════════════
    # 初始化阶段
    # ═══════════════════════════════════════════════════════════════
    
    print(f"🎬 阶段1: 加载配置")
    
    # 加载剧本配置
    config = load_config(script_id)
    actor_prompt = config['actor_prompt']
    scenario = config['scenario']
    
    print(f"✅ 剧本配置加载完成")
    print(f"   剧本编号: {scenario.get('剧本编号')}")
    print(f"   Actor Prompt: {len(actor_prompt)} 字符")
    
    # 🔧 优化：提前提取Judger所需的精简上下文（只提取一次）
    from Benchmark.epj.judger_prompts import _extract_judger_context
    judger_context = _extract_judger_context(actor_prompt)
    print(f"   Judger Context: {len(judger_context)} 字符 (压缩率: {len(judger_context)/len(actor_prompt)*100:.1f}%)")
    
    # 初始化EPJ Orchestrator
    epj_orch = EPJOrchestrator(judger, threshold_type="high_threshold", K=K, max_turns=max_turns)
    
    # ═══════════════════════════════════════════════════════════════
    # T=0: EPJ初始化 - 使用预先计算的IEDR
    # ═══════════════════════════════════════════════════════════════
    
    print(f"\n🎬 阶段2: EPJ初始化 (T=0) - 加载预先计算的IEDR")
    
    # 🔧 优化：script_content传递精简的judger_context而不是完整actor_prompt
    script_content = {
        "actor_prompt": actor_prompt,  # 完整版（给IEDR初始化用，如果需要）
        "judger_context": judger_context,  # 精简版（给MDEP-PR评估用）
        "scenario": scenario
    }
    
    # 🔧 优化: 从批量评估结果中加载IEDR，避免重复计算
    from Benchmark.epj.iedr_loader import load_precomputed_iedr
    
    # 尝试加载预先计算的IEDR
    precomputed_data = load_precomputed_iedr(script_id)
    
    if precomputed_data and precomputed_data['status'] == 'success':
        # 使用预先计算的IEDR
        filled_iedr = precomputed_data['iedr']
        P_0_dict = precomputed_data['P_0']
        P_0 = (P_0_dict['C'], P_0_dict['A'], P_0_dict['P'])
        
        # 🆕 附加EPM参数（如果存在）
        if 'epm' in precomputed_data:
            filled_iedr['epm'] = precomputed_data['epm']
        
        print(f"✅ 从批量评估结果加载IEDR")
        print(f"   IEDR: C=[{filled_iedr['C.1']},{filled_iedr['C.2']},{filled_iedr['C.3']}] "
              f"A=[{filled_iedr['A.1']},{filled_iedr['A.2']},{filled_iedr['A.3']}] "
              f"P=[{filled_iedr['P.1']},{filled_iedr['P.2']},{filled_iedr['P.3']}]")
        
        # 使用新的初始化方法（跳过Judger调用）
        init_result = epj_orch.initialize_with_precomputed_iedr(filled_iedr, P_0)
    else:
        # 回退：如果找不到预计算的IEDR，使用原来的方法
        print(f"⚠️  未找到预计算的IEDR，将实时计算（消耗API）")
        init_result = epj_orch.initialize_at_T0(script_content)
        P_0 = init_result['P_0']
    
    print(f"\n✅ EPJ初始化完成")
    print(f"   初始赤字向量 P_0 = {P_0}")
    print(f"   初始距离 = {init_result['initial_distance']:.2f}")
    
    # ═══════════════════════════════════════════════════════════════
    # 初始化 Actor 和 Director
    # ═══════════════════════════════════════════════════════════════
    
    print(f"\n🎬 阶段3: 初始化 Actor 和 Director")
    
    # Actor获得system prompt（通过set_system_prompt方法，会自动预处理）
    actor.set_system_prompt(actor_prompt)
    
    # Director获得scenario和actor_prompt
    # 注意：Director在外部已经初始化，这里只是确认
    print(f"✅ Director 持有 scenario（{len(director.stages)} 个阶段）")
    
    # ═══════════════════════════════════════════════════════════════
    # 对话循环
    # ═══════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print(f"🎬 开始对话循环")
    print(f"{'='*70}\n")
    
    history = []
    turn_count = 0
    should_continue = True
    termination_reason = None
    
    # 收集最近K轮用于评估
    recent_turns_buffer = []
    
    # 🔧 修复时序问题：存储待传递给下一轮Actor的指导
    pending_guidance = None
    
    # 🆕 EPM v2.0: 存储最新的state_packet（包含epm_summary）
    latest_state_packet = None
    
    # 🆕 EPM v2.0: 存储详细的胜利条件分析（如果EPM触发停机）
    epm_victory_analysis = None
    
    while should_continue and turn_count < max_turns:
        turn_count += 1
        
        print(f"\n{'='*60}")
        print(f"🔄 第 {turn_count}/{max_turns} 轮")
        print(f"{'='*60}")
        
        # 1. Actor 生成回复
        # 🔧 修复：使用pending_guidance（上一轮末尾设置的指导）
        if turn_count == 1:
            # 第一轮，Actor主动开启话题
            actor_message = actor.generate_reply([], None, None)
        else:
            # 后续轮次，基于对话历史和Director指导
            if pending_guidance:
                print(f"🔄 [Actor] 收到Director指导: {pending_guidance[:100]}...")
            actor_message = actor.generate_reply(history, None, pending_guidance)
        
        print(f"💬 Actor: {actor_message}")
        
        # 🔧 关键修复：在TestModel回复前，先将Actor的消息加入history
        history.append({"role": "actor", "content": actor_message})
        
        # 2. TestModel 回复（现在可以看到Actor刚说的话了）
        test_model_message = test_model.generate_reply(history)
        print(f"🤖 TestModel: {test_model_message}")
        
        # 3. 记录本轮对话
        turn_record = {
            "turn": turn_count,
            "actor": actor_message,
            "test_model": test_model_message
        }
        
        history.append({"role": "test_model", "content": test_model_message})
        
        recent_turns_buffer.append(turn_record)
        
        # 保持buffer长度为K
        if len(recent_turns_buffer) > K:
            recent_turns_buffer.pop(0)
        
        # ═══════════════════════════════════════════════════════════════
        # EPJ 评估（每K轮）
        # ═══════════════════════════════════════════════════════════════
        
        if epj_orch.should_evaluate(turn_count):
            print(f"\n{'🔬'*20}")
            print(f"🔬 EPJ 评估时刻（第{turn_count}轮）")
            print(f"{'🔬'*20}")
            
            # Judger填表 → Orchestrator计算 → 生成状态数据包
            # 🔧 问题3修复：传递script_content让Judger能代入Actor视角
            # 🆕 传递完整历史（用于上下文）+ 最近K轮（用于标注评估范围）
            state_packet = epj_orch.evaluate_at_turn_K(
                recent_turns=recent_turns_buffer,  # 最近K轮（评估范围）
                full_history=history,  # 完整历史（供参考）
                current_turn=turn_count, 
                script_content=script_content
            )
            
            # 🆕 EPM v2.0: 保存最新的state_packet（供Director剧情控制使用）
            latest_state_packet = state_packet
            
            # 🆕 EPM v2.0: 检查能量动力学判停（如果启用）
            epm_stop_triggered = False
            epm_summary = state_packet.get('epm_summary', None)  # 提前获取epm_summary
            
            if epm_summary and epm_summary['success']:
                epm_stop_triggered = True
                
                print(f"\n🎉 [EPM v2.0] 检测到胜利条件!")
                print(f"   胜利类型: {epm_summary['victory_type']}")
                print(f"   指标: E_total={epm_summary['metrics']['E_total']}, "
                      f"r_t={epm_summary['metrics']['r_t']}, "
                      f"projection={epm_summary['metrics']['projection']}")
                print(f"   阈值: ε_energy={epm_summary['thresholds']['epsilon_energy']}, "
                      f"ε_distance={epm_summary['thresholds']['epsilon_distance']}, "
                      f"ε_direction={epm_summary['thresholds']['epsilon_direction']}")
                
                # 🆕 生成详细的胜利条件分析
                metrics = epm_summary['metrics']
                thresholds = epm_summary['thresholds']
                
                # 检查每个条件是否达成
                geometric_achieved = metrics['r_t'] <= thresholds['epsilon_distance']
                positional_achieved = metrics['projection'] >= -thresholds['epsilon_direction']
                energetic_achieved = metrics['E_total'] >= thresholds['epsilon_energy']
                
                epm_victory_analysis = {
                    "primary_victory_type": epm_summary['victory_type'],
                    "conditions": {
                        "geometric": {
                            "name": "几何胜利（距离条件）",
                            "achieved": geometric_achieved,
                            "metric": "r_t",
                            "value": metrics['r_t'],
                            "threshold": thresholds['epsilon_distance'],
                            "formula": "r_t ≤ ε_distance",
                            "description": "当前位置距离原点足够近"
                        },
                        "positional": {
                            "name": "位置胜利（穿越条件）",
                            "achieved": positional_achieved,
                            "metric": "projection",
                            "value": metrics['projection'],
                            "threshold": -thresholds['epsilon_direction'],
                            "formula": "P_t · v*_0 ≥ -ε_direction",
                            "description": "成功穿越目标区域（从负半空间到正半空间）"
                        },
                        "energetic": {
                            "name": "能量胜利（累积条件）",
                            "achieved": energetic_achieved,
                            "metric": "E_total",
                            "value": metrics['E_total'],
                            "threshold": thresholds['epsilon_energy'],
                            "formula": "E_total ≥ ε_energy",
                            "description": "累积的有效共情能量达到初始赤字水平"
                        }
                    },
                    "achieved_conditions": [
                        k for k, v in {
                            "geometric": geometric_achieved,
                            "positional": positional_achieved,
                            "energetic": energetic_achieved
                        }.items() if v
                    ],
                    "turn_at_victory": turn_count,
                    "initial_deficit": epj_orch.get_initial_deficit(),
                    "final_position": epj_orch.get_current_position()
                }
                
                # EPM成功时，自动触发停机
                should_continue = False
                victory_type_zh = {
                    "geometric": "几何胜利（精准到达原点附近）",
                    "positional": "位置胜利（成功穿越或接近目标区域）",
                    "energetic": "能量胜利（累积足够的共情能量）"
                }
                termination_reason = f"EPM v2.0 判定成功: {victory_type_zh.get(epm_summary['victory_type'], epm_summary['victory_type'])}"
                termination_type = f"EPM_SUCCESS_{epm_summary['victory_type'].upper()}"
                
                print(f"\n🏁 [EPM判停] 对话成功终止")
                print(f"   类型: {termination_type}")
                print(f"   理由: {termination_reason}")
                print(f"   达成条件: {', '.join(epm_victory_analysis['achieved_conditions'])}")
                
                break
            
            # 🚫 EPM失败检测：陷入停滞、持续倒退等兜底逻辑
            elif epm_summary.get('failure_detected', False):
                failure_reasons = epm_summary.get('failure_reasons', {})
                failure_list = []
                if failure_reasons.get('collapsed'):
                    failure_list.append("连续5轮负能量（方向崩溃）")
                if failure_reasons.get('stagnant'):
                    failure_list.append("位置停滞不前")
                if failure_reasons.get('regressing'):
                    failure_list.append("持续倒退（8轮中70%负能量）")
                
                should_continue = False
                termination_reason = f"EPM v2.0 判定失败: {', '.join(failure_list)}"
                termination_type = "EPM_FAILURE"
                
                print(f"\n🏁 [EPM判停] 对话失败终止")
                print(f"   类型: {termination_type}")
                print(f"   理由: {termination_reason}")
                print(f"   失败原因详情:")
                for reason, detected in failure_reasons.items():
                    if detected:
                        reason_map = {
                            'collapsed': '❌ 方向崩溃: 连续5轮能量增量为负',
                            'stagnant': '❌ 陷入停滞: 位置变化标准差 < 0.5',
                            'regressing': '❌ 持续倒退: 近8轮中70%为负能量且总损失>1'
                        }
                        print(f"      {reason_map.get(reason, reason)}")
                
                epm_stop_triggered = True
                break
            
            # Director基于状态数据包做决策（EPJ v1.0 或 EPM未触发时）
            epj_decision = None
            if not epm_stop_triggered:
                epj_decision = director.make_epj_decision(state_packet, history)
                
                print(f"\n📋 EPJ决策结果:")
                print(f"   决策: {epj_decision['decision']}")
                print(f"   理由: {epj_decision['reason']}")
                
                # 处理EPJ决策
                if epj_decision['decision'] == 'STOP':
                    should_continue = False
                    termination_reason = epj_decision['reason']
                    termination_type = epj_decision.get('termination_type', 'UNKNOWN')
                    
                    print(f"\n🏁 [EPJ决策] 对话终止")
                    print(f"   类型: {termination_type}")
                    print(f"   理由: {termination_reason}")
                    
                    break
                
                # 如果继续，检查是否有EPJ指导
                if epj_decision.get('guidance'):
                    # 将EPJ指导传递给下一轮
                    # 这里暂存到最后一条记录中
                    history[-1]['epj_guidance'] = epj_decision['guidance']
                    print(f"\n💡 EPJ提供指导: {epj_decision['guidance'][:100]}...")
        
        # ═══════════════════════════════════════════════════════════════
        # Director 剧情控制（每轮都可能介入）
        # ═══════════════════════════════════════════════════════════════
        
        # 准备完整的EPJ状态数据包（传递给Director）
        # 核心原则：不传递单一的"进度百分比"，而是传递完整的向量状态
        current_epj_state = None
        ref_progress = 0
        
        if epj_orch.initialized:
            # 获取最新的EPJ状态
            trajectory = epj_orch.get_trajectory()
            if trajectory:
                latest_point = trajectory[-1]
                from Benchmark.epj.display_metrics import calculate_display_progress
                
                # 构建完整的EPJ状态数据包（包含EPM v2.0数据）
                current_epj_state = {
                    "P_0_start_deficit": epj_orch.get_initial_deficit(),
                    "P_t_current_position": epj_orch.get_current_position(),
                    "v_t_last_increment": latest_point.get('v_t', (0,0,0)),
                    "distance_to_goal": latest_point.get('distance', 0),
                    "display_progress": calculate_display_progress(
                        epj_orch.get_current_position(),
                        epj_orch.get_initial_deficit()
                    ),
                    # 🆕 EPM v2.0 数据
                    "trajectory": trajectory,  # 完整轨迹（包含每轮的epm数据）
                    "epm_summary": latest_state_packet.get('epm_summary') if latest_state_packet else None  # 从最新的EPJ评估获取
                }
                
                ref_progress = int(current_epj_state['display_progress'])
                print(f"\n   📊 EPJ状态：P_t={current_epj_state['P_t_current_position']}, "
                      f"显示进度={ref_progress}%（仅供参考）")
        
        # Director基于EPJ状态评估并决策
        # 完全依赖Director的智能分析，而不是预先的简单判断
        director_result = director.evaluate_continuation(
            history=history,
            progress=None,  # 不使用单一分数
            epj_state=current_epj_state  # 传递完整的向量状态
        )
        
        # ═══════════════════════════════════════════════════════════════
        # 🔧 修复: 检查Director是否要求终止对话（问题5修复）
        # ═══════════════════════════════════════════════════════════════
        if director_result.get('should_continue') == False:
            should_continue = False
            termination_reason = director_result.get('guidance', 'Director决定结束对话')
            
            print(f"\n🏁 [Director] 主动终止对话")
            print(f"   原因: {termination_reason}")
            
            # 如果有final_guidance，传递给Actor（让Actor说结束语）
            if director_result.get('guidance'):
                history[-1]['director_guidance'] = director_result['guidance']
                print(f"   最后指导: {director_result['guidance'][:100]}...")
            
            break  # 立即退出对话循环
        
        # Director自己决定是否需要介入
        # 通过返回no_intervention标志或guidance内容来控制
        if director_result.get('guidance') and not director_result.get('no_intervention'):
            print(f"\n🎬 Director 介入剧情控制")
            # 🔧 修复：将指导存入pending_guidance，供下一轮Actor使用
            pending_guidance = director_result['guidance']
            # 同时也记录到history中（用于日志和分析）
            history[-1]['director_guidance'] = director_result['guidance']
            print(f"💡 Director剧情指导: {pending_guidance[:100]}...")
        else:
            print(f"👁️  Director 观察中（未介入）")
            # 清空pending_guidance（本轮没有新指导）
            pending_guidance = None
    
    # ═══════════════════════════════════════════════════════════════
    # 对话结束
    # ═══════════════════════════════════════════════════════════════
    
    print(f"\n{'='*70}")
    print(f"🏁 对话结束")
    print(f"{'='*70}")
    
    # 获取最终状态
    final_position = epj_orch.get_current_position()
    trajectory = epj_orch.get_trajectory()
    
    print(f"\n📊 EPJ最终统计:")
    print(f"   总轮次: {turn_count}")
    print(f"   总评估次数: {len(trajectory) - 1}")  # 减去T=0
    print(f"   初始赤字: {epj_orch.get_initial_deficit()}")
    print(f"   最终位置: {final_position}")
    print(f"   终止原因: {termination_reason}")
    
    # 生成结果
    result = {
        "total_turns": turn_count,
        "termination_reason": termination_reason,
        "script_id": script_id,
        "scenario": scenario,
        "history": history,
        
        # 模型信息
        "test_model_name": test_model_name if test_model_name else "unknown",
        "actor_model": getattr(actor, 'model_name', 'unknown') if hasattr(actor, 'model_name') else 'unknown',
        "judger_model": getattr(judger, 'model_name', 'unknown') if hasattr(judger, 'model_name') else 'unknown',
        "director_model": getattr(director, 'model_name', 'unknown') if hasattr(director, 'model_name') else 'unknown',
        
        # EPJ数据
        "epj": {
            "P_0_initial_deficit": epj_orch.get_initial_deficit(),
            "P_final_position": final_position,
            "trajectory": trajectory,  # 现在包含每轮的detailed_analysis和EPM数据
            "total_evaluations": len(trajectory) - 1,
            "K": K,
            "epsilon": epj_orch.calculator.epsilon,
            
            # 添加IEDR详细信息（如果有）
            "iedr_details": epj_orch.iedr_result if hasattr(epj_orch, 'iedr_result') and epj_orch.iedr_result else None,
            
            # 🆕 EPM v2.0 参数（如果启用）
            "epm_enabled": epj_orch.calculator.enable_epm,
            "epm_params": {
                "v_star_0": list(epj_orch.calculator.v_star_0) if epj_orch.calculator.v_star_0 else None,
                "epsilon_distance": epj_orch.calculator.epsilon_distance_relative,
                "epsilon_direction": epj_orch.calculator.epsilon_direction_relative,
                "epsilon_energy": epj_orch.calculator.epsilon_energy,
                "E_total_final": epj_orch.calculator.E_total,
                "alpha": 0.10  # 相对阈值系数
            } if epj_orch.calculator.enable_epm and epj_orch.calculator.v_star_0 else None,
            
            # 🆕 EPM v2.0 胜利条件详细分析（如果触发EPM停机）
            "epm_victory_analysis": epm_victory_analysis
        }
    }
    
    return result


# ═══════════════════════════════════════════════════════════════
# 测试
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("EPJ Chat Loop 测试需要完整的Agent实例")
    print("请使用 run_demo_epj.py 进行测试")

