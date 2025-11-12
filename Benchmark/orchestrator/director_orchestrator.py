# Benchmark/orchestrator/director_orchestrator.py (继续添加)

class ConversationContext:
    """
    对话上下文对象 - 作为变量中转站
    """
    def __init__(self):
        self.history = []
        self.topic = None
        self.actors = {}
        self.variables = {}
    
    def set_actors(self, **actors):
        """设置所有参与者"""
        self.actors.update(actors)
    
    def set_variables(self, **variables):
        """设置任意变量"""
        self.variables.update(variables)
    
    def get_actor(self, name):
        """获取指定参与者"""
        return self.actors.get(name)
    
    def get_variable(self, name, default=None):
        """获取指定变量"""
        return self.variables.get(name, default)


class DirectorOrchestrator:
    """
    Director编排器 - 处理Director输出并协调后续流程
    """
    def __init__(self):
        self.context = None
        self.quality_scores_history = []  # 记录过程质量分数历史
    
    def set_context(self, context: ConversationContext):
        """设置对话上下文"""
        self.context = context
    
    def process_judger_evaluation(self, recent_turns: list, current_progress: int) -> dict:
        """
        处理Judger评估，更新进度和质量分数
        
        Args:
            recent_turns: 最近3轮对话记录
            current_progress: 当前累计进度
            
        Returns:
            dict: 包含进度增量和质量分数的结果
        """
        if not self.context:
            raise ValueError("请先设置ConversationContext")
        
        # 获取judger实例
        judger = self.context.get_actor('judger')
        if not judger:
            print("⚠️ [编排器] 未找到Judger实例，跳过评估")
            return {"progress_increment": 0, "quality_score": 50}
        
        print(f"🎯 [编排器] 开始Judger评估...")
        
        try:
            # 1. 评估共情进度
            progress_score = judger.evaluate_empathy_progress(recent_turns, current_progress)
            
            # 2. 评估共情质量
            quality_score = judger.evaluate_empathy_quality(recent_turns)
            
            # 3. 记录质量分数历史
            self.quality_scores_history.append(quality_score)
            
            # 4. 存储评估结果到上下文
            self.context.set_variables(
                latest_progress_increment=progress_score,
                latest_quality_score=quality_score,
                quality_scores_history=self.quality_scores_history.copy()
            )
            
            print(f"📊 [编排器] Judger评估完成:")
            print(f"    进度增量: {progress_score}")
            print(f"    质量分数: {quality_score}")
            
            return {
                "progress_increment": progress_score,
                "quality_score": quality_score
            }
            
        except Exception as e:
            print(f"!!! [编排器] Judger评估失败: {e}")
            return {"progress_increment": 0, "quality_score": 50}
    
    def process_director_output(self, director_result: dict) -> bool:
        """
        处理Director输出，格式化存储并传递给Actor
        
        Args:
            director_result: Director的输出 {"should_continue": bool, "guidance": str}
            
        Returns:
            bool: 是否继续对话
        """
        if not self.context:
            raise ValueError("请先设置ConversationContext")
        
        # 1. 提取Director结果
        should_continue = director_result.get("should_continue", True)
        guidance = director_result.get("guidance", "")
        
        # 2. 存储指导信息到上下文
        self.context.set_variables(
            latest_director_guidance=guidance,
            director_should_continue=should_continue,
            director_last_evaluation=director_result
        )
        
        # 3. 如果需要继续，将指导传递给Actor（预留扩展接口）
        if should_continue and guidance:
            self._apply_guidance_to_actor(guidance)
        
        # 4. 记录日志
        self._log_director_decision(director_result)
        
        return should_continue
    
    def process_final_evaluation(self, full_history: list) -> int:
        """
        处理最终整体质量评估
        
        Args:
            full_history: 完整对话历史
            
        Returns:
            int: 整体质量分数
        """
        if not self.context:
            raise ValueError("请先设置ConversationContext")
        
        # 获取judger实例
        judger = self.context.get_actor('judger')
        if not judger:
            print("⚠️ [编排器] 未找到Judger实例，跳过最终评估")
            return 50
        
        print(f"🎯 [编排器] 开始最终整体质量评估...")
        
        try:
            overall_score = judger.evaluate_overall_quality(full_history)
            
            # 存储最终评估结果
            self.context.set_variables(
                overall_quality_score=overall_score,
                final_evaluation_completed=True
            )
            
            print(f"📊 [编排器] 最终评估完成，整体质量分数: {overall_score}")
            return overall_score
            
        except Exception as e:
            print(f"!!! [编排器] 最终评估失败: {e}")
            return 50
    
    def get_updated_progress_for_director(self, base_progress: int) -> int:
        """
        获取包含最新Judger评估的进度分数，供Director使用
        
        Args:
            base_progress: 基础进度分数
            
        Returns:
            int: 更新后的进度分数
        """
        latest_increment = self.context.get_variable('latest_progress_increment', 0)
        updated_progress = base_progress + latest_increment
        
        print(f"📈 [编排器] 进度更新: {base_progress} + {latest_increment} = {updated_progress}")
        return updated_progress
    
    def _apply_guidance_to_actor(self, guidance: str):
        """
        将Director的指导应用到Actor（预留扩展接口）
        """
        # 预留接口：未来可以直接调用actor.set_guidance()等方法
        actor = self.context.get_actor('actor')
        if actor and hasattr(actor, 'set_guidance'):
            actor.set_guidance(guidance)
        
        # 当前只存储到上下文中，供Actor的prompt生成时使用
        print(f"🎯 [编排器] 指导已存储到上下文，供Actor使用")
    
    def _log_director_decision(self, director_result: dict):
        """记录Director决策日志"""
        should_continue = director_result.get("should_continue", True)
        guidance = director_result.get("guidance", "")
        
        print(f"🎬 [编排器] Director决策已处理:")
        print(f"    继续对话: {'✅ 是' if should_continue else '❌ 否'}")
        print(f"    指导内容: {guidance}")
        print(f"    已存储到上下文变量中")


def process_director_output(director_result: dict, context: ConversationContext) -> bool:
    """
    便捷函数 - 处理Director输出
    
    Args:
        director_result: Director的输出结果
        context: 对话上下文对象
        
    Returns:
        bool: 是否继续对话
    """
    orchestrator = DirectorOrchestrator()
    orchestrator.set_context(context)
    return orchestrator.process_director_output(director_result)


def process_judger_evaluation(recent_turns: list, current_progress: int, context: ConversationContext) -> dict:
    """
    便捷函数 - 处理Judger评估
    
    Args:
        recent_turns: 最近3轮对话记录
        current_progress: 当前累计进度
        context: 对话上下文对象
        
    Returns:
        dict: 评估结果
    """
    orchestrator = DirectorOrchestrator()
    orchestrator.set_context(context)
    return orchestrator.process_judger_evaluation(recent_turns, current_progress)


def process_final_evaluation(full_history: list, context: ConversationContext) -> int:
    """
    便捷函数 - 处理最终评估
    
    Args:
        full_history: 完整对话历史
        context: 对话上下文对象
        
    Returns:
        int: 整体质量分数
    """
    orchestrator = DirectorOrchestrator()
    orchestrator.set_context(context)
    return orchestrator.process_final_evaluation(full_history)