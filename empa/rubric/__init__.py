"""
Rubric interface and official rubric implementations.

A *rubric* encapsulates everything that is domain-specific in an EMPA
evaluation: dimension definitions, scoring keys, prompt templates, and
termination parameters.  The evaluation engine is rubric-agnostic — it
operates on N-dimensional vectors and energy scalars, delegating all
domain semantics to the rubric.

Built-in rubrics:

- ``empathy_v2``: The official EPM empathy rubric with C/A/P dimensions,
  IEDR initial-deficit assessment, and MDEP-PR progress tracking.

To create a custom rubric, subclass :class:`RubricConfig` and implement
all abstract methods.  See ``docs/custom_rubric_guide.md`` for a tutorial.
"""

from empa.rubric.base import RubricConfig

__all__ = ["RubricConfig"]
