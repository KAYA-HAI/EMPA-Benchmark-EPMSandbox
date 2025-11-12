# Benchmark/agents/judger.py

from Benchmark.prompts.judger_prompts import (
    generate_progress_prompt, 
    generate_quality_prompt, 
    generate_overall_prompt
)
from Benchmark.llms.api import get_llm_response
import re
import json

class Judger:
    """
    共情评估员（传感器），负责填写心理量表。
    
    EPJ系统中的职责：
    - T=0: 填写初始共情赤字量表 (IEDR)
    - T>0: 每K轮填写MDEP进展量表 (MDEP-PR)
    - 禁止计算分数和做最终决策（由Orchestrator和Director负责）
    """
    def __init__(self, model_name: str = "google/gemini-2.5-pro"):
        self.model_name = model_name

    def evaluate_empathy_progress(self, recent_turns: list, current_progress: int) -> int:
        """
        评估最近3轮的共情进度改善情况
        
        Args:
            recent_turns: 最近3轮对话记录
            current_progress: 当前累计进度分数
            
        Returns:
            int: 进度分数（可为负数）
        """
        prompt = generate_progress_prompt(recent_turns, current_progress)
        
        try:
            print(f"--- [Judger] 正在评估共情进度（模型: {self.model_name}）... ---")
            
            response = get_llm_response(
                messages=[{"role": "user", "content": prompt}],
                model_name=self.model_name
            )
            
            # 提取分数
            progress_score = self._extract_score(response)
            print(f"--- [Judger] 进度评估完成，分数: {progress_score} ---")
            
            return progress_score
            
        except Exception as e:
            print(f"!!! [Judger] 进度评估失败: {e} !!!")
            return 0  # 默认返回0分

    def evaluate_empathy_quality(self, recent_turns: list) -> int:
        """
        评估最近3轮的共情质量
        
        Args:
            recent_turns: 最近3轮对话记录
            
        Returns:
            int: 过程质量分数 (0-100)
        """
        prompt = generate_quality_prompt(recent_turns)
        
        try:
            print(f"--- [Judger] 正在评估共情质量（模型: {self.model_name}）... ---")
            
            response = get_llm_response(
                messages=[{"role": "user", "content": prompt}],
                model_name=self.model_name
            )
            
            # 提取分数
            quality_score = self._extract_score(response, min_score=0, max_score=100)
            print(f"--- [Judger] 质量评估完成，分数: {quality_score} ---")
            
            return quality_score
            
        except Exception as e:
            print(f"!!! [Judger] 质量评估失败: {e} !!!")
            return 50  # 默认返回中等分数

    def evaluate_overall_quality(self, full_history: list) -> int:
        """
        评估整体共情质量
        
        Args:
            full_history: 完整对话历史记录
            
        Returns:
            int: 总质量分数 (0-100)
        """
        prompt = generate_overall_prompt(full_history)
        
        try:
            print(f"--- [Judger] 正在评估整体共情质量（模型: {self.model_name}）... ---")
            
            response = get_llm_response(
                messages=[{"role": "user", "content": prompt}],
                model_name=self.model_name
            )
            
            # 提取分数
            overall_score = self._extract_score(response, min_score=0, max_score=100)
            print(f"--- [Judger] 整体评估完成，分数: {overall_score} ---")
            
            return overall_score
            
        except Exception as e:
            print(f"!!! [Judger] 整体评估失败: {e} !!!")
            return 50  # 默认返回中等分数

    def _extract_score(self, response: str, min_score=None, max_score=None) -> int:
        """
        从LLM响应中提取分数
        """
        try:
            # 查找数字
            numbers = re.findall(r'-?\d+', response)
            if numbers:
                score = int(numbers[-1])  # 取最后一个数字
                
                # 应用范围限制
                if min_score is not None:
                    score = max(score, min_score)
                if max_score is not None:
                    score = min(score, max_score)
                    
                return score
            else:
                raise ValueError("未找到有效分数")
                
        except Exception as e:
            print(f"⚠️ [Judger] 分数提取失败: {e}, 响应: {response}")
            return 0 if min_score is None else min_score
    
    # ═══════════════════════════════════════════════════════════════
    # EPJ 系统 - 量表填写功能
    # ═══════════════════════════════════════════════════════════════
    
    def fill_iedr(self, script_content: dict) -> dict:
        """
        填写初始共情赤字量表 (IEDR) - T=0时调用
        
        这是EPJ系统的第一步：量化剧本的初始共情需求
        
        Args:
            script_content: 剧本内容（包含actor_prompt和scenario）
        
        Returns:
            dict: 填写完成的IEDR量表
            {
                "C.1": 0-3,
                "C.2": 0-3,
                "A.1": 0-3,
                "A.2": 0-3,
                "A.3": 0-3,
                "P.1": 0-3,
                "P.2": 0-3,
                "P.3": 0-3,
                "reasoning": "判断依据"
            }
        """
        from Benchmark.epj.judger_prompts import generate_iedr_prompt
        
        prompt = generate_iedr_prompt(script_content)
        
        try:
            print(f"═══ [Judger/传感器] T=0: 填写 IEDR 量表 ═══")
            
            response = get_llm_response(
                messages=[{"role": "user", "content": prompt}],
                model_name=self.model_name,
                json_mode=True,
                max_tokens=8000  # IEDR：确保有足够空间输出完整JSON（包含详细evidence和reasoning）
            )
            
            # 解析JSON响应
            raw_response = self._parse_rubric_response(response)
            
            # 转换格式：提取level字段
            filled_iedr = self._convert_iedr_format(raw_response)
            
            print(f"✅ [Judger] IEDR 量表填写完成")
            print(f"   C.1={filled_iedr.get('C.1')}, C.2={filled_iedr.get('C.2')}, C.3={filled_iedr.get('C.3')}")
            print(f"   A.1={filled_iedr.get('A.1')}, A.2={filled_iedr.get('A.2')}, A.3={filled_iedr.get('A.3')}")
            print(f"   P.1={filled_iedr.get('P.1')}, P.2={filled_iedr.get('P.2')}, P.3={filled_iedr.get('P.3')}")
            
            return filled_iedr
            
        except Exception as e:
            print(f"!!! [Judger] IEDR 填写失败: {e} !!!")
            # 返回默认值（中等难度）
            return {
                "C.1": 1, "C.2": 1, "C.3": 1,
                "A.1": 1, "A.2": 1, "A.3": 1,
                "P.1": 1, "P.2": 1, "P.3": 1,
                "reasoning": "填写失败，使用默认值"
            }
    
    def fill_mdep_pr(self, recent_turns: list, script_context: dict = None, actor_prompt: str = None, full_history: list = None) -> dict:
        """
        填写MDEP进展量表 (MDEP-PR) - T>0时每K轮调用
        
        这是EPJ系统的核心评估步骤：量化每K轮的共情进展
        
        Args:
            recent_turns: 最近K轮的对话记录（评估范围）
            script_context: 剧本上下文（可选）
            full_history: 完整对话历史（供参考上下文，可选）
        
        Returns:
            dict: 填写完成的MDEP-PR量表
            {
                "C.Prog": 0-2,
                "C.Neg": 0 or -1 or -2,
                "A.Prog": 0-2,
                "A.Neg": 0 or -1 or -2,
                "P.Prog": 0-2,
                "P.Neg": 0 or -1 or -2,
                "reasoning": "判断依据"
            }
        """
        from Benchmark.epj.judger_prompts import generate_mdep_pr_prompt
        
        # 🆕 传递完整历史供Judger参考上下文
        prompt = generate_mdep_pr_prompt(recent_turns, script_context, full_history)
        
        # 🔧 添加重试机制（最多3次）
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 [Judger] 重试第 {attempt} 次...")
                    import time
                    time.sleep(2)  # 短暂延迟后重试
                
                print(f"═══ [Judger/传感器] T>0: 填写 MDEP-PR 量表 ═══")
                print(f"   评估轮次: 最近 {len(recent_turns)} 轮")
                
                response = get_llm_response(
                    messages=[{"role": "user", "content": prompt}],
                    model_name=self.model_name,
                    json_mode=True,
                    max_tokens=6000  # 🔧 问题3修复：增加到6000，确保完整JSON不被截断
                )
                
                # 🔧 检测空响应或错误标记
                if not response or "（错误：API返回空响应" in response:
                    last_error = "API返回空响应"
                    print(f"⚠️ [Judger] 检测到空响应，准备重试...")
                    continue  # 进入下一次重试
                
                # 解析JSON响应
                raw_response = self._parse_rubric_response(response)
                
                # 🔧 问题3修复：转换新格式并显示reasoning
                filled_mdep_pr = self._convert_mdep_format(raw_response)
                
                print(f"✅ [Judger] MDEP-PR 量表填写完成")
                print(f"   C: Prog={filled_mdep_pr.get('C.Prog')}, Neg={filled_mdep_pr.get('C.Neg')}")
                print(f"   A: Prog={filled_mdep_pr.get('A.Prog')}, Neg={filled_mdep_pr.get('A.Neg')}")
                print(f"   P: Prog={filled_mdep_pr.get('P.Prog')}, Neg={filled_mdep_pr.get('P.Neg')}")
                
                # 🔧 问题3修复：显示reasoning（如果有）
                self._print_mdep_reasoning(raw_response)
                
                # 💾 附加详细分析信息（供保存使用）
                filled_mdep_pr['detailed_analysis'] = raw_response
                
                return filled_mdep_pr
                
            except Exception as e:
                last_error = str(e)
                print(f"⚠️ [Judger] 尝试 {attempt + 1}/{max_retries} 失败: {e}")
                if attempt == max_retries - 1:  # 最后一次尝试
                    break
        
        # 所有重试都失败后，返回默认值
        print(f"!!! [Judger] MDEP-PR 填写失败（已重试{max_retries}次）: {last_error} !!!")
        return {
            "C.Prog": 0, "C.Neg": 0,
            "A.Prog": 0, "A.Neg": 0,
            "P.Prog": 0, "P.Neg": 0,
            "reasoning": f"填写失败（重试{max_retries}次后），使用默认值: {last_error}"
        }
    
    def _parse_rubric_response(self, response: str) -> dict:
        """
        解析量表填写响应（提取JSON）
        
        Args:
            response: LLM的响应文本
        
        Returns:
            dict: 解析后的量表数据
        """
        # 🔧 问题3修复：增加详细日志
        if not response or not isinstance(response, str):
            print(f"!!! [Judger] 响应类型错误: {type(response)} !!!")
            raise ValueError(f"响应类型错误: {type(response)}")
        
        # 打印响应的前100个字符用于调试
        print(f"📝 [Judger] 收到响应（前100字符）: {response[:100]}...")
        print(f"📝 [Judger] 响应总长度: {len(response)} 字符")
        
        try:
            # 尝试直接解析
            parsed = json.loads(response.strip())
            print(f"✅ [Judger] JSON解析成功（直接解析）")
            return parsed
        except json.JSONDecodeError as e:
            print(f"⚠️ [Judger] 直接JSON解析失败: {e}")
            
            # 尝试提取代码块中的JSON
            import re
            json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
            json_match = re.search(json_pattern, response, re.DOTALL)
            
            if json_match:
                json_str = json_match.group(1).strip()
                print(f"📝 [Judger] 从代码块提取JSON（长度: {len(json_str)}）")
                try:
                    parsed = json.loads(json_str)
                    print(f"✅ [Judger] JSON解析成功（代码块提取）")
                    return parsed
                except json.JSONDecodeError as e2:
                    print(f"!!! [Judger] 代码块JSON解析失败: {e2} !!!")
                    print(f"!!! [Judger] 提取的JSON: {json_str[:200]}... !!!")
                    raise ValueError(f"无法解析提取的JSON: {e2}")
            else:
                # 🚨 关键：打印完整响应以便调试
                print(f"!!! [Judger] 未找到JSON代码块 !!!")
                print(f"!!! [Judger] 完整响应内容: !!!")
                print(f"{response}")
                print(f"!!! ==================== !!!")
                raise ValueError(f"无法从响应中提取JSON")
    
    def _convert_iedr_format(self, raw_response: dict) -> dict:
        """
        将IEDR的详细响应格式转换为简化格式
        
        输入格式（详细）:
        {
          "C.1_level": 2,
          "C.1_evidence": "...",
          "C.1_reasoning": "...",
          ...
        }
        
        输出格式（简化）:
        {
          "C.1": 2,
          "C.2": 1,
          ...
        }
        """
        indicators = [
            "C.1", "C.2", "C.3",
            "A.1", "A.2", "A.3",
            "P.1", "P.2", "P.3"
        ]
        
        simplified = {}
        for indicator in indicators:
            level_key = f"{indicator}_level"
            if level_key in raw_response:
                simplified[indicator] = raw_response[level_key]
            else:
                # 如果没有_level后缀，尝试直接使用indicator键
                simplified[indicator] = raw_response.get(indicator, 1)
        
        return simplified
    
    def _convert_mdep_format(self, raw_response: dict) -> dict:
        """
        提取level字段用于向量计算
        
        说明：
        - Prompt要求输出完整格式（level + evidence + reasoning），这是为了科学性和可追溯性
        - scoring.py只需要level数字来计算向量 v_t
        - 原始的evidence和reasoning保存在 _raw_response 中，供后续分析使用
        
        新格式（Prompt输出）：
        {
          "C_Prog_level": 2,
          "C_Prog_evidence": "AI说...",
          "C_Prog_reasoning": "因为...",
          ...
        }
        
        计算格式（scoring.py输入）：
        {
          "C.Prog": 2,
          "C.Neg": 0,
          ...
        }
        
        Args:
            raw_response: Judger LLM的原始JSON响应
        
        Returns:
            dict: 提取level后的数据（用于scoring.calculate_increment_vector）
        """
        # 检查是否是新格式（带_level后缀）
        if 'C_Prog_level' in raw_response:
            # 新格式：提取level字段，转换为scoring期望的格式
            scoring_format = {
                "C.Prog": raw_response.get('C_Prog_level', 0),
                "C.Neg": raw_response.get('C_Neg_level', 0),
                "A.Prog": raw_response.get('A_Prog_level', 0),
                "A.Neg": raw_response.get('A_Neg_level', 0),
                "P.Prog": raw_response.get('P_Prog_level', 0),
                "P.Neg": raw_response.get('P_Neg_level', 0),
                "_raw_response": raw_response  # 保存完整响应（包含evidence和reasoning）
            }
            return scoring_format
        else:
            # 兼容旧格式（如果Prompt没有按预期输出）
            return raw_response
    
    def _print_mdep_reasoning(self, raw_response: dict):
        """
        打印MDEP-PR的evidence和reasoning（问题3修复）
        
        Args:
            raw_response: 原始JSON响应
        """
        # 检查是否是新格式
        if 'C_Prog_level' not in raw_response:
            # 旧格式：只显示reasoning字段
            if 'reasoning' in raw_response:
                print(f"\n📝 [Judger推理]: {raw_response['reasoning']}")
            return
        
        # 新格式：显示详细的evidence和reasoning
        print(f"\n📝 [Judger分析详情]:")
        
        dimensions = [
            ('C', '认知'),
            ('A', '情感'),  
            ('P', '动机')
        ]
        
        for dim_code, dim_name in dimensions:
            print(f"\n   【{dim_name}轴】:")
            
            # Prog
            prog_level = raw_response.get(f'{dim_code}_Prog_level', 0)
            prog_evidence = raw_response.get(f'{dim_code}_Prog_evidence', '')
            prog_reasoning = raw_response.get(f'{dim_code}_Prog_reasoning', '')
            
            if prog_level != 0:
                print(f"     进展[{prog_level:+d}]:")
                if prog_evidence:
                    print(f"       证据: {prog_evidence[:60]}...")
                if prog_reasoning:
                    print(f"       理由: {prog_reasoning}")
            else:
                # 🔧 问题2修复：0级别也显示reasoning
                if prog_reasoning:
                    print(f"     进展[0]: {prog_reasoning}")
            
            # Neg
            neg_level = raw_response.get(f'{dim_code}_Neg_level', 0)
            neg_evidence = raw_response.get(f'{dim_code}_Neg_evidence', '')
            neg_reasoning = raw_response.get(f'{dim_code}_Neg_reasoning', '')
            
            if neg_level != 0:
                print(f"     倒退[{neg_level:+d}]:")
                if neg_evidence:
                    print(f"       证据: {neg_evidence[:60]}...")
                if neg_reasoning:
                    print(f"       理由: {neg_reasoning}")
            else:
                # 🔧 问题2修复：0级别也显示reasoning
                if neg_reasoning:
                    print(f"     倒退[0]: {neg_reasoning}")