"""
Visualization tools for EMPA results.

Single-model trajectory::

    from empa.visualization import load_trajectories, plot_multiview
    trajectories = load_trajectories("results/benchmark_runs/gpt-4o_20260304/")
    plot_multiview(trajectories, "output/multiview.png", model_name="GPT-4o")

Multi-model comparison::

    from empa.visualization import discover_models, plot_errorbar_bars, plot_radar_grid
    models = discover_models("results/benchmark_runs/epm-bench/")
    plot_errorbar_bars(models, output_dir="output/")
    plot_radar_grid(models, output_dir="output/")
    generate_comparison_table(models, output_dir="output/")
    generate_epmq_summary_table(models, output_dir="output/")
"""

from empa.visualization.trajectory import (
    load_trajectories,
    plot_multiview,
    smooth_trajectory,
)
from empa.visualization.comparison import (
    discover_models,
    generate_comparison_table,
    generate_epmq_summary_table,
    plot_errorbar_bars,
    plot_radar_grid,
)

__all__ = [
    # Single-model trajectory
    "load_trajectories",
    "plot_multiview",
    "smooth_trajectory",
    # Multi-model comparison
    "discover_models",
    "plot_errorbar_bars",
    "plot_radar_grid",
    "generate_comparison_table",
    "generate_epmq_summary_table",
]
