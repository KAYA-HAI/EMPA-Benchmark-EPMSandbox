"""
IEDR (Initial Empathy Deficit Rating) prompt template.

Re-exports ``generate_iedr_prompt`` which is co-located with the MDEP-PR
prompt in ``mdep_prompt.py`` for historical reasons.
"""

from empa.rubric.empathy_v2.mdep_prompt import generate_iedr_prompt

__all__ = ["generate_iedr_prompt"]
