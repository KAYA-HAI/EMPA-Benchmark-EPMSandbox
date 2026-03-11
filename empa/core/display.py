"""
Display-only progress metrics.

.. warning::
    These metrics are **strictly for UI / reporting purposes**.
    Termination decisions must use the epsilon-zone or EPM energy logic
    from :mod:`empa.core.vector_engine` and :mod:`empa.core.energy_dynamics`.
"""

from __future__ import annotations

from typing import Tuple


def calculate_display_progress(
    P_t: Tuple[int, ...], P_0: Tuple[int, ...]
) -> float:
    """Return an approximate 0-100 progress score (Manhattan-based)."""
    initial_total = sum(abs(v) for v in P_0)
    if initial_total == 0:
        return 100.0
    current_total = sum(abs(v) for v in P_t)
    ratio = (initial_total - current_total) / initial_total
    return max(0.0, min(100.0, ratio * 100.0))


def dimensional_progress(
    P_t: Tuple[int, ...], P_0: Tuple[int, ...]
) -> dict[str, float]:
    """Per-axis 0-100 progress (display only)."""
    labels = ["C", "A", "P"]
    result = {}
    for i, label in enumerate(labels[: len(P_t)]):
        initial = abs(P_0[i]) if i < len(P_0) else 0
        current = abs(P_t[i])
        if initial == 0:
            result[f"{label}_progress"] = 100.0
        else:
            r = (initial - current) / initial
            result[f"{label}_progress"] = max(0.0, min(100.0, r * 100.0))
    return result
