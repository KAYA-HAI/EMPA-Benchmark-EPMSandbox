"""
EPM v2.0 energy dynamics: success/failure detection and termination logic.

This module implements the three victory conditions (geometric, positional,
energetic) and three failure detectors (directional collapse, stagnation,
persistent regression).  All checks are parameterised and dimension-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from empa.rubric.base import TerminationParams


@dataclass(frozen=True)
class EPMStatus:
    """Result of an EPM state evaluation."""

    turn: int
    success: bool
    victory_type: str | None
    failure_detected: bool
    failure_reasons: Dict[str, bool]
    metrics: Dict[str, float]
    thresholds: Dict[str, float]
    min_turns_met: bool


def check_success(
    r_t: float,
    projection: float,
    E_total: float,
    epsilon_distance: float,
    epsilon_direction: float,
    epsilon_energy: float,
    current_turn: int,
    min_turns: int,
) -> Tuple[bool, str | None]:
    """
    Three-way victory condition: (geometric OR positional) AND energetic.

    Returns (is_success, victory_type).
    """
    if current_turn < min_turns:
        return False, None

    geometric = r_t <= epsilon_distance
    positional = projection >= -epsilon_direction
    energetic = E_total >= epsilon_energy

    if (geometric or positional) and energetic:
        return True, "geometric" if geometric else "positional"
    return False, None


def check_directional_collapse(
    trajectory: List[Dict],
    params: TerminationParams,
) -> bool:
    """Detect N consecutive negative-energy steps."""
    current_turn = len(trajectory) - 1
    if current_turn < params.min_turns:
        return False

    w = params.collapse_window
    if len(trajectory) < w + 1:
        return False

    deltas = []
    for pt in trajectory[-w:]:
        epm = pt.get("epm", {})
        if "delta_E" in epm:
            deltas.append(epm["delta_E"])

    return len(deltas) == w and all(d < 0 for d in deltas)


def check_stagnation(
    trajectory: List[Dict],
    params: TerminationParams,
) -> bool:
    """Detect position stagnation (low variance in ||P_t||)."""
    current_turn = len(trajectory) - 1
    if current_turn < params.min_turns:
        return False

    w = params.stagnation_window
    if len(trajectory) < w + 1:
        return False

    norms = []
    for pt in trajectory[-w:]:
        epm = pt.get("epm", {})
        if "P_norm" in epm:
            norms.append(epm["P_norm"])

    if len(norms) < w:
        return False

    import statistics

    try:
        return statistics.stdev(norms) < params.stagnation_threshold
    except statistics.StatisticsError:
        return False


def check_persistent_regression(
    trajectory: List[Dict],
    params: TerminationParams,
) -> bool:
    """Detect sustained negative energy over a longer window."""
    current_turn = len(trajectory) - 1
    if current_turn < params.min_turns:
        return False

    w = params.regression_window
    if len(trajectory) < w + 1:
        return False

    deltas = []
    for pt in trajectory[-w:]:
        epm = pt.get("epm", {})
        if "delta_E" in epm:
            deltas.append(epm["delta_E"])

    if len(deltas) < w:
        return False

    neg_count = sum(1 for d in deltas if d < 0)
    if neg_count > w * params.regression_ratio and sum(deltas) < -1.0:
        return True
    return False


def evaluate_epm_state(
    current_turn: int,
    r_t: float,
    projection: float,
    E_total: float,
    epsilon_distance: float,
    epsilon_direction: float,
    epsilon_energy: float,
    trajectory: List[Dict],
    params: TerminationParams,
) -> EPMStatus:
    """
    Full EPM state evaluation: check success conditions and failure detectors.

    Returns an ``EPMStatus`` with all metrics, verdicts, and thresholds.
    """
    success, victory_type = check_success(
        r_t, projection, E_total,
        epsilon_distance, epsilon_direction, epsilon_energy,
        current_turn, params.min_turns,
    )

    collapsed = check_directional_collapse(trajectory, params)
    stagnant = check_stagnation(trajectory, params)
    regressing = check_persistent_regression(trajectory, params)
    failure = collapsed or (stagnant and regressing)

    latest_epm = trajectory[-1].get("epm", {}) if trajectory else {}

    return EPMStatus(
        turn=current_turn,
        success=success,
        victory_type=victory_type,
        failure_detected=failure,
        failure_reasons={
            "collapsed": collapsed,
            "stagnant": stagnant,
            "regressing": regressing,
        },
        metrics={
            "r_t": round(r_t, 4),
            "projection": round(projection, 4),
            "E_total": round(E_total, 4),
            "delta_E": round(latest_epm.get("delta_E", 0.0), 4),
            "alignment": round(latest_epm.get("alignment", 0.0), 4),
        },
        thresholds={
            "epsilon_distance": round(epsilon_distance, 4),
            "epsilon_direction": round(epsilon_direction, 4),
            "epsilon_energy": round(epsilon_energy, 4),
        },
        min_turns_met=current_turn >= params.min_turns,
    )
