"""
Main dialogue loop for the EMPA benchmark.

Orchestrates the interaction between Actor, TestModel, Judger (via
:class:`EPJOrchestrator`), and Director over multiple turns.  Returns a
structured result dict that can be persisted as JSON for analysis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from empa.agents.actor import Actor
from empa.agents.director import Director
from empa.agents.base import BaseAgent, BaseJudger
from empa.core.display import calculate_display_progress
from empa.data.loader import load_config, load_precomputed_iedr
from empa.orchestrator.epj_orchestrator import EPJOrchestrator
from empa.rubric.base import RubricConfig

logger = logging.getLogger(__name__)

MIN_TURNS = 12


def run_chat_loop(
    actor: Actor,
    director: Director,
    judger: BaseJudger,
    test_model: BaseAgent,
    rubric: RubricConfig,
    script_id: str,
    *,
    max_turns: int = 45,
    K: int = 1,
    test_model_name: str = "unknown",
) -> Dict[str, Any]:
    """Execute a full EMPA benchmark dialogue and return the result."""

    print()
    print("=" * 70)
    print(f"🎬 开始测试: {script_id}")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Load case data
    # ------------------------------------------------------------------
    print()
    print("📚 加载剧本配置...")
    config = load_config(script_id)
    actor_prompt = config["actor_prompt"]
    scenario = config["scenario"]

    from empa.rubric.empathy_v2.mdep_prompt import extract_judger_context
    judger_context = extract_judger_context(actor_prompt)

    script_content = {
        "actor_prompt": actor_prompt,
        "judger_context": judger_context,
        "scenario": scenario,
    }
    print(f"✅ 已加载 Actor Prompt {script_id} ({len(actor_prompt)} 字符)")
    print(f"✅ Judger Context: {len(judger_context)} 字符 (压缩率: {len(judger_context)/len(actor_prompt)*100:.1f}%)")
    print(f"✅ 剧本加载成功")

    # ------------------------------------------------------------------
    # 2. EPJ initialisation (T=0)
    # ------------------------------------------------------------------
    print()
    print("🎬 阶段2: EPJ初始化 (T=0)")
    epj = EPJOrchestrator(judger, rubric, K=K, max_turns=max_turns)
    print(f"✅ [EPJOrchestrator] 初始化完成")
    print(f"   评估周期 K = {K}")
    print(f"   最大轮次 = {max_turns}")
    print(f"   🆕 EPM v2.0 {'已启用' if epj.enable_epm else '已禁用'}")

    precomputed = load_precomputed_iedr(script_id)
    if precomputed and precomputed["status"] == "success":
        P_0_dict = precomputed["P_0"]
        P_0 = (P_0_dict["C"], P_0_dict["A"], P_0_dict["P"])
        filled_iedr = precomputed["iedr"]
        epm_pre = precomputed.get("epm")
        if epm_pre:
            filled_iedr["epm"] = epm_pre

        print()
        print("=" * 70)
        print("EPJ 初始化 (T=0) - 使用预先计算的IEDR")
        print("=" * 70)

        if epm_pre:
            print()
            print("🆕 [EPM v2.0] 使用预计算参数")
            print(f"   ||P_0|| = {epm_pre.get('P_0_norm', 'N/A')}")
            v_star = epm_pre.get("v_star_0")
            if v_star:
                print(f"   v*_0（理想方向）= ({v_star[0]:.3f}, {v_star[1]:.3f}, {v_star[2]:.3f})")
            print(f"   ε_distance（距离阈值）= {epm_pre.get('epsilon_distance', 'N/A')}")
            print(f"   ε_direction（方向阈值）= {epm_pre.get('epsilon_direction', 'N/A')}")
            print(f"   ε_energy（能量阈值）= {epm_pre.get('epsilon_energy', 'N/A')}")

        init = epj.initialize_with_precomputed_iedr(filled_iedr, P_0, epm_precomputed=epm_pre)

        print()
        print(f"✅ [EPJOrchestrator] T=0 初始化完成（使用预计算IEDR）")
        print(f"   P_0 = {P_0}")
        print(f"   初始赤字距离 = {init['initial_distance']:.2f}")
        print(f"   📝 跳过Judger调用，节省API消耗")
    else:
        print(f"⚠️  无预计算IEDR，将实时计算...")
        init = epj.initialize_at_T0(script_content)
        P_0 = init["P_0"]
        print(f"✅ P_0 = {P_0}, 距离 = {init['initial_distance']:.2f}")

    # ------------------------------------------------------------------
    # 3. Prepare agents
    # ------------------------------------------------------------------
    print()
    print("🎬 阶段3: 初始化 Actor 和 Director")
    actor.set_system_prompt(actor_prompt)
    print(f"✅ [Actor] System Prompt已设置（{len(actor_prompt)} 字符）")

    print(f"✅ Director 持有 scenario（{len(director.stages)} 个阶段）")

    # ------------------------------------------------------------------
    # 4. Dialogue loop
    # ------------------------------------------------------------------
    print()
    print("=" * 70)
    print("🎬 开始对话循环")
    print("=" * 70)

    history: list[dict] = []
    turn = 0
    should_continue = True
    termination_reason: Optional[str] = None
    termination_type = "MAX_TURNS"
    recent_buf: list[dict] = []
    pending_guidance: Optional[str] = None
    latest_state_packet: Optional[dict] = None
    epm_victory_analysis: Optional[dict] = None

    while should_continue and turn < max_turns:
        turn += 1
        print()
        print("=" * 60)
        print(f"🔄 第 {turn}/{max_turns} 轮")
        print("=" * 60)

        # 4a. Actor speaks
        if turn == 1:
            actor_msg = actor.generate_reply([], director_guidance=None)
        else:
            actor_msg = actor.generate_reply(history, director_guidance=pending_guidance)
        history.append({"role": "actor", "content": actor_msg})
        print(f"💬 Actor: {actor_msg}")

        # 4b. TestModel replies
        print(f"🤖 [TestModel] 正在调用 API: {test_model_name}")
        tm_msg = test_model.generate_reply(history)
        history.append({"role": "test_model", "content": tm_msg})
        print(f"✅ [TestModel] API 调用成功，响应长度: {len(tm_msg)} 字符")
        print(f"🤖 TestModel: {tm_msg}")

        recent_buf.append({"turn": turn, "actor": actor_msg, "test_model": tm_msg})
        if len(recent_buf) > K:
            recent_buf.pop(0)

        # ---------------------------------------------------------------
        # 4c. EPJ evaluation every K turns
        # ---------------------------------------------------------------
        if epj.should_evaluate(turn):
            print()
            _print_epj_eval_header(turn)

            state_packet = epj.evaluate_at_turn_K(
                recent_turns=recent_buf,
                current_turn=turn,
                script_content=script_content,
                full_history=history,
            )
            latest_state_packet = state_packet

            # Print Judger results
            filled = state_packet.get("filled_mdep_pr", {})
            _print_judger_results(filled)

            # Print vector update
            _print_vector_update(epj, turn)

            epm_summary = state_packet.get("epm_summary")

            # EPM success
            if epm_summary and epm_summary.get("success"):
                _print_epm_victory(epm_summary, turn)
                if turn >= MIN_TURNS:
                    should_continue = False
                    termination_reason = f"EPM success: {epm_summary.get('victory_type', 'unknown')}"
                    termination_type = f"EPM_SUCCESS_{epm_summary['victory_type'].upper()}"
                    epm_victory_analysis = _build_victory_analysis(epm_summary, turn, epj)
                    break
                else:
                    print(f"⚠️  EPM胜利条件达成但未满足最小轮次 ({turn} < {MIN_TURNS})")

            # EPM failure
            if epm_summary and epm_summary.get("failure_detected"):
                reasons = epm_summary.get("failure_reasons", {})
                active = [k for k, v in reasons.items() if v]
                print(f"❌ EPM 失败检测: {', '.join(active)}")
                should_continue = False
                termination_reason = "EPM failure: " + ", ".join(active)
                termination_type = "EPM_FAILURE"
                break

            # Director EPJ decision
            _print_director_epj_decision_header(state_packet, epm_summary)
            epj_dec = director.make_epj_decision(state_packet, history)

            print(f"\n📋 EPJ决策结果:")
            print(f"   决策: {epj_dec['decision']}")
            print(f"   理由: {epj_dec['reason']}")

            if epj_dec["decision"] == "STOP":
                should_continue = False
                termination_reason = epj_dec["reason"]
                termination_type = epj_dec.get("termination_type", "UNKNOWN")
                break

            if epj_dec.get("guidance"):
                print(f"\n💡 EPJ提供指导: {epj_dec['guidance'][:200]}...")
                history[-1]["epj_guidance"] = epj_dec["guidance"]

        # ---------------------------------------------------------------
        # 4d. Director plot control (every turn)
        # ---------------------------------------------------------------
        epj_state = _build_epj_state(epj, turn, latest_state_packet)
        if latest_state_packet:
            _P = latest_state_packet.get("P_t_current_position", "?")
            _disp = calculate_display_progress(
                epj.get_current_position(), epj.get_initial_deficit()
            )
            print(f"   📊 EPJ状态：P_t={_P}, 显示进度={_disp:.0f}%（仅供参考）")
        dir_result = director.evaluate_continuation(history=history, epj_state=epj_state)

        if dir_result.get("should_continue") is False:
            should_continue = False
            termination_reason = dir_result.get("guidance", "Director ended conversation")
            termination_type = "DIRECTOR_END"
            print(f"\n🛑 Director 结束对话: {termination_reason[:100]}")
            break

        if dir_result.get("guidance") and not dir_result.get("no_intervention"):
            pending_guidance = dir_result["guidance"]
            history[-1]["director_guidance"] = dir_result["guidance"]
            print(f"\n🎬 Director 介入剧情控制")
            print(f"💡 Director剧情指导: {dir_result['guidance'][:200]}...")
        else:
            pending_guidance = None
            print(f"👁️  Director 观察中（未介入）")

    # ------------------------------------------------------------------
    # 5. Compile result
    # ------------------------------------------------------------------
    if termination_reason is None:
        termination_reason = f"Reached max turns ({max_turns})"

    final_P = epj.get_current_position()
    trajectory = epj.get_trajectory()

    print()
    print("=" * 70)
    print(f"🏁 对话结束: {script_id}")
    print("=" * 70)
    print(f"   总轮次: {turn}")
    print(f"   终止类型: {termination_type}")
    print(f"   终止原因: {termination_reason}")
    print(f"   P_0 = {epj.get_initial_deficit()}")
    print(f"   P_final = {final_P}")
    if trajectory:
        print(f"   最终距离: {trajectory[-1].get('distance', 'N/A')}")
    print("=" * 70)

    result: Dict[str, Any] = {
        "total_turns": turn,
        "termination_reason": termination_reason,
        "termination_type": termination_type,
        "script_id": script_id,
        "scenario": _translate_scenario_keys(scenario),
        "history": history,
        "test_model_name": test_model_name,
        "epj": {
            "P_0_initial_deficit": epj.get_initial_deficit(),
            "P_final_position": final_P,
            "trajectory": trajectory,
            "total_evaluations": max(0, len(trajectory) - 1),
            "K": K,
            "epsilon": epj.engine.epsilon,
            "iedr_details": epj.iedr_result,
            "epm_enabled": epj.enable_epm,
            "epm_victory_analysis": epm_victory_analysis,
        },
    }
    return result


# ------------------------------------------------------------------
# Structured output helpers
# ------------------------------------------------------------------


def _print_epj_eval_header(turn: int) -> None:
    print("🔬" * 20)
    print(f"🔬 EPJ 评估时刻（第{turn}轮）")
    print("🔬" * 20)
    print()
    print("=" * 70)
    print(f"EPJ 评估 (T={turn})")
    print("=" * 70)


def _print_judger_results(filled: dict) -> None:
    c_prog = filled.get("C.Prog", 0)
    c_neg = filled.get("C.Neg", 0)
    a_prog = filled.get("A.Prog", 0)
    a_neg = filled.get("A.Neg", 0)
    p_prog = filled.get("P.Prog", 0)
    p_neg = filled.get("P.Neg", 0)

    print(f"✅ [Judger] MDEP-PR 量表填写完成")
    print(f"   C: Prog={c_prog:+d}, Neg={c_neg}")
    print(f"   A: Prog={a_prog:+d}, Neg={a_neg}")
    print(f"   P: Prog={p_prog:+d}, Neg={p_neg}")

    raw = filled.get("detailed_analysis", {})
    if raw and raw.get("C_Prog_reasoning"):
        print()
        print("📝 [Judger分析详情]:")
        for axis, label in [("C", "认知轴"), ("A", "情感轴"), ("P", "动机轴")]:
            print(f"\n   【{label}】:")
            prog_l = raw.get(f"{axis}_Prog_level", 0)
            prog_e = raw.get(f"{axis}_Prog_evidence", "")
            prog_r = raw.get(f"{axis}_Prog_reasoning", "")
            neg_l = raw.get(f"{axis}_Neg_level", 0)
            neg_e = raw.get(f"{axis}_Neg_evidence", "")
            neg_r = raw.get(f"{axis}_Neg_reasoning", "")
            print(f"     进展[{prog_l:+d}]:")
            if prog_e and str(prog_e) != "0":
                print(f"       证据: {str(prog_e)[:150]}...")
            print(f"       理由: {str(prog_r)}")
            print(f"     倒退[{neg_l}]: {str(neg_r)}")


def _print_vector_update(epj: EPJOrchestrator, turn: int) -> None:
    traj = epj.get_trajectory()
    if not traj:
        return
    latest = traj[-1]
    P_t = epj.get_current_position()
    v_t = latest.get("v_t", (0, 0, 0))
    distance = latest.get("distance", 0)

    print(f"\n═══ [VectorCalculator] T={turn}: 计算 v_t 并更新 P_t ═══")

    epm = latest.get("epm")
    if epm:
        alignment = epm.get("alignment", 0)
        if alignment > 0:
            dir_label = "正向"
        elif alignment < -0.1:
            dir_label = "反向"
        else:
            dir_label = "中性"

        print()
        print("🆕 [EPM v2.0] 能量动力学分析")
        print(f"   移动模长 ||v_t|| = {epm.get('v_t_norm', 0):.2f}")
        print(f"   对齐度 cos(θ) = {alignment:.3f} ({dir_label})")
        print(f"   有效能量增量 ΔE = {epm.get('delta_E', 0):+.2f}")
        print(f"   累计能量 E_total = {epm.get('E_total', 0):.2f} / {epj.engine.epsilon_energy or 0:.2f} ({epm.get('E_total', 0) / (epj.engine.epsilon_energy or 1) * 100:.1f}%)")
        print(f"   当前距离 ||P_t|| = {epm.get('P_norm', 0):.2f}")
        print(f"   位置投影 P_t·v*_0 = {epm.get('projection', 0):.2f}")

    print()
    print(f"✅ [VectorCalculator] 计算完成")
    print(f"   v_t = {v_t}")
    print(f"   P_t = {P_t}")
    print(f"   距离（欧氏）= {distance:.2f}")

    display_progress = calculate_display_progress(P_t, epj.get_initial_deficit())
    in_zone = latest.get("in_zone", False)

    is_stagnant = latest.get("is_stagnant", False)
    stag_label = "True（停滞警告）" if is_stagnant else "False（进展正常）"

    print(f"📦 [VectorCalculator] 状态数据包生成完成")
    print(f"   P_t = {P_t}")
    print(f"   距离目标 = {distance:.2f}（欧氏距离）")
    print(f"   等效进度 = {display_progress:.1f}%（仅供显示）")
    print(f"   在区域内 = {in_zone}（科学决策标准）")
    print(f"   超时 = False")
    print(f"   ✅ 停滞检测 = {stag_label}")


def _print_director_epj_decision_header(state_packet: dict, epm_summary: Optional[dict]) -> None:
    print(f"\n═══ [Director/决策者] EPJ决策分析 ═══")
    print(f"📊 状态数据包分析:")
    print(f"   当前轮次: {state_packet.get('current_turn')}")
    print(f"   当前位置: {state_packet.get('P_t_current_position')}")
    print(f"   本轮增量: {state_packet.get('v_t_last_increment')}")
    print(f"   距离目标: {state_packet.get('distance_to_goal', 0):.2f}")
    print(f"   在区域内: {state_packet.get('is_in_zone', False)}")
    print(f"   超时: {state_packet.get('is_timeout', False)}")

    if epm_summary:
        m = epm_summary.get("metrics", {})
        t = epm_summary.get("thresholds", {})
        print(f"\n📊 EPM v2.0 能量动力学:")
        print(f"   距离原点: {m.get('r_t', 0):.2f} / {t.get('epsilon_distance', 0):.2f}")
        print(f"   位置投影: {m.get('projection', 0):.2f} / {-t.get('epsilon_direction', 0):.2f}")
        print(f"   累计能量: {m.get('E_total', 0):.2f} / {t.get('epsilon_energy', 0):.2f}")


def _print_epm_victory(epm_summary: dict, turn: int) -> None:
    m = epm_summary["metrics"]
    t = epm_summary["thresholds"]
    print()
    print("🎉" * 20)
    print(f"🏆 EPM 胜利! (第{turn}轮)")
    print(f"   胜利类型: {epm_summary['victory_type']}")
    print(f"   距离: {m['r_t']:.2f} ≤ {t['epsilon_distance']:.2f} {'✅' if m['r_t'] <= t['epsilon_distance'] else '❌'}")
    print(f"   投影: {m['projection']:.2f} ≥ {-t['epsilon_direction']:.2f} {'✅' if m['projection'] >= -t['epsilon_direction'] else '❌'}")
    print(f"   能量: {m['E_total']:.2f} ≥ {t['epsilon_energy']:.2f} {'✅' if m['E_total'] >= t['epsilon_energy'] else '❌'}")
    print("🎉" * 20)


# ------------------------------------------------------------------
# State helpers
# ------------------------------------------------------------------


def _build_epj_state(
    epj: EPJOrchestrator,
    turn: int,
    latest_packet: Optional[dict],
) -> Optional[dict]:
    if not epj.initialized:
        return None
    traj = epj.get_trajectory()
    if not traj:
        return None
    latest = traj[-1]
    P_0 = epj.get_initial_deficit()
    P_t = epj.get_current_position()
    disp = calculate_display_progress(P_t, P_0)
    return {
        "current_turn": turn,
        "P_0_start_deficit": P_0,
        "P_t_current_position": P_t,
        "v_t_last_increment": latest.get("v_t", (0, 0, 0)),
        "distance_to_goal": latest.get("distance", 0),
        "display_progress": disp,
        "trajectory": traj,
        "epm_summary": latest_packet.get("epm_summary") if latest_packet else None,
    }


def _build_victory_analysis(
    epm_summary: dict,
    turn: int,
    epj: EPJOrchestrator,
) -> dict:
    m = epm_summary["metrics"]
    t = epm_summary["thresholds"]
    geo = m["r_t"] <= t["epsilon_distance"]
    pos = m["projection"] >= -t["epsilon_direction"]
    ene = m["E_total"] >= t["epsilon_energy"]
    return {
        "primary_victory_type": epm_summary["victory_type"],
        "conditions": {
            "geometric": {"achieved": geo, "value": m["r_t"], "threshold": t["epsilon_distance"]},
            "positional": {"achieved": pos, "value": m["projection"], "threshold": -t["epsilon_direction"]},
            "energetic": {"achieved": ene, "value": m["E_total"], "threshold": t["epsilon_energy"]},
        },
        "achieved_conditions": [k for k, v in {"geometric": geo, "positional": pos, "energetic": ene}.items() if v],
        "turn_at_victory": turn,
        "initial_deficit": epj.get_initial_deficit(),
        "final_position": epj.get_current_position(),
    }


_SCENARIO_KEY_MAP = {
    "剧本编号": "script_id",
    "故事的经过": "story_progression",
    "故事的结果": "story_outcome",
    "故事的插曲": "story_interlude",
}
_STAGE_KEY_MAP = {"标题": "title", "内容": "content"}


def _translate_scenario_keys(scenario: dict) -> dict:
    """Translate Chinese scenario keys to English for result output.

    Only renames structural keys; content values stay unchanged.
    """
    out: Dict[str, Any] = {}
    for k, v in scenario.items():
        new_key = _SCENARIO_KEY_MAP.get(k, k)
        if k == "故事的经过" and isinstance(v, dict):
            prog = {}
            for sk, sv in v.items():
                new_sk = sk.replace("阶段", "phase_")
                if isinstance(sv, dict):
                    prog[new_sk] = {_STAGE_KEY_MAP.get(ik, ik): iv for ik, iv in sv.items()}
                else:
                    prog[new_sk] = sv
            out[new_key] = prog
        else:
            out[new_key] = v
    return out
