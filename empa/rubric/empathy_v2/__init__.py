"""
Official EPM empathy rubric v2.

This rubric evaluates empathic dialogue along three dimensions:

- **C** (Cognitive empathy): Being understood
- **A** (Affective empathy): Being resonated with
- **P** (Motivational empathy): Being affirmed / empowered

It includes two assessment instruments:

- **IEDR** (Initial Empathy Deficit Rating): 9 indicators, 4 levels each,
  used at T=0 to establish the initial deficit vector P_0.
- **MDEP-PR** (Multi-Dimensional Empathy Progress Rating): 6 indicators
  (3 progress + 3 regression), used every K turns to compute v_t.
"""

from empa.rubric.empathy_v2.config import EmpathyRubricV2

__all__ = ["EmpathyRubricV2"]
