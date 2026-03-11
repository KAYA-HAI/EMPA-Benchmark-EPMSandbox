"""
Director agent — controls plot progression and EPJ/EPM-based decisions.

Responsibilities:
1. **Plot control** (:meth:`evaluate_continuation`): decide which story
   fragment to release, how to adjust empathy strategy, whether to
   intervene, or when to end the conversation.
2. **EPJ termination** (:meth:`make_epj_decision`): rule-based check on
   the state packet (zone, timeout, stagnation, energy) that does *not*
   require an LLM call.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from empa.agents.base import BaseAgent
from empa.core.utils import parse_vector_string
from empa.llm.base import LLMClient, LLMResponse, Message

logger = logging.getLogger(__name__)

MIN_TURNS = 12


class Director(BaseAgent):
    """Concrete Director with function-calling–based plot control."""

    def __init__(
        self,
        llm: LLMClient,
        scenario: dict,
        actor_prompt: str = "",
        stages: Optional[List[dict]] = None,
    ) -> None:
        self._llm = llm
        self.scenario = scenario
        self.actor_prompt = actor_prompt
        self.actor_profile = self._parse_actor_prompt(actor_prompt) if actor_prompt else {}

        if stages is not None:
            self.stages = stages
        else:
            self.stages = self._extract_stages(scenario)

        self.revealed_stages: List[int] = []
        self.revealed_memories: List[str] = []
        self.revealed_info: List[dict] = []
        self._current_turn = 0

    # ------------------------------------------------------------------
    # BaseAgent interface (not used directly by the chat loop)
    # ------------------------------------------------------------------

    def generate_reply(self, history: List[Dict[str, str]], **kw: Any) -> str:  # pragma: no cover
        raise NotImplementedError("Director does not produce dialogue replies")

    # ==================================================================
    # Plot control (LLM-driven)
    # ==================================================================

    def evaluate_continuation(
        self,
        history: list,
        *,
        progress: Optional[int] = None,
        epj_state: Optional[dict] = None,
    ) -> dict:
        """Ask the LLM to decide the next plot action via function calling."""
        if epj_state and "current_turn" in epj_state:
            self._current_turn = epj_state["current_turn"]

        from empa.rubric.empathy_v2.director_prompt import generate_director_prompt
        from empa.rubric.empathy_v2.director_functions import get_director_tools

        available_stages = self.stages
        print(f"📚 [Director] 当前有 {len(available_stages)} 个故事阶段")
        print(f"   已释放: {len(self.revealed_stages)} 个")
        print(f"   未释放: {len(available_stages) - len(self.revealed_stages)} 个")
        print(f"   已释放记忆: {len(self.revealed_memories)} 个")

        prompt = generate_director_prompt(
            epj_state=epj_state or {},
            history=history,
            available_stages=self.stages,
            revealed_stages=self.revealed_stages,
            actor_profile=self.actor_profile,
            revealed_memories=self.revealed_memories,
        )

        print(f"--- [Director] 正在评估对话并决策剧情发展... ---")
        tools = get_director_tools()

        try:
            resp = self._llm.complete(
                [Message(role="user", content=prompt)],
                tools=tools,
                max_tokens=4000,
            )
            if resp.tool_calls:
                fn_name = resp.tool_calls[0].name
                fn_args = resp.tool_calls[0].arguments
                print(f"🎬 [Director] LLM调用函数: {fn_name}")
                print(f"   参数: {fn_args}")
                result = self._handle_tool_call(fn_name, fn_args)
            else:
                result = {"should_continue": True, "guidance": None}
            print(f"--- [Director] 决策完成 ---")
            return result
        except Exception as exc:
            logger.error("Director evaluation failed: %s", exc)
            return {"should_continue": True, "guidance": "评估失败，继续对话"}

    # ==================================================================
    # EPJ termination (rule-based, no LLM)
    # ==================================================================

    def make_epj_decision(self, state_packet: dict, history: list) -> dict:
        """Deterministic decision based on the EPJ/EPM state packet."""
        is_in_zone = state_packet.get("is_in_zone", False)
        is_timeout = state_packet.get("is_timeout", False)
        current_turn = state_packet.get("current_turn", 0)
        P_t = state_packet.get("P_t_current_position", "(0,0,0)")
        v_t = state_packet.get("v_t_last_increment", "(0,0,0)")
        distance = state_packet.get("distance_to_goal", 999)

        if is_in_zone:
            if current_turn < MIN_TURNS:
                return {
                    "decision": "CONTINUE",
                    "reason": f"已进入目标区域，但未达最低轮次（{current_turn}/{MIN_TURNS}）",
                }
            epm = state_packet.get("epm_summary", {})
            if epm:
                E = epm.get("metrics", {}).get("E_total", 0)
                eps_E = epm.get("thresholds", {}).get("epsilon_energy", 0)
                if E < eps_E:
                    return {"decision": "CONTINUE", "reason": f"已进入目标区域，但能量不足（{E:.1f}/{eps_E:.1f}）"}
            return {
                "decision": "STOP",
                "reason": "轨迹已到达目标区域且能量充足",
                "termination_type": "SUCCESS",
            }

        if is_timeout:
            return {
                "decision": "STOP",
                "reason": f"超时（{state_packet.get('max_turns')}轮）",
                "termination_type": "TIMEOUT",
            }

        if state_packet.get("is_stagnant"):
            info = state_packet.get("stagnation_info", {})
            return {
                "decision": "STOP",
                "reason": f"停滞: {info.get('reason', '')}",
                "termination_type": "STAGNATION",
            }

        v_t_vec = parse_vector_string(v_t)
        P_t_vec = parse_vector_string(P_t)
        guidance = self._guidance_from_vectors(
            v_t_vec, P_t_vec, distance, state_packet.get("epm_summary")
        )
        return {"decision": "CONTINUE", "reason": f"距离目标还有 {distance:.2f}，继续对话", "guidance": guidance}

    # ==================================================================
    # Tool call dispatch
    # ==================================================================

    def _handle_tool_call(self, fn: str, args: dict) -> dict:
        self.revealed_info.append({"function": fn, "args": args})
        dispatch = {
            "select_and_reveal_fragment": self._handle_reveal_fragment,
            "observe_and_wait": self._handle_observe,
            "continue_without_new_info": self._handle_continue,
            "reveal_memory": self._handle_memory,
            "adjust_empathy_strategy": self._handle_strategy,
            "introduce_turning_point": self._handle_turning_point,
            "end_conversation": self._handle_end,
        }
        handler = dispatch.get(fn)
        if handler:
            return handler(args)
        logger.warning("Unknown Director function: %s", fn)
        return {"should_continue": True, "guidance": None}

    def _handle_reveal_fragment(self, args: dict) -> dict:
        idx = args.get("stage_index", 0)
        if idx >= len(self.stages):
            return {"should_continue": True, "guidance": "继续当前的表达"}
        if idx in self.revealed_stages:
            logger.info("Stage %d already revealed, skipping", idx)
        else:
            self.revealed_stages.append(idx)

        stage = self.stages[idx]
        guidance = (
            f"【{stage['阶段名']}：{stage['标题']}】\n剧情内容：\n{stage['内容']}\n"
        )
        if args.get("actor_guidance"):
            guidance += f"\n【策略指导】\n{args['actor_guidance']}\n"
        else:
            guidance += "\n【表演指导】\n请自然地将上述内容融入对话中。\n"
        return {"should_continue": True, "guidance": guidance, "plot_action": f"reveal_stage_{idx}"}

    def _handle_observe(self, args: dict) -> dict:
        observation = args.get("observation", "")
        wait_reason = args.get("wait_reason", "")
        print(f"👁️  [Director] 选择暂不介入，继续观察")
        print(f"   观察: {observation}")
        print(f"   等待理由: {wait_reason}")
        return {"should_continue": True, "guidance": None, "no_intervention": True}

    def _handle_continue(self, args: dict) -> dict:
        return {
            "should_continue": True,
            "guidance": f"【维持当前状态】\n聚焦: {args.get('focus_suggestion', '')}",
        }

    def _handle_memory(self, args: dict) -> dict:
        period = args.get("memory_period", "")
        if period in self.revealed_memories:
            return {"should_continue": True, "guidance": "继续深化当前话题，从新的角度展开"}
        self.revealed_memories.append(period)
        print(f"📝 [Director] 记录已释放记忆：{period}")

        experience = self.actor_profile.get("experience", "")
        guidance = (
            f"【记忆片段释放】\n从你的 <experience> 中，现在可以提到关于【{period}】的经历。\n"
            f"参考信息：\n{experience}\n\n"
            "表演指导：自然地提到这段经历，作为对当前话题的呼应。"
        )
        return {"should_continue": True, "guidance": guidance, "plot_action": "reveal_memory"}

    def _handle_strategy(self, args: dict) -> dict:
        ag = args.get("actor_guidance", "")
        if not ag:
            ag = self._default_strategy(args.get("focus_aspect", ""))
        return {
            "should_continue": True,
            "guidance": f"【表演策略调整】\n聚焦方向：{args.get('focus_aspect')}\n{ag}",
            "plot_action": "adjust_strategy",
        }

    def _handle_turning_point(self, args: dict) -> dict:
        parts: list[str] = []
        idx = args.get("stage_index", -1)
        if 0 <= idx < len(self.stages) and idx not in self.revealed_stages:
            s = self.stages[idx]
            parts.append(f"【剧情内容：{s['阶段名']} - {s['标题']}】\n{s['内容']}")
            self.revealed_stages.append(idx)
        if args.get("actor_guidance"):
            parts.append(f"【策略指导】\n{args['actor_guidance']}")
        elif args.get("empathy_aspect"):
            parts.append(f"【共情策略：聚焦{args['empathy_aspect']}】\n{self._default_strategy(args['empathy_aspect'])}")
        return {
            "should_continue": True,
            "guidance": "【综合转折点】\n" + "\n".join(parts),
            "plot_action": "turning_point",
        }

    def _handle_end(self, args: dict) -> dict:
        if self._current_turn < MIN_TURNS:
            logger.info("Director wants to end but below MIN_TURNS (%d/%d)", self._current_turn, MIN_TURNS)
            return {"should_continue": True, "guidance": None, "plot_action": "wait_min_turns"}
        return {
            "should_continue": False,
            "guidance": args.get("reason", "对话自然结束"),
            "plot_action": "end",
        }

    # ==================================================================
    # Helpers
    # ==================================================================

    @staticmethod
    def _parse_actor_prompt(prompt: str) -> dict:
        sections = {
            "character_info": r"<character_info>(.*?)</character_info>",
            "empathy_threshold": r"<empathy_threshold>(.*?)</empathy_threshold>",
            "psychological_profile": r"<psychological_profile>(.*?)</psychological_profile>",
            "experience": r"<experience>(.*?)</experience>",
            "scenario": r"<scenario>(.*?)</scenario>",
        }
        profile: dict[str, str] = {}
        for key, pat in sections.items():
            m = re.search(pat, prompt, re.DOTALL)
            if m:
                profile[key] = m.group(1).strip()
        return profile

    @staticmethod
    def _extract_stages(scenario: dict) -> List[dict]:
        """Pull story stages from a scenario dict.

        Supports two layouts:
        1. ``scenario["故事的经过"]["阶段1"]`` (production format)
        2. ``scenario["故事阶段1"]`` (flat format)
        """
        stages: List[dict] = []

        story_progress = scenario.get("故事的经过", {})
        if isinstance(story_progress, dict) and story_progress:
            stage_keys = sorted(
                story_progress.keys(),
                key=lambda x: int(x.replace("阶段", "")) if x.replace("阶段", "").isdigit() else 999,
            )
            for key in stage_keys:
                val = story_progress[key]
                if isinstance(val, dict):
                    stages.append({
                        "阶段名": f"故事阶段{key.replace('阶段', '')}",
                        "标题": val.get("标题", ""),
                        "内容": val.get("内容", ""),
                    })
                elif isinstance(val, str):
                    stages.append({"阶段名": f"故事阶段{key.replace('阶段', '')}", "标题": "", "内容": val})
            if stages:
                return stages

        for key in sorted(scenario.keys()):
            if key.startswith("故事阶段"):
                val = scenario[key]
                if isinstance(val, dict):
                    stages.append({
                        "阶段名": key,
                        "标题": val.get("标题", ""),
                        "内容": val.get("内容", ""),
                    })
                elif isinstance(val, str):
                    stages.append({"阶段名": key, "标题": "", "内容": val})
        return stages

    @staticmethod
    def _default_strategy(aspect: str) -> str:
        if "情感" in aspect:
            return "强化情绪表达：明确说出核心情绪（愤怒、委屈），加强强度。"
        if "动机" in aspect:
            return "强调付出和动机：说出你为这件事做了什么，直接要求被认可和支持。"
        if "认知" in aspect:
            return "表达困惑和思考：提出你不理解的问题，寻求对方帮你分析。"
        return "根据当前情况调整表达方式。"

    def _guidance_from_vectors(
        self,
        v_t: Tuple[int, int, int],
        P_t: Tuple[int, int, int],
        distance: float,
        epm_summary: Optional[dict] = None,
    ) -> str:
        c_v, a_v, p_v = v_t
        c_p, a_p, p_p = P_t

        lines = [f"【EPM综合分析与指导】"]
        lines.append(f"当前位置 P_t=({c_p},{a_p},{p_p})，距离={distance:.2f}")
        lines.append(f"本轮增量 v_t=({c_v},{a_v},{p_v})")

        if epm_summary:
            m = epm_summary.get("metrics", {})
            t = epm_summary.get("thresholds", {})
            lines.append(f"能量 E={m.get('E_total', 0):.1f}/{t.get('epsilon_energy', 0):.1f}")

        deepest = min([("C", c_p), ("A", a_p), ("P", p_p)], key=lambda x: x[1])
        if deepest[1] < -10:
            dim_map = {"C": "认知共情", "A": "情感共情", "P": "动机共情"}
            lines.append(f"聚焦 {dim_map.get(deepest[0], deepest[0])}（赤字最深: {deepest[1]}）")

        return "\n".join(lines)
