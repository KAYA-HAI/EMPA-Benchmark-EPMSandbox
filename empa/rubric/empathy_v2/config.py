"""
Official EPM empathy rubric v2 — concrete RubricConfig implementation.

This file contains the scoring keys, dimension definitions, and prompt
generation logic that constitute the core intellectual property of
EMPA.  The evaluation engine calls these through the RubricConfig
interface, never importing them directly.

Scoring design:

    Base Deficit Unit (BDU) = -2

    IED multipliers per indicator type:
      - Standard   (x1.0): -2, -4, -6
      - Priority   (x1.5): -3, -6, -9
      - Core       (x2.0): -4, -8, -12

    MDEP progress scores:  0 → 0,  1 → +1,  2 → +3
    MDEP regression scores: 0 → 0, -1 → -2, -2 → -4/-5
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from empa.rubric.base import DimensionDef, RubricConfig, TerminationParams

# ======================================================================
# Scoring Keys (unchanged from original — every value preserved exactly)
# ======================================================================

IED_SCORING_KEY: Dict[Tuple[str, int], int] = {
    # C axis — Cognitive empathy
    ("C.1", 0): 0,   ("C.1", 1): -2,  ("C.1", 2): -4,  ("C.1", 3): -6,   # Complexity:  standard  (x1.0)
    ("C.2", 0): 0,   ("C.2", 1): -2,  ("C.2", 2): -4,  ("C.2", 3): -6,   # Depth:       standard  (x1.0)
    ("C.3", 0): 0,   ("C.3", 1): -3,  ("C.3", 2): -6,  ("C.3", 3): -9,   # Priority:    priority  (x1.5)
    # A axis — Affective empathy
    ("A.1", 0): 0,   ("A.1", 1): -2,  ("A.1", 2): -4,  ("A.1", 3): -6,   # Intensity:   standard  (x1.0)
    ("A.2", 0): 0,   ("A.2", 1): -4,  ("A.2", 2): -8,  ("A.2", 3): -12,  # Accessibility: core    (x2.0)
    ("A.3", 0): 0,   ("A.3", 1): -3,  ("A.3", 2): -6,  ("A.3", 3): -9,   # Priority:    priority  (x1.5)
    # P axis — Motivational empathy
    ("P.1", 0): 0,   ("P.1", 1): -2,  ("P.1", 2): -4,  ("P.1", 3): -6,   # Agency:      standard  (x1.0)
    ("P.2", 0): 0,   ("P.2", 1): -4,  ("P.2", 2): -8,  ("P.2", 3): -12,  # Value:       core      (x2.0)
    ("P.3", 0): 0,   ("P.3", 1): -3,  ("P.3", 2): -6,  ("P.3", 3): -9,   # Priority:    priority  (x1.5)
}

MDEP_SCORING_KEY: Dict[str, Dict[int, int]] = {
    "C.Prog": {0: 0, 1: +1, 2: +3},
    "C.Neg":  {0: 0, -1: -2, -2: -4},
    "A.Prog": {0: 0, 1: +1, 2: +3},
    "A.Neg":  {0: 0, -1: -2, -2: -5},
    "P.Prog": {0: 0, 1: +1, 2: +3},
    "P.Neg":  {0: 0, -1: -2, -2: -5},
}

# Indicators grouped by dimension, used for initial deficit computation
_IED_INDICATORS = {
    "C": ["C.1", "C.2", "C.3"],
    "A": ["A.1", "A.2", "A.3"],
    "P": ["P.1", "P.2", "P.3"],
}


# ======================================================================
# Concrete RubricConfig
# ======================================================================

class EmpathyRubricV2(RubricConfig):
    """
    Official EPM empathy rubric with C/A/P dimensions.

    This rubric assesses empathic dialogue quality across three axes:

    - **C** (Cognitive): Being understood — situation comprehension, depth,
      and the priority the speaker assigns to cognitive empathy.
    - **A** (Affective): Being resonated with — emotional intensity,
      accessibility, and affective-empathy priority.
    - **P** (Motivational): Being affirmed — initial agency level, value
      relevance, and motivational-empathy priority.
    """

    def dimensions(self) -> List[DimensionDef]:
        return [
            DimensionDef(
                name="C",
                description="Cognitive empathy — being understood",
                progress_indicators=["C.1", "C.2", "C.3"],
                regression_indicators=[],
            ),
            DimensionDef(
                name="A",
                description="Affective empathy — being resonated with",
                progress_indicators=["A.1", "A.2", "A.3"],
                regression_indicators=[],
            ),
            DimensionDef(
                name="P",
                description="Motivational empathy — being affirmed/empowered",
                progress_indicators=["P.1", "P.2", "P.3"],
                regression_indicators=[],
            ),
        ]

    def initial_scoring_key(self) -> Dict[Tuple[str, int], int]:
        return IED_SCORING_KEY

    def progress_scoring_key(self) -> Dict[str, Dict[int, int]]:
        return MDEP_SCORING_KEY

    def termination_params(self) -> TerminationParams:
        return TerminationParams(
            max_turns=45,
            min_turns=12,
            eval_interval=1,
            alpha=0.05,
            collapse_window=5,
            stagnation_window=5,
            stagnation_threshold=0.5,
            regression_window=8,
            regression_ratio=0.7,
        )

    # ------------------------------------------------------------------
    # Vector computation (override for exact backward compatibility)
    # ------------------------------------------------------------------

    def compute_initial_deficit(
        self, filled_form: Dict[str, int]
    ) -> Tuple[float, ...]:
        result = []
        for dim_name, indicators in _IED_INDICATORS.items():
            total = 0
            for ind in indicators:
                level = filled_form.get(ind, 0)
                total += IED_SCORING_KEY.get((ind, level), 0)
            result.append(total)
        return tuple(result)

    def compute_increment(
        self, filled_form: Dict[str, int]
    ) -> Tuple[float, ...]:
        result = []
        for dim in self.dimension_names:
            prog_key = f"{dim}.Prog"
            neg_key = f"{dim}.Neg"
            val = MDEP_SCORING_KEY[prog_key].get(filled_form.get(prog_key, 0), 0)
            val += MDEP_SCORING_KEY[neg_key].get(filled_form.get(neg_key, 0), 0)
            result.append(val)
        return tuple(result)

    # ------------------------------------------------------------------
    # Prompt generation (delegated to separate modules)
    # ------------------------------------------------------------------

    def generate_initial_assessment_prompt(
        self, script_content: Dict[str, Any]
    ) -> str:
        from empa.rubric.empathy_v2.iedr_prompt import generate_iedr_prompt
        return generate_iedr_prompt(script_content)

    def generate_progress_prompt(
        self,
        recent_turns: list,
        script_context: Dict[str, Any] | None = None,
        full_history: list | None = None,
    ) -> str:
        from empa.rubric.empathy_v2.mdep_prompt import generate_mdep_pr_prompt
        return generate_mdep_pr_prompt(recent_turns, script_context, full_history)

    def generate_director_system_prompt(
        self,
        scenario: Dict[str, Any],
        actor_prompt: str,
    ) -> str:
        from empa.rubric.empathy_v2.director_prompt import generate_director_prompt
        return generate_director_prompt(scenario, actor_prompt)

    def generate_test_model_system_prompt(self) -> str:
        from empa.rubric.empathy_v2.test_model_prompt import (
            TEST_MODEL_SYSTEM_PROMPT,
        )
        return TEST_MODEL_SYSTEM_PROMPT

    # ------------------------------------------------------------------
    # Judger context extraction (empathy-specific)
    # ------------------------------------------------------------------

    def extract_judger_context(self, actor_prompt: str) -> str:
        from empa.rubric.empathy_v2.mdep_prompt import extract_judger_context
        return extract_judger_context(actor_prompt)
