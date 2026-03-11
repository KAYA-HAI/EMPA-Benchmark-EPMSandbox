"""
EPM-Q (Empathy Physics Model — Quantitative) scoring algorithm.

Computes 9 standardized indices grouped into three dimensions:

- **Outcome Quality**: Idx_RDI, Idx_Etot, Idx_Snet
- **Process Efficiency**: Idx_Rho, Idx_Sproj, Idx_Tau
- **Process Stability**: Idx_Rpos, Idx_Align, Idx_Pen

Final composite: ``EPM_Index = 0.4 * Outcome + 0.2 * Efficiency + 0.4 * Stability``
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Scientific constants
# ---------------------------------------------------------------------------
RHO_MAX = 2.5   # empirical max intensity
ALPHA = 1.5     # net-score conversion factor
BETA = 1.2      # energy conversion factor

# Composite weights
W_OUTCOME = 0.4
W_EFFICIENCY = 0.2
W_STABILITY = 0.4


def calculate_epmq_indices(metrics: Dict[str, Any]) -> Dict[str, float]:
    """Compute per-case EPM-Q standardized indices (9 total).

    Parameters
    ----------
    metrics : dict
        Raw physical quantities extracted by :func:`extract_result_metrics`.

    Returns
    -------
    dict
        Keys ``Idx_RDI``, ``Idx_Etot``, ``Idx_Snet``, ``Idx_Rho``,
        ``Idx_Sproj``, ``Idx_Tau``, ``Idx_Rpos``, ``Idx_Align``, ``Idx_Pen``.
    """
    indices: Dict[str, float] = {}

    r0 = metrics.get("initial_distance", 0)
    if r0 <= 1e-6:
        r0 = 1.0

    # --- Outcome Quality ---
    rdi = metrics.get("distance_improvement_rate", 0)
    indices["Idx_RDI"] = max(0, min(100, (rdi + 100) / 2))

    e_total = metrics.get("E_total", 0)
    indices["Idx_Etot"] = (max(0, e_total) / (BETA * r0)) * 100

    s_net = metrics.get("total_net_score", 0)
    indices["Idx_Snet"] = (max(0, s_net) / (ALPHA * r0)) * 100

    # --- Process Efficiency ---
    rho = metrics.get("energy_per_turn", 0)
    indices["Idx_Rho"] = (max(0, rho) / RHO_MAX) * 100

    s_proj = metrics.get("avg_effective_projection", 0)
    indices["Idx_Sproj"] = (max(0, s_proj) / RHO_MAX) * 100

    tau = metrics.get("tortuosity", 1.0)
    if tau < 1.0:
        tau = 1.0
    indices["Idx_Tau"] = max(0, (3.0 - tau) / 2.0 * 100)

    # --- Process Stability ---
    indices["Idx_Rpos"] = metrics.get("positive_energy_ratio", 0)

    align = metrics.get("avg_alignment", 0)
    indices["Idx_Align"] = (align + 1.0) / 2.0 * 100

    r_pen = metrics.get("performance_penalty_rate", 0)
    indices["Idx_Pen"] = max(0, (3.0 - r_pen) / 3.0 * 100)

    return indices


# ---------------------------------------------------------------------------
# Result metric extraction
# ---------------------------------------------------------------------------

def extract_result_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract raw physical quantities from a single benchmark result JSON.

    Also calls :func:`calculate_epmq_indices` to attach the 9 indices.
    """
    termination_reason = result.get("termination_reason", "N/A")

    victory_data = result.get(
        "epm_victory_analysis",
        result.get("epj", {}).get("epm_victory_analysis"),
    )

    if victory_data:
        conds = victory_data.get("conditions", {})
        spatial = (
            conds.get("geometric", {}).get("achieved", False)
            or conds.get("positional", {}).get("achieved", False)
        )
        energy = conds.get("energetic", {}).get("achieved", False)
        if spatial and energy:
            termination_type = "SUCCESS"
        else:
            termination_type = "FAILURE"
    elif "成功" in termination_reason or "SUCCESS" in termination_reason.upper():
        termination_type = "SUCCESS"
    elif "失败" in termination_reason or "FAILURE" in termination_reason.upper():
        termination_type = "FAILURE"
    elif "MAX_TURNS" in termination_reason.upper() or "超时" in termination_reason:
        termination_type = "MAX_TURNS"
    else:
        termination_type = "UNKNOWN"

    metrics: Dict[str, Any] = {
        "script_id": result.get("script_id", "N/A"),
        "total_turns": result.get("total_turns", 0),
        "termination_type": termination_type,
        "termination_reason": termination_reason,
    }

    epj = result.get("epj", {})
    trajectory = epj.get("trajectory", [])

    if trajectory:
        initial_turn = trajectory[0]
        final_turn = trajectory[-1]

        metrics["initial_distance"] = initial_turn.get("distance", 0)
        metrics["final_distance"] = final_turn.get("distance", 0)
        metrics["E_total"] = final_turn.get("epm", {}).get("E_total", 0)
        metrics["epsilon_energy"] = initial_turn.get("epm", {}).get(
            "P_norm", metrics["initial_distance"]
        )

        metrics["distance_improvement"] = (
            metrics["initial_distance"] - metrics["final_distance"]
        )
        metrics["distance_improvement_rate"] = (
            metrics["distance_improvement"] / metrics["initial_distance"] * 100
            if metrics["initial_distance"] > 0
            else 0
        )

        metrics["energy_surplus"] = metrics["E_total"] - metrics["epsilon_energy"]
        metrics["energy_achievement_rate"] = (
            metrics["E_total"] / metrics["epsilon_energy"] * 100
            if metrics["epsilon_energy"] > 0
            else 0
        )

        turns = metrics["total_turns"]
        metrics["energy_per_turn"] = metrics["E_total"] / turns if turns else 0
        metrics["distance_improvement_per_turn"] = (
            metrics["distance_improvement"] / turns if turns else 0
        )

    # --- MDEP-derived metrics ---
    C_total = A_total = P_total = 0
    C_prog = C_neg = A_prog = A_neg = P_prog = P_neg = 0
    positive_energy_count = 0
    alignments: List[float] = []
    total_neg_abs = 0
    delta_E_list: List[float] = []
    max_negative_streak = current_negative_streak = 0

    for t in trajectory:
        mdep = t.get("mdep_analysis", {})
        c_p = mdep.get("C_Prog_level", 0)
        c_n = mdep.get("C_Neg_level", 0)
        a_p = mdep.get("A_Prog_level", 0)
        a_n = mdep.get("A_Neg_level", 0)
        p_p = mdep.get("P_Prog_level", 0)
        p_n = mdep.get("P_Neg_level", 0)

        C_total += c_p + c_n
        A_total += a_p + a_n
        P_total += p_p + p_n
        C_prog += c_p; C_neg += c_n
        A_prog += a_p; A_neg += a_n
        P_prog += p_p; P_neg += p_n
        total_neg_abs += abs(c_n) + abs(a_n) + abs(p_n)

        epm = t.get("epm", {})
        dE = epm.get("delta_E", 0)
        delta_E_list.append(dE)
        if dE > 0:
            positive_energy_count += 1
            current_negative_streak = 0
        elif dE < 0:
            current_negative_streak += 1
            max_negative_streak = max(max_negative_streak, current_negative_streak)
        else:
            current_negative_streak = 0

        if "alignment" in epm:
            alignments.append(epm["alignment"])

    metrics["C_net_score"] = C_total
    metrics["A_net_score"] = A_total
    metrics["P_net_score"] = P_total
    metrics["total_net_score"] = C_total + A_total + P_total
    metrics["net_score_per_turn"] = (
        metrics["total_net_score"] / metrics["total_turns"]
        if metrics["total_turns"]
        else 0
    )

    metrics["C_Prog_sum"] = C_prog
    metrics["C_Neg_sum"] = C_neg
    metrics["A_Prog_sum"] = A_prog
    metrics["A_Neg_sum"] = A_neg
    metrics["P_Prog_sum"] = P_prog
    metrics["P_Neg_sum"] = P_neg
    prog_sum_total = C_prog + A_prog + P_prog
    metrics["Prog_sum_total"] = prog_sum_total
    metrics["Prog_per_turn"] = (
        prog_sum_total / metrics["total_turns"] if metrics["total_turns"] else 0
    )
    neg_sum_total = C_neg + A_neg + P_neg
    metrics["Neg_sum_total"] = neg_sum_total
    metrics["Neg_per_turn"] = (
        neg_sum_total / metrics["total_turns"] if metrics["total_turns"] else 0
    )

    metrics["positive_energy_ratio"] = (
        positive_energy_count / len(trajectory) * 100 if trajectory else 0
    )
    metrics["avg_alignment"] = (
        sum(alignments) / len(alignments) if alignments else 0
    )
    metrics["avg_effective_projection"] = (
        sum(delta_E_list) / len(delta_E_list) if delta_E_list else 0
    )
    metrics["performance_penalty_rate"] = (
        total_neg_abs / len(trajectory) if trajectory else 0
    )
    metrics["total_neg_abs"] = total_neg_abs

    if delta_E_list:
        mean_de = sum(delta_E_list) / len(delta_E_list)
        metrics["delta_E_var"] = sum(
            (x - mean_de) ** 2 for x in delta_E_list
        ) / len(delta_E_list)
    else:
        metrics["delta_E_var"] = 0.0
    metrics["max_negative_streak"] = max_negative_streak

    # Tortuosity
    path_coords = [t["P_t"] for t in trajectory if "P_t" in t]
    total_path_len = 0.0
    if len(path_coords) > 1:
        for i in range(len(path_coords) - 1):
            d = math.sqrt(
                sum((a - b) ** 2 for a, b in zip(path_coords[i], path_coords[i + 1]))
            )
            total_path_len += d
    metrics["total_path_len"] = total_path_len

    if len(path_coords) > 1:
        displacement = math.sqrt(
            sum(
                (a - b) ** 2
                for a, b in zip(path_coords[0], path_coords[-1])
            )
        )
        if displacement > 1e-6:
            metrics["tortuosity"] = total_path_len / displacement
        elif total_path_len < 1e-6:
            metrics["tortuosity"] = 1.0
        else:
            metrics["tortuosity"] = 0.0
    else:
        metrics["tortuosity"] = 1.0

    # Success flag
    if victory_data:
        conds = victory_data.get("conditions", {})
        spatial = (
            conds.get("geometric", {}).get("achieved", False)
            or conds.get("positional", {}).get("achieved", False)
        )
        energy = conds.get("energetic", {}).get("achieved", False)
        metrics["success"] = spatial and energy
    else:
        metrics["success"] = (
            "判定成功" in termination_reason
            or "成功" in termination_reason
            or termination_type == "SUCCESS"
        )

    # Attach EPM-Q indices
    metrics.update(calculate_epmq_indices(metrics))
    return metrics


# ---------------------------------------------------------------------------
# SP metadata extraction
# ---------------------------------------------------------------------------

def extract_sp_metadata(
    script_id: str, cases_dir: Optional[Path] = None
) -> Dict[str, str]:
    """Parse empathy threshold and priority levels from an actor prompt file."""
    if cases_dir is None:
        cases_dir = Path(__file__).resolve().parent.parent / "data" / "cases"

    sp_file = cases_dir / f"{script_id}.md"
    info: Dict[str, str] = {
        "sp_threshold_level": "N/A",
        "sp_emotional_priority": "N/A",
        "sp_motivational_priority": "N/A",
        "sp_cognitive_priority": "N/A",
    }

    if not sp_file.exists():
        return info

    try:
        text = sp_file.read_text(encoding="utf-8")
    except Exception:
        return info

    m = re.search(r"共情阈值【(.+?)】", text)
    if m:
        level = m.group(1).strip()
        info["sp_threshold_level"] = level[0] if level else level

    def _priority(label: str) -> str:
        m_local = re.search(label + r"：\[优先级：(.+?)\]", text)
        if m_local:
            return m_local.group(1).strip()[:1]
        m_line = re.search(label + r"：([^\n]+)", text)
        if m_line:
            seg = m_line.group(1).strip()
            for kw in ("高", "中", "低"):
                if f"{kw}优先级" in seg or seg.startswith(kw):
                    return kw
        return "N/A"

    emo = _priority("情感共情")
    mot = _priority("动机共情")
    cog = _priority("认知共情")

    if emo == "N/A" and mot == "N/A" and cog == "N/A":
        m_order = re.search(r"当下共情需求优先级[：:]\s*([^\n。]+)", text)
        if m_order:
            parts = [p.strip() for p in re.split(r"[>＞]", m_order.group(1)) if p.strip()]
            rank = {0: "高", 1: "中", 2: "低"}
            for idx, part in enumerate(parts):
                lv = rank.get(idx, "低")
                if "情感共情" in part:
                    emo = lv
                if "动机共情" in part:
                    mot = lv
                if "认知共情" in part:
                    cog = lv

    info["sp_emotional_priority"] = emo if emo != "N/A" else "中"
    info["sp_motivational_priority"] = mot if mot != "N/A" else "中"
    info["sp_cognitive_priority"] = cog if cog != "N/A" else "中"

    return info


# ---------------------------------------------------------------------------
# Aggregate statistics
# ---------------------------------------------------------------------------

def compute_composite_scores(
    case_indices: List[Dict[str, float]],
) -> Dict[str, Any]:
    """Aggregate per-case EPM-Q indices into composite scores.

    Parameters
    ----------
    case_indices : list of dict
        Each dict must contain the 9 ``Idx_*`` keys.

    Returns
    -------
    dict
        Contains ``Outcome_Score``, ``Efficiency_Score``, ``Stability_Score``,
        ``EPM_Index``, and ``Details_*`` sub-dicts.
    """
    n = len(case_indices)
    if n == 0:
        return {}

    def _mean(key: str) -> float:
        return sum(d.get(key, 0) for d in case_indices) / n

    s_rdi = _mean("Idx_RDI")
    s_etot = _mean("Idx_Etot")
    s_snet = _mean("Idx_Snet")
    outcome = (s_rdi + s_etot + s_snet) / 3

    s_rho = _mean("Idx_Rho")
    s_sproj = _mean("Idx_Sproj")
    s_tau = _mean("Idx_Tau")
    efficiency = (s_rho + s_sproj + s_tau) / 3

    s_rpos = _mean("Idx_Rpos")
    s_align = _mean("Idx_Align")
    s_pen = _mean("Idx_Pen")
    stability = (s_rpos + s_align + s_pen) / 3

    epm_index = (
        W_OUTCOME * outcome + W_EFFICIENCY * efficiency + W_STABILITY * stability
    )

    return {
        "Outcome_Score": outcome,
        "Details_Outcome": {"RDI": s_rdi, "Etot": s_etot, "Snet": s_snet},
        "Efficiency_Score": efficiency,
        "Details_Efficiency": {"Rho": s_rho, "Sproj": s_sproj, "Tau": s_tau},
        "Stability_Score": stability,
        "Details_Stability": {"Rpos": s_rpos, "Align": s_align, "Pen": s_pen},
        "EPM_Index": epm_index,
    }
