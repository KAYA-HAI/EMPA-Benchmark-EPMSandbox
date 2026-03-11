"""
Vector parsing and formatting utilities.

These are convenience helpers used across agents and orchestration layers.
The heavy-lifting vector math lives in :mod:`empa.core.vector_engine`.
"""

from __future__ import annotations

import math
import re
from typing import Tuple

Vector = Tuple[int, ...]


def parse_vector_string(vector_str: str | Tuple) -> Tuple[int, int, int]:
    """Parse ``"(-3, -5, -12)"`` into ``(-3, -5, -12)``."""
    if isinstance(vector_str, (tuple, list)):
        return tuple(int(x) for x in vector_str[:3])  # type: ignore[return-value]
    numbers = re.findall(r"[+-]?\d+", str(vector_str))
    if len(numbers) >= 3:
        return (int(numbers[0]), int(numbers[1]), int(numbers[2]))
    return (0, 0, 0)


def format_vector(vec: Tuple[int, ...], *, with_sign: bool = False) -> str:
    """Format a vector tuple as a readable string."""
    if with_sign:
        return "(" + ", ".join(f"{v:+d}" for v in vec) + ")"
    return "(" + ", ".join(str(v) for v in vec) + ")"


def vector_magnitude(vec: Tuple[int, ...]) -> float:
    """Euclidean norm."""
    return math.sqrt(sum(v ** 2 for v in vec))


def manhattan_distance(vec: Tuple[int, ...]) -> int:
    """Manhattan (L1) distance from the origin."""
    return sum(abs(v) for v in vec)
