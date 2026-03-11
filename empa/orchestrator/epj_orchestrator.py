"""
EPJ Orchestrator — vector computation and state management.

Acts as the **calculator** layer in the three-tier EPJ architecture:
    Judger (sensor) → **Orchestrator (calculator)** → Director (decision maker)

The orchestrator:
1. Receives numeric ratings from the Judger.
2. Delegates vector math to :class:`~empa.core.vector_engine.VectorEngine`.
3. Produces a *state packet* consumed by the Director.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from empa.agents.base import BaseJudger
from empa.core.vector_engine import VectorEngine
from dataclasses import asdict

from empa.core.energy_dynamics import (
    evaluate_epm_state,
)
from empa.rubric.base import RubricConfig, TerminationParams

logger = logging.getLogger(__name__)


class EPJOrchestrator:
    """EPJ state machine that bridges the Judger and the Director."""

    def __init__(
        self,
        judger: BaseJudger,
        rubric: RubricConfig,
        *,
        K: int = 1,
        max_turns: int = 45,
        enable_epm: bool = True,
    ) -> None:
        n_dims = len(rubric.dimensions())
        epsilon = rubric.termination_params().epsilon
        self.judger = judger
        self.rubric = rubric
        self.K = K
        self.max_turns = max_turns
        self.enable_epm = enable_epm

        self.engine = VectorEngine(n_dims=n_dims, epsilon=epsilon, enable_epm=enable_epm)
        self.initialized = False
        self.iedr_result: Optional[dict] = None

    # ------------------------------------------------------------------
    # Initialization (T=0)
    # ------------------------------------------------------------------

    def initialize_at_T0(self, script_content: dict) -> dict:
        """Compute P_0 by having the Judger fill the initial form."""
        filled = self.judger.fill_initial_assessment(script_content)
        P_0 = self.rubric.compute_initial_deficit(filled)
        tp = self.engine.initialize(P_0)

        self.initialized = True
        self.iedr_result = {
            "filled_iedr": filled,
            "P_0": P_0,
            "initial_distance": tp["distance"],
            "source": "runtime_evaluation",
        }
        logger.info("EPJ T=0: P_0=%s, distance=%.2f", P_0, tp["distance"])
        return {"P_0": P_0, "filled_iedr": filled, "initial_distance": tp["distance"]}

    def initialize_with_precomputed_iedr(
        self,
        filled_iedr: dict,
        P_0: Tuple[int, ...],
        epm_precomputed: Optional[dict] = None,
    ) -> dict:
        """Skip the Judger and use pre-computed IEDR data."""
        tp = self.engine.initialize(P_0, epm_precomputed=epm_precomputed)

        self.initialized = True
        self.iedr_result = {
            "filled_iedr": filled_iedr,
            "P_0": P_0,
            "initial_distance": tp["distance"],
            "source": "precomputed",
        }
        logger.info("EPJ T=0 (precomputed): P_0=%s, distance=%.2f", P_0, tp["distance"])
        return {"P_0": P_0, "filled_iedr": filled_iedr, "initial_distance": tp["distance"]}

    # ------------------------------------------------------------------
    # Periodic evaluation
    # ------------------------------------------------------------------

    def evaluate_at_turn_K(
        self,
        recent_turns: list,
        current_turn: int,
        script_content: Optional[dict] = None,
        full_history: Optional[list] = None,
    ) -> dict:
        """Fill MDEP-PR, update the vector, and return a state packet."""
        if not self.initialized:
            raise RuntimeError("EPJ not initialized — call initialize_at_T0 first")

        filled = self.judger.fill_progress_form(
            recent_turns, script_context=script_content, full_history=full_history
        )
        v_t = self.rubric.compute_increment(filled)
        mdep_analysis = filled.get("detailed_analysis")

        tp = self.engine.update(v_t, current_turn, mdep_analysis)

        state_packet = self._build_state_packet(current_turn)
        state_packet["filled_mdep_pr"] = filled

        if self.enable_epm and self.engine.v_star_0 is not None:
            epm_summary = self._compute_epm_summary(current_turn)
            if epm_summary:
                state_packet["epm_summary"] = epm_summary

        return state_packet

    def should_evaluate(self, current_turn: int) -> bool:
        return current_turn > 0 and current_turn % self.K == 0

    # ------------------------------------------------------------------
    # State accessors
    # ------------------------------------------------------------------

    def get_current_position(self) -> Tuple[int, ...]:
        return self.engine.current_P or (0,) * len(self.rubric.dimensions())

    def get_initial_deficit(self) -> Tuple[int, ...]:
        return self.engine.P_0 or (0,) * len(self.rubric.dimensions())

    def get_trajectory(self) -> list:
        return self.engine.trajectory

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_state_packet(self, current_turn: int) -> dict:
        traj = self.engine.trajectory
        latest = traj[-1] if traj else {}
        P_0 = self.get_initial_deficit()
        P_t = self.get_current_position()
        distance = latest.get("distance", 0)
        in_zone = latest.get("in_zone", False)

        return {
            "current_turn": current_turn,
            "P_0_start_deficit": str(P_0),
            "P_t_current_position": str(P_t),
            "v_t_last_increment": str(latest.get("v_t", (0,) * len(P_0))),
            "distance_to_goal": distance,
            "is_in_zone": in_zone,
            "is_timeout": current_turn >= self.max_turns,
            "max_turns": self.max_turns,
            "trajectory": traj,
        }

    def _compute_epm_summary(self, current_turn: int) -> Optional[dict]:
        traj = self.engine.trajectory
        if not traj or "epm" not in traj[-1]:
            return None
        epm = traj[-1]["epm"]
        r_t = epm["P_norm"]
        projection = epm["projection"]
        E_total = epm["E_total"]
        eps_d = self.engine.epsilon_distance or 0
        eps_dir = self.engine.epsilon_direction or 0
        eps_e = self.engine.epsilon_energy or 0

        status = evaluate_epm_state(
            current_turn=current_turn,
            r_t=r_t,
            projection=projection,
            E_total=E_total,
            epsilon_distance=eps_d,
            epsilon_direction=eps_dir,
            epsilon_energy=eps_e,
            trajectory=traj,
            params=self.rubric.termination_params(),
        )
        result = asdict(status)

        result["progress"] = {
            "geometric": f"{(1 - r_t / eps_d) * 100:.1f}%" if eps_d > 0 else "N/A",
            "positional": f"{((projection + eps_dir) / eps_dir) * 100:.1f}%" if eps_dir > 0 else "N/A",
            "energetic": f"{(E_total / eps_e) * 100:.1f}%" if eps_e > 0 else "N/A",
        }
        result["collapsed"] = result.get("failure_reasons", {}).get("collapsed", False)

        return result
