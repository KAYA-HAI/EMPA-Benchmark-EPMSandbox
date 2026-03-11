"""
Generate descriptive statistics and EPM-Q reports from benchmark results.

Outputs CSV, Excel (with multi-level headers), and Markdown summary.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from empa.evaluation.epmq import (
    compute_composite_scores,
    extract_result_metrics,
    extract_sp_metadata,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_case_metadata(metadata_file: Optional[Path] = None) -> Dict[str, Dict]:
    """Load case sampling metadata (dominant axis, difficulty, category, etc.)."""
    if metadata_file is None:
        metadata_file = _DATA_DIR / "case_metadata.json"
    if not metadata_file.exists():
        return {}

    with open(metadata_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cases_list = data.get("selected_cases", data.get("sampled_cases", []))
    meta: Dict[str, Dict] = {}
    for case in cases_list:
        sid = case["script_id"]
        deficits = case.get("deficits", {})
        meta[sid] = {
            "dominant_axis": case.get("dominant_axis", "N/A"),
            "difficulty": case.get("difficulty", "N/A"),
            "category": case.get("category", "未分类"),
            "C_deficit": deficits.get("C", "N/A"),
            "A_deficit": deficits.get("A", "N/A"),
            "P_deficit": deficits.get("P", "N/A"),
            "total_deficit": deficits.get("total", "N/A"),
        }
    return meta


def generate_report(
    results_dir: str | Path,
    *,
    metadata_file: Optional[Path] = None,
    output_base: Optional[str] = None,
    formats: str = "all",
) -> Dict[str, Any]:
    """Generate evaluation report from a benchmark results directory.

    Parameters
    ----------
    results_dir : path-like
        Directory containing ``script_*_result.json`` and ``summary.json``.
    metadata_file : Path, optional
        Case metadata JSON. Defaults to built-in ``case_metadata.json``.
    output_base : str, optional
        Base path (without extension) for output files. Defaults to
        ``<results_dir>/descriptive_statistics``.
    formats : str
        One of ``"csv"``, ``"excel"``, ``"markdown"``, ``"all"``.

    Returns
    -------
    dict
        Summary statistics including EPM-Q composite scores.
    """
    import numpy as np
    import pandas as pd

    results_dir = Path(results_dir)
    metadata = load_case_metadata(metadata_file)

    # Load individual result files
    result_files = sorted(results_dir.glob("script_*_result.json"))
    if not result_files:
        result_files = sorted(results_dir.glob("script_*.json"))

    results: List[Dict] = []
    for rf in result_files:
        with open(rf, "r", encoding="utf-8") as f:
            results.append(json.load(f))

    if not results:
        summary_file = results_dir / "summary.json"
        if summary_file.exists():
            with open(summary_file, "r", encoding="utf-8") as f:
                summary = json.load(f)
            results = summary.get("results", [])

    if not results:
        raise FileNotFoundError(f"No result files found in {results_dir}")

    _DIFF_EN = {"较易": "Easy", "中等": "Medium", "困难": "Hard", "极难": "Very Hard"}
    _CAT_EN = {
        "休闲娱乐": "Leisure", "身心健康": "Health", "生活状况": "Life",
        "观念认同": "Values", "人际关系": "Relations", "生涯发展": "Career",
        "未分类": "Unclassified",
    }
    _SP_EN = {"高": "High", "中": "Medium", "低": "Low"}

    # --- Build per-case rows ---
    rows: List[Dict] = []
    for result in results:
        script_id = result.get("script_id", "N/A")

        individual = results_dir / f"{script_id}_result.json"
        if individual.exists():
            try:
                with open(individual, "r", encoding="utf-8") as f:
                    result = json.load(f)
            except Exception:
                pass

        row: Dict[str, Any] = {}
        metrics = extract_result_metrics(result)

        # Deficits from trajectory
        c_def = a_def = p_def = total_def = "N/A"
        traj = result.get("epj", {}).get("trajectory", [])
        if traj:
            p0 = traj[0].get("P_t", [])
            if len(p0) == 3:
                c_def = round(-p0[0], 2) if p0[0] < 0 else 0.0
                a_def = round(-p0[1], 2) if p0[1] < 0 else 0.0
                p_def = round(-p0[2], 2) if p0[2] < 0 else 0.0
                total_def = round(c_def + a_def + p_def, 2)

        meta = metadata.get(script_id, {})
        row["Case_ID"] = script_id
        row["Dominant_Axis"] = meta.get("dominant_axis", "N/A")
        row["Difficulty"] = _DIFF_EN.get(meta.get("difficulty", ""), meta.get("difficulty", "N/A"))
        row["Category"] = _CAT_EN.get(meta.get("category", ""), meta.get("category", "N/A"))

        sp = extract_sp_metadata(script_id)
        row["SP_Empathy_Threshold"] = _SP_EN.get(sp.get("sp_threshold_level", ""), sp.get("sp_threshold_level", "N/A"))
        row["SP_Emotional_Priority"] = _SP_EN.get(sp.get("sp_emotional_priority", ""), sp.get("sp_emotional_priority", "N/A"))
        row["SP_Motivational_Priority"] = _SP_EN.get(sp.get("sp_motivational_priority", ""), sp.get("sp_motivational_priority", "N/A"))
        row["SP_Cognitive_Priority"] = _SP_EN.get(sp.get("sp_cognitive_priority", ""), sp.get("sp_cognitive_priority", "N/A"))

        row["C_Deficit"] = c_def if c_def != "N/A" else meta.get("C_deficit", "N/A")
        row["A_Deficit"] = a_def if a_def != "N/A" else meta.get("A_deficit", "N/A")
        row["P_Deficit"] = p_def if p_def != "N/A" else meta.get("P_deficit", "N/A")
        row["Total_Deficit"] = total_def if total_def != "N/A" else meta.get("total_deficit", "N/A")

        row["Success"] = "Yes" if metrics.get("success") else "No"
        row["Turns"] = metrics.get("total_turns", 0)
        row["Termination_Type"] = metrics.get("termination_type", "N/A")

        row["Initial_Distance"] = round(metrics.get("initial_distance", 0), 2)
        row["Final_Distance"] = round(metrics.get("final_distance", 0), 2)
        row["Distance_Improvement%"] = round(metrics.get("distance_improvement_rate", 0), 1)
        row["Total_Energy"] = round(metrics.get("E_total", 0), 2)
        row["Energy_Achievement%"] = round(metrics.get("energy_achievement_rate", 0), 1)
        row["Energy_Surplus"] = round(metrics.get("energy_surplus", 0), 2)

        row["Geometric_Win"] = "Yes" if metrics.get("geometric_achieved") else "No"
        row["Positional_Win"] = "Yes" if metrics.get("positional_achieved") else "No"
        row["Energetic_Win"] = "Yes" if metrics.get("energetic_achieved") else "No"

        row["C_Net_Score"] = metrics.get("C_net_score", 0)
        row["A_Net_Score"] = metrics.get("A_net_score", 0)
        row["P_Net_Score"] = metrics.get("P_net_score", 0)
        row["Total_Net_Score"] = metrics.get("total_net_score", 0)

        row["C_Prog_sum"] = metrics.get("C_Prog_sum", 0)
        row["C_Neg_sum"] = metrics.get("C_Neg_sum", 0)
        row["A_Prog_sum"] = metrics.get("A_Prog_sum", 0)
        row["A_Neg_sum"] = metrics.get("A_Neg_sum", 0)
        row["P_Prog_sum"] = metrics.get("P_Prog_sum", 0)
        row["P_Neg_sum"] = metrics.get("P_Neg_sum", 0)
        row["Total_Prog_sum"] = metrics.get("Prog_sum_total", 0)
        row["Total_Neg_sum"] = metrics.get("Neg_sum_total", 0)

        row["Net_Score_Per_Turn"] = round(metrics.get("net_score_per_turn", 0), 2)
        row["Prog_Per_Turn"] = round(metrics.get("Prog_per_turn", 0), 2)
        row["Neg_Per_Turn"] = round(metrics.get("Neg_per_turn", 0), 2)
        row["Tortuosity"] = round(metrics.get("tortuosity", 0), 2)
        row["Avg_Effective_Projection"] = round(metrics.get("avg_effective_projection", 0), 2)

        row["Positive_Energy_Ratio%"] = round(metrics.get("positive_energy_ratio", 0), 1)
        row["Avg_Alignment"] = round(metrics.get("avg_alignment", 0), 3)
        row["Penalty_Rate"] = round(metrics.get("performance_penalty_rate", 0), 2)
        row["Total_Neg_Abs"] = metrics.get("total_neg_abs", 0)
        row["Delta_E_Variance"] = round(metrics.get("delta_E_var", 0), 4)
        row["Max_Negative_Streak"] = metrics.get("max_negative_streak", 0)

        for key in (
            "Idx_RDI", "Idx_Etot", "Idx_Snet",
            "Idx_Rho", "Idx_Sproj", "Idx_Tau",
            "Idx_Rpos", "Idx_Align", "Idx_Pen",
        ):
            row[key] = metrics.get(key, 0)

        if not metrics.get("success"):
            reason = metrics.get("termination_reason", "")
            if "方向崩溃" in reason:
                row["Failure_Type"] = "Direction Collapse"
            elif "停滞" in reason:
                row["Failure_Type"] = "Stagnation"
            elif "持续倒退" in reason:
                row["Failure_Type"] = "Persistent Regression"
            elif "超时" in reason or "MAX_TURNS" in reason:
                row["Failure_Type"] = "Timeout"
            elif "能量不足" in reason:
                row["Failure_Type"] = "Energy Deficit"
            else:
                row["Failure_Type"] = "Other"
        else:
            row["Failure_Type"] = "-"

        rows.append(row)

    df = pd.DataFrame(rows).sort_values("Case_ID")

    # --- EPM-Q composite ---
    idx_keys = [
        "Idx_RDI", "Idx_Etot", "Idx_Snet",
        "Idx_Rho", "Idx_Sproj", "Idx_Tau",
        "Idx_Rpos", "Idx_Align", "Idx_Pen",
    ]
    case_indices = [
        {k: row[k] for k in idx_keys} for _, row in df.iterrows()
    ]
    epmq = compute_composite_scores(case_indices)

    # --- Summary statistics ---
    summary_stats: Dict[str, Any] = {
        "total_cases": len(df),
        "success_count": int((df["Success"] == "Yes").sum()),
        "failure_count": int((df["Success"] == "No").sum()),
        "EPM_Q": epmq,
    }
    summary_stats["success_rate%"] = round(
        summary_stats["success_count"] / max(summary_stats["total_cases"], 1) * 100, 1
    )

    # --- Append descriptive stat rows (mean, std, min, max) ---
    df_out = df.copy()
    numeric_cols = df_out.select_dtypes(include="number").columns.tolist()

    for label, fn in [("Mean", "mean"), ("Std", "std"), ("Min", "min"), ("Max", "max")]:
        stat_row: Dict[str, Any] = {}
        for col in df_out.columns:
            if col in numeric_cols:
                series = df_out[col]
                stat_row[col] = getattr(series, fn)() if fn != "std" else series.std(ddof=1)
            else:
                stat_row[col] = ""
        if "Case_ID" in df_out.columns:
            stat_row["Case_ID"] = label
        df_out = pd.concat([df_out, pd.DataFrame([stat_row])], ignore_index=True)

    df_out = df_out.where(pd.notnull(df_out), "")

    # --- Output ---
    if output_base is None:
        output_base = str(results_dir / "descriptive_statistics")

    saved_files: List[str] = []

    if formats in ("csv", "all"):
        csv_file = f"{output_base}.csv"
        df_out.to_csv(csv_file, index=False, encoding="utf-8-sig")
        saved_files.append(csv_file)
        print(f"✅ CSV: {csv_file}")

    if formats in ("excel", "all"):
        try:
            excel_file = f"{output_base}.xlsx"
            with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
                df_out.to_excel(writer, sheet_name="Detailed Data", index=False)

                epmq_data = {
                    "Metric": ["Outcome Score", "Efficiency Score", "Stability Score", "FINAL EPM INDEX"],
                    "Score": [
                        epmq.get("Outcome_Score", 0),
                        epmq.get("Efficiency_Score", 0),
                        epmq.get("Stability_Score", 0),
                        epmq.get("EPM_Index", 0),
                    ],
                }
                pd.DataFrame(epmq_data).to_excel(writer, sheet_name="EPM-Q Scoreboard", index=False)
            saved_files.append(excel_file)
            print(f"✅ Excel: {excel_file}")
        except ImportError:
            print("⚠️  openpyxl not installed, skipping Excel output. Install with: pip install openpyxl")

    if formats in ("markdown", "all"):
        md_file = f"{output_base}.md"
        _write_markdown(md_file, df_out, summary_stats, results_dir)
        saved_files.append(md_file)
        print(f"✅ Markdown: {md_file}")

    # Terminal output
    print()
    print("=" * 60)
    print(f"🏆 EPM-Index: {epmq.get('EPM_Index', 0):.2f} (baseline: 100.0)")
    print(f"   Outcome:    {epmq.get('Outcome_Score', 0):.2f}")
    print(f"   Efficiency: {epmq.get('Efficiency_Score', 0):.2f}")
    print(f"   Stability:  {epmq.get('Stability_Score', 0):.2f}")
    print(f"   Cases: {summary_stats['success_count']}/{summary_stats['total_cases']} success ({summary_stats['success_rate%']}%)")
    print("=" * 60)

    return summary_stats


def _write_markdown(
    path: str,
    df: "pd.DataFrame",
    stats: Dict[str, Any],
    results_dir: Path,
) -> None:
    epmq = stats.get("EPM_Q", {})
    with open(path, "w", encoding="utf-8") as f:
        f.write("# EPM-Q Evaluation Report\n\n")
        f.write(f"**Results**: `{results_dir.name}`\n\n")

        f.write("## 🏆 EPM-Q Scoreboard\n\n")
        f.write(f"### **EPM-Index: {epmq.get('EPM_Index', 0):.2f}**\n")
        f.write("*(scientific baseline: 100.0)*\n\n")

        f.write("| Dimension (Weight) | Score | Details |\n")
        f.write("| :--- | :--- | :--- |\n")

        det = epmq.get("Details_Outcome", {})
        f.write(f"| **Outcome** ({0.4}) | **{epmq.get('Outcome_Score', 0):.2f}** | "
                f"RDI: {det.get('RDI', 0):.1f} \\| Etot: {det.get('Etot', 0):.1f} \\| Snet: {det.get('Snet', 0):.1f} |\n")

        det = epmq.get("Details_Efficiency", {})
        f.write(f"| **Efficiency** ({0.2}) | **{epmq.get('Efficiency_Score', 0):.2f}** | "
                f"Rho: {det.get('Rho', 0):.1f} \\| Sproj: {det.get('Sproj', 0):.1f} \\| Tau: {det.get('Tau', 0):.1f} |\n")

        det = epmq.get("Details_Stability", {})
        f.write(f"| **Stability** ({0.4}) | **{epmq.get('Stability_Score', 0):.2f}** | "
                f"Rpos: {det.get('Rpos', 0):.1f} \\| Align: {det.get('Align', 0):.1f} \\| Pen: {det.get('Pen', 0):.1f} |\n")

        f.write(f"\n---\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total cases**: {stats['total_cases']}\n")
        f.write(f"- **Success**: {stats['success_count']}\n")
        f.write(f"- **Failure**: {stats['failure_count']}\n")
        f.write(f"- **Success rate**: {stats['success_rate%']}%\n\n")

        core_cols = [
            "Case_ID", "Dominant_Axis", "Difficulty", "Success", "Turns", "Total_Net_Score",
            "Distance_Improvement%", "Energy_Achievement%", "Positive_Energy_Ratio%", "Failure_Type",
        ]
        existing = [c for c in core_cols if c in df.columns]
        f.write(df[existing].to_markdown(index=False))
        f.write("\n\n*Full data available in CSV/Excel files*\n")
