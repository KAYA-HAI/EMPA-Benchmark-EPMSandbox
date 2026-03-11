#!/usr/bin/env python3
"""
Example: Define a custom rubric for EMPA.

This shows how to create a custom evaluation rubric by subclassing
:class:`empa.rubric.base.RubricConfig`.  The custom rubric can define
its own dimensions, scoring keys, and prompt templates.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Tuple

from empa.rubric.base import DimensionDef, RubricConfig, TerminationParams


class SimpleEmpathyRubric(RubricConfig):
    """A minimal 2-dimension rubric for demonstration purposes."""

    def dimensions(self) -> List[DimensionDef]:
        return [
            DimensionDef(
                name="E",
                description="Emotional Empathy",
                progress_indicators=["E.Prog"],
                regression_indicators=["E.Neg"],
            ),
            DimensionDef(
                name="C",
                description="Cognitive Empathy",
                progress_indicators=["C.Prog"],
                regression_indicators=["C.Neg"],
            ),
        ]

    @property
    def dimension_names(self) -> List[str]:
        return ["E", "C"]

    def initial_scoring_key(self) -> Dict[Tuple[str, int], int]:
        return {
            ("E.1", 0): 0, ("E.1", 1): -2, ("E.1", 2): -4, ("E.1", 3): -6,
            ("E.2", 0): 0, ("E.2", 1): -2, ("E.2", 2): -4, ("E.2", 3): -6,
            ("C.1", 0): 0, ("C.1", 1): -2, ("C.1", 2): -4, ("C.1", 3): -6,
            ("C.2", 0): 0, ("C.2", 1): -2, ("C.2", 2): -4, ("C.2", 3): -6,
        }

    def progress_scoring_key(self) -> Dict[str, Dict[int, int]]:
        return {
            "E.Prog": {0: 0, 1: 2, 2: 4},
            "E.Neg": {0: 0, -1: -2, -2: -4},
            "C.Prog": {0: 0, 1: 2, 2: 4},
            "C.Neg": {0: 0, -1: -2, -2: -4},
        }

    def termination_params(self) -> TerminationParams:
        return TerminationParams(epsilon=1.0, min_turns=6, max_turns=20)

    def generate_initial_assessment_prompt(self, script_content: dict) -> str:
        return "Rate initial emotional/cognitive empathy deficit..."

    def generate_progress_prompt(
        self, recent_turns: list, script_context: dict = None, full_history: list = None
    ) -> str:
        return "Rate empathy progress for the last K turns..."

    def generate_director_system_prompt(self, scenario: dict, **kwargs) -> str:
        return "You are a dialogue director..."

    def generate_test_model_system_prompt(self) -> str:
        return "You are a helpful and empathetic AI assistant."


def main():
    rubric = SimpleEmpathyRubric()
    print("Custom Rubric:")
    print(f"  Dimensions: {rubric.dimension_names}")
    print(f"  Num dimensions: {len(rubric.dimensions())}")
    print(f"  Termination params: epsilon={rubric.termination_params().epsilon}, "
          f"min_turns={rubric.termination_params().min_turns}")

    filled_iedr = {"E.1": 2, "E.2": 1, "C.1": 3, "C.2": 1}
    P_0 = rubric.compute_initial_deficit(filled_iedr)
    print(f"\n  Initial deficit P_0: {P_0}")

    filled_mdep = {"E.Prog": 1, "E.Neg": 0, "C.Prog": 2, "C.Neg": 0}
    v_t = rubric.compute_increment(filled_mdep)
    print(f"  Increment v_t: {v_t}")

    from empa.core.vector_engine import VectorEngine
    engine = VectorEngine(n_dims=2, epsilon=1.0, enable_epm=True)
    engine.initialize(P_0)
    engine.update(v_t, turn=3)
    print(f"  After 1 step: P_t={engine.get_position()}")


if __name__ == "__main__":
    main()
