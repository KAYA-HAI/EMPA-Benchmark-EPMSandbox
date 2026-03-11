"""
Generic scoring engine that delegates to a RubricConfig.

This module provides the bridge between the rubric's scoring keys and
the vector engine.  It never hardcodes any dimension names or score values.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from empa.rubric.base import RubricConfig

Vector = Tuple[float, ...]


class ScoringEngine:
    """
    Converts filled rubric forms into vectors using the active rubric.

    This class holds a reference to the rubric and exposes simple methods
    that the orchestrator can call without knowing rubric internals.
    """

    def __init__(self, rubric: RubricConfig):
        self.rubric = rubric

    @property
    def n_dimensions(self) -> int:
        return self.rubric.n_dimensions

    @property
    def dimension_names(self) -> List[str]:
        return self.rubric.dimension_names

    def compute_initial_deficit(self, filled_form: Dict[str, int]) -> Vector:
        """Compute P_0 from a filled initial-assessment form."""
        return self.rubric.compute_initial_deficit(filled_form)

    def compute_increment(self, filled_form: Dict[str, int]) -> Vector:
        """Compute v_t from a filled progress form."""
        return self.rubric.compute_increment(filled_form)

    def compute_display_progress(
        self, current_P: Vector, P_0: Vector
    ) -> float:
        """
        Compute a 0–100 display progress score.

        This is a heuristic for human readability, not used for decisions.
        The formula measures how much of each dimension's deficit has been
        recovered, clipped to [0, 100].
        """
        if not P_0 or all(x == 0 for x in P_0):
            return 100.0

        recoveries = []
        for p0, pt in zip(P_0, current_P):
            if p0 == 0:
                recoveries.append(100.0)
            else:
                recovery = (1.0 - pt / p0) * 100.0
                recoveries.append(max(0.0, min(100.0, recovery)))

        return sum(recoveries) / len(recoveries)
