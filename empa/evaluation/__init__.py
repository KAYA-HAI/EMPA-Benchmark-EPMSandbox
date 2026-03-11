"""
Post-run evaluation: EPM-Q index, descriptive statistics, and report generation.

Usage::

    from empa.evaluation import generate_report
    stats = generate_report("results/benchmark_runs/gpt-4o_20260304/")
"""

from empa.evaluation.epmq import (
    calculate_epmq_indices,
    compute_composite_scores,
    extract_result_metrics,
    extract_sp_metadata,
)
from empa.evaluation.report import generate_report

__all__ = [
    "calculate_epmq_indices",
    "compute_composite_scores",
    "extract_result_metrics",
    "extract_sp_metadata",
    "generate_report",
]
