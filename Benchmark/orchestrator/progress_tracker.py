# Benchmark/orchestrator/progress_tracker.py

class ProgressTracker:
    """
    追踪对话的进度（增量累加制）
    """
    def __init__(self):
        self.turn_count = 0
        self.total_score = 0  # 累计的总分（可以为负）
        self.evaluation_history = []  # 记录每次评估的结果

    def increment_turn(self):
        """增加回合数"""
        self.turn_count += 1

    def update_score(self, score_increment: int):
        """
        更新分数（累加增量）
        
        Args:
            score_increment: 本轮的分数增量（可以为负）
        """
        old_score = self.total_score
        self.total_score += score_increment
        print(f"[ProgressTracker] 分数更新：{old_score} + {score_increment} = {self.total_score}")

    def get_progress(self) -> int:
        """获取当前总分"""
        return self.total_score

    def get_turn_count(self) -> int:
        """获取当前回合数"""
        return self.turn_count
    
    def add_evaluation(self, evaluation: dict):
        """记录评估结果"""
        self.evaluation_history.append(evaluation)
    
    def get_recent_trends(self, n: int = 3) -> list:
        """获取最近N次评估的趋势"""
        recent = self.evaluation_history[-n:]
        return [e.get("emotion_trend", "不变") for e in recent]
    
    def get_last_score_increment(self) -> int:
        """获取最近一次的分数增量"""
        if self.evaluation_history:
            return self.evaluation_history[-1].get("score_increment", 0)
        return 0