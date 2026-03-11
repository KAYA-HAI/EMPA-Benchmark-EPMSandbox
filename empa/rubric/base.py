"""
Abstract base class for evaluation rubrics.

A ``RubricConfig`` fully specifies the domain-specific aspects of an
EMPA evaluation.  The core engine calls rubric methods to:

1. Know how many dimensions the evaluation space has and what they are called.
2. Convert a filled initial-assessment form into an initial deficit vector.
3. Convert a filled progress form into an increment vector.
4. Generate the LLM prompts that instruct the Judger how to fill each form.
5. Generate the LLM prompts that instruct the Director how to guide dialogue.
6. Provide termination parameters (thresholds, window sizes, etc.).

All vector operations in the engine are dimension-agnostic: they work with
``Tuple[float, ...]`` of length ``n_dimensions``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple


@dataclass(frozen=True)
class DimensionDef:
    """Definition of a single evaluation dimension."""

    name: str
    description: str
    progress_indicators: List[str] = field(default_factory=list)
    regression_indicators: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class TerminationParams:
    """Parameters that govern when a dialogue should stop."""

    epsilon: float = 1.0
    max_turns: int = 45
    min_turns: int = 12
    eval_interval: int = 1
    alpha: float = 0.05
    collapse_window: int = 5
    stagnation_window: int = 5
    stagnation_threshold: float = 0.5
    regression_window: int = 8
    regression_ratio: float = 0.7


class RubricConfig(ABC):
    """
    Abstract base for all evaluation rubrics.

    Subclasses must implement every ``@abstractmethod``.  The engine never
    imports domain-specific constants directly — it always asks the rubric.
    """

    # ------------------------------------------------------------------
    # Dimension metadata
    # ------------------------------------------------------------------

    @abstractmethod
    def dimensions(self) -> List[DimensionDef]:
        """Return ordered list of evaluation dimensions."""
        ...

    @property
    def n_dimensions(self) -> int:
        return len(self.dimensions())

    @property
    def dimension_names(self) -> List[str]:
        return [d.name for d in self.dimensions()]

    # ------------------------------------------------------------------
    # Scoring keys
    # ------------------------------------------------------------------

    @abstractmethod
    def initial_scoring_key(self) -> Dict[Tuple[str, int], int]:
        """
        Map ``(indicator_id, level) -> deficit_score`` for the initial
        assessment form.

        Example (empathy rubric)::

            {("C.1", 0): 0, ("C.1", 1): -2, ("C.1", 2): -4, ...}
        """
        ...

    @abstractmethod
    def progress_scoring_key(self) -> Dict[str, Dict[int, int]]:
        """
        Map ``indicator_id -> {level: score}`` for the progress form.

        Example (empathy rubric)::

            {"C.Prog": {0: 0, 1: +1, 2: +3},
             "C.Neg":  {0: 0, -1: -2, -2: -4}, ...}
        """
        ...

    # ------------------------------------------------------------------
    # Prompt generation
    # ------------------------------------------------------------------

    @abstractmethod
    def generate_initial_assessment_prompt(
        self, script_content: Dict[str, Any]
    ) -> str:
        """
        Build the LLM prompt that asks the Judger to fill the initial
        assessment form (e.g. IEDR for empathy).
        """
        ...

    @abstractmethod
    def generate_progress_prompt(
        self,
        recent_turns: list,
        script_context: Dict[str, Any] | None = None,
        full_history: list | None = None,
    ) -> str:
        """
        Build the LLM prompt that asks the Judger to fill the progress
        form (e.g. MDEP-PR for empathy).
        """
        ...

    @abstractmethod
    def generate_director_system_prompt(
        self,
        scenario: Dict[str, Any],
        actor_prompt: str,
    ) -> str:
        """Build the Director's system prompt."""
        ...

    @abstractmethod
    def generate_test_model_system_prompt(self) -> str:
        """Build the TestModel's system prompt."""
        ...

    # ------------------------------------------------------------------
    # Vector computation helpers
    # ------------------------------------------------------------------

    def compute_initial_deficit(
        self, filled_form: Dict[str, int]
    ) -> Tuple[float, ...]:
        """
        Convert a filled initial-assessment form into the initial deficit
        vector P_0.  Default implementation uses ``initial_scoring_key()``.
        """
        dims = self.dimensions()
        scoring = self.initial_scoring_key()
        result = []
        for dim in dims:
            total = 0
            for indicator in dim.progress_indicators + dim.regression_indicators:
                level = filled_form.get(indicator, 0)
                total += scoring.get((indicator, level), 0)
            result.append(total)
        return tuple(result)

    def compute_increment(
        self, filled_form: Dict[str, int]
    ) -> Tuple[float, ...]:
        """
        Convert a filled progress form into the increment vector v_t.
        Default implementation uses ``progress_scoring_key()``.
        """
        dims = self.dimensions()
        scoring = self.progress_scoring_key()
        result = []
        for dim in dims:
            prog_key = f"{dim.name}.Prog"
            neg_key = f"{dim.name}.Neg"
            val = scoring.get(prog_key, {}).get(filled_form.get(prog_key, 0), 0)
            val += scoring.get(neg_key, {}).get(filled_form.get(neg_key, 0), 0)
            result.append(val)
        return tuple(result)

    # ------------------------------------------------------------------
    # Termination parameters
    # ------------------------------------------------------------------

    def termination_params(self) -> TerminationParams:
        """Return termination parameters.  Override to customize."""
        return TerminationParams()

    # ------------------------------------------------------------------
    # Optional: extract context for Judger
    # ------------------------------------------------------------------

    def extract_judger_context(self, actor_prompt: str) -> str:
        """
        Extract a condensed version of the actor prompt for the Judger.
        Default: return full prompt.  Override for domain-specific extraction.
        """
        return actor_prompt
