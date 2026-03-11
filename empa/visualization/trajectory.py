"""
Multi-View 3D Trajectory Visualization.

Generates a publication-quality 2x2 layout:
- Top-left: 3D trajectory overview
- Top-right: XY projection (Cognitive x Affective)
- Bottom-left: XZ projection (Cognitive x Proactive)
- Bottom-right: YZ projection (Affective x Proactive)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

THEME_COLOR = "#D82E4D"

STATUS_STYLES: Dict[str, Dict[str, Any]] = {
    "success": {"line_color": "#1f77b4", "end_color": "green", "end_edge": "darkgreen", "end_marker": "^"},
    "failure": {"line_color": "#d62728", "end_color": "#d62728", "end_edge": "#d62728", "end_marker": "x"},
    "max_turns": {"line_color": "#ff7f0e", "end_color": "#ff7f0e", "end_edge": "#ff7f0e", "end_marker": "x"},
}
_DEFAULT_STYLE: Dict[str, Any] = {
    "line_color": "#6b7280", "end_color": "#6b7280", "end_edge": "#6b7280", "end_marker": "o",
}


def load_trajectories(results_dir: str | Path) -> List[Dict[str, Any]]:
    """Load trajectory data from benchmark result JSON files.

    Parameters
    ----------
    results_dir : path-like
        Directory containing ``script_*_result.json`` files.

    Returns
    -------
    list of dict
        Each dict has keys ``script_id``, ``points`` (ndarray), ``status``,
        ``total_turns``.
    """
    results_dir = Path(results_dir)
    trajectories: List[Dict[str, Any]] = []

    for jf in sorted(results_dir.glob("script_*_result.json")):
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)

        script_id = data["script_id"]
        total_turns = data["total_turns"]
        reason = data.get("termination_reason", "")

        if "EPM" in reason and ("失败" in reason or "负能量" in reason):
            status = "failure"
        elif "对话停滞" in reason:
            status = "failure"
        elif total_turns >= 45:
            status = "max_turns"
        else:
            status = "success"

        epj = data.get("epj", {})
        traj = epj.get("trajectory", [])
        if traj:
            points = np.array([pt["P_t"] for pt in traj])
            trajectories.append({
                "script_id": script_id,
                "points": points,
                "status": status,
                "total_turns": total_turns,
            })

    return trajectories


def smooth_trajectory(points: np.ndarray, num_points: int = 100) -> np.ndarray:
    """Smooth a trajectory using B-spline interpolation."""
    if len(points) < 4:
        return points
    try:
        from scipy.interpolate import make_interp_spline

        dists = np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1))
        cum = np.concatenate([[0], np.cumsum(dists)])
        if cum[-1] <= 0:
            return points
        t = cum / cum[-1]
        t_smooth = np.linspace(0, 1, num_points)
        k = min(3, len(points) - 1)
        return np.column_stack([
            make_interp_spline(t, points[:, i], k=k)(t_smooth)
            for i in range(points.shape[1])
        ])
    except Exception:
        return points


def _axis_range(vals: np.ndarray, pad: float = 0.12):
    """Compute asymmetric axis range that always includes origin."""
    vmin = min(float(np.nanmin(vals)), 0.0)
    vmax = max(float(np.nanmax(vals)), 0.0)
    span = vmax - vmin if vmax != vmin else 1.0
    return vmin - span * pad, vmax + span * pad


def plot_multiview(
    trajectories: List[Dict[str, Any]],
    output_path: str | Path,
    model_name: str = "Model",
) -> None:
    """Generate the production multiview 2x2 trajectory layout.

    This matches the exact visualization style used in the paper figures,
    including the ``#D82E4D`` theme colour for all axes and labels.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    matplotlib.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "axes.unicode_minus": False,
        "axes.facecolor": "white",
        "figure.facecolor": "white",
        "lines.antialiased": True,
        "text.color": THEME_COLOR,
        "axes.labelcolor": THEME_COLOR,
        "xtick.color": THEME_COLOR,
        "ytick.color": THEME_COLOR,
        "axes.edgecolor": THEME_COLOR,
        "axes.titlecolor": THEME_COLOR,
        "axes.titlesize": 22,
        "axes.labelsize": 20,
        "xtick.labelsize": 18,
        "ytick.labelsize": 18,
        "figure.titlesize": 26,
        "figure.dpi": 300,
    })

    fig = plt.figure(figsize=(24, 20), facecolor="white")

    all_pts = np.vstack([t["points"] for t in trajectories])
    x_min, x_max = _axis_range(all_pts[:, 0])
    y_min, y_max = _axis_range(all_pts[:, 1])
    z_min, z_max = _axis_range(all_pts[:, 2])

    n_cases = len(trajectories)

    def _color(status: str) -> str:
        return STATUS_STYLES.get(status, _DEFAULT_STYLE)["line_color"]

    # === 3D Main View ===
    ax_3d = fig.add_subplot(2, 2, 1, projection="3d", facecolor="white")

    for traj in trajectories:
        pts = traj["points"]
        smooth = smooth_trajectory(pts, num_points=100)
        color = _color(traj["status"])
        style = STATUS_STYLES.get(traj["status"], _DEFAULT_STYLE)

        ax_3d.plot(smooth[:, 0], smooth[:, 1], smooth[:, 2],
                   color=color, linewidth=1.2, alpha=0.5, zorder=5)
        ax_3d.scatter(pts[:, 0], pts[:, 1], pts[:, 2],
                      c=color, s=15, alpha=0.6, edgecolors="white",
                      linewidths=0.5, zorder=10)

        ax_3d.scatter([pts[0, 0]], [pts[0, 1]], [pts[0, 2]],
                      c="navy", s=40, marker="o", alpha=0.7, zorder=15)

        if traj["status"] == "success":
            ax_3d.scatter([pts[-1, 0]], [pts[-1, 1]], [pts[-1, 2]],
                          c="green", s=60, marker="^", alpha=0.8,
                          edgecolors="darkgreen", linewidths=1, zorder=15)
        else:
            ax_3d.scatter([pts[-1, 0]], [pts[-1, 1]], [pts[-1, 2]],
                          c=color, s=60, marker="x", alpha=0.9,
                          linewidths=2, zorder=15)

    ax_3d.scatter([0], [0], [0], c="gold", s=600, marker="*",
                  edgecolors="orange", linewidths=3, zorder=100, alpha=0.95)

    ax_3d.set_xlabel("Cognitive (C)", fontsize=20, labelpad=15, fontweight="bold", color=THEME_COLOR)
    ax_3d.set_ylabel("Affective (A)", fontsize=20, labelpad=15, fontweight="bold", color=THEME_COLOR)
    ax_3d.set_zlabel("Proactive (P)", fontsize=20, labelpad=20, fontweight="bold", color=THEME_COLOR)
    ax_3d.set_title(f"3D Trajectory Overview (N={n_cases})",
                    fontsize=22, fontweight="bold", pad=20, color=THEME_COLOR)
    ax_3d.view_init(elev=25, azim=225)
    ax_3d.set_xlim([x_min, x_max])
    ax_3d.set_ylim([y_min, y_max])
    ax_3d.set_zlim([z_min, z_max])
    ax_3d.invert_xaxis()
    ax_3d.invert_yaxis()
    ax_3d.invert_zaxis()
    ax_3d.grid(True, alpha=0.2)

    # === 2D Projections ===
    proj_specs = [
        (2, "XY Projection (Top View)", 0, 1, "Cognitive Axis (C)", "Affective Axis (A)",
         [x_min, x_max], [y_min, y_max]),
        (3, "XZ Projection (Side View)", 0, 2, "Cognitive Axis (C)", "Proactive Axis (P)",
         [x_min, x_max], [z_min, z_max]),
        (4, "YZ Projection (Front View)", 1, 2, "Affective Axis (A)", "Proactive Axis (P)",
         [y_min, y_max], [z_min, z_max]),
    ]
    for subplot_idx, title, xi, yi, xlabel, ylabel, xlim, ylim in proj_specs:
        ax = fig.add_subplot(2, 2, subplot_idx, facecolor="white")
        for traj in trajectories:
            color = _color(traj["status"])
            pts = traj["points"]

            ax.plot(pts[:, xi], pts[:, yi], color=color,
                    linewidth=1.2, alpha=0.5, marker="o", markersize=2)

            ax.scatter([pts[0, xi]], [pts[0, yi]],
                       c="navy", s=25, marker="o", alpha=0.7, zorder=10)

            if traj["status"] == "success":
                ax.scatter([pts[-1, xi]], [pts[-1, yi]],
                           c="green", s=40, marker="^", alpha=0.8, zorder=10)
            else:
                ax.scatter([pts[-1, xi]], [pts[-1, yi]],
                           c=color, s=40, marker="x", alpha=0.9, zorder=10)

        ax.scatter([0], [0], c="gold", s=400, marker="*",
                   edgecolors="orange", linewidths=2.5, zorder=100)
        ax.axhline(0, color="gray", linewidth=1, linestyle="--", alpha=0.4)
        ax.axvline(0, color="gray", linewidth=1, linestyle="--", alpha=0.4)
        ax.set_xlabel(xlabel, fontsize=20, fontweight="bold", color=THEME_COLOR)
        ax.set_ylabel(ylabel, fontsize=20, fontweight="bold", color=THEME_COLOR)
        ax.set_title(title, fontsize=22, fontweight="bold", pad=15, color=THEME_COLOR)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(True, alpha=0.25, linestyle="-", linewidth=0.5)
        ax.invert_xaxis()
        ax.invert_yaxis()

    # === Global Legend ===
    legend_elements = [
        Line2D([0], [0], color="#1f77b4", lw=4, label="Success Path"),
        Line2D([0], [0], color="#d62728", lw=4, label="Failure Path"),
        Line2D([0], [0], color="#ff7f0e", lw=4, label="Timeout Path"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="navy",
               markersize=15, label="Start Point", markeredgecolor="white", markeredgewidth=1),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="green",
               markersize=15, label="Success End", markeredgecolor="darkgreen", markeredgewidth=1),
        Line2D([0], [0], marker="x", color="red", linestyle="None",
               markersize=15, label="Failure End", markeredgewidth=3),
        Line2D([0], [0], marker="*", color="w", markerfacecolor="gold",
               markersize=20, label="Target Origin", markeredgecolor="orange", markeredgewidth=1.5),
    ]
    fig.legend(handles=legend_elements, loc="upper center",
               bbox_to_anchor=(0.5, 0.955), ncol=7,
               fontsize=18, framealpha=0.95, edgecolor=THEME_COLOR, labelcolor=THEME_COLOR)

    fig.suptitle(
        f"Multi-View 3D Trajectory Analysis: {model_name}\n"
        f"Visualization of {n_cases} Real-World Cases with Orthogonal Projections",
        fontsize=26, fontweight="bold", y=0.99, color=THEME_COLOR,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.93])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), dpi=300, bbox_inches="tight", pad_inches=0.3)
    plt.close()
    print(f"✅ Saved: {output_path}")
