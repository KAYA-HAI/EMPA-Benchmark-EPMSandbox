"""
Command-line interface for the EMPA benchmark.

Usage::

    # Run the official 30-case benchmark
    empa run --model openai/gpt-4o

    # Run specific cases
    empa run --model openai/gpt-4o --cases script_003,script_010

    # Run with a custom (local) model
    empa run --model default --base-url http://localhost:8000/v1 --test-api-key EMPTY

    # List available benchmark cases
    empa list-cases
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional

OFFICIAL_30_CASES = [
    "script_003", "script_010", "script_011", "script_020", "script_021",
    "script_029", "script_042", "script_059", "script_063", "script_081",
    "script_095", "script_128", "script_161", "script_195", "script_215",
    "script_222", "script_238", "script_243", "script_262", "script_263",
    "script_269", "script_282", "script_288", "script_304", "script_327",
    "script_349", "script_355", "script_363", "script_366", "script_391",
]

DEFAULT_INFRA_MODEL = "google/gemini-2.5-pro"
DEFAULT_MAX_TURNS = 45
DEFAULT_K = 1
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="empa",
        description="EMPA: A vector-based benchmark for empathic dialogue systems",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )
    sub = parser.add_subparsers(dest="command")

    # --- run ---
    run_p = sub.add_parser("run", help="Run the benchmark")
    run_p.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging",
    )
    run_p.add_argument(
        "--model", required=True,
        help="Model to evaluate (e.g. openai/gpt-4o, google/gemini-2.5-flash)",
    )
    run_p.add_argument(
        "--api-key", default=None,
        help="API key for the infrastructure models (Actor/Judger/Director). "
             "Defaults to OPENROUTER_API_KEY env var.",
    )
    run_p.add_argument(
        "--test-api-key", default=None,
        help="API key for the model under test. Defaults to --api-key if not set.",
    )
    run_p.add_argument(
        "--base-url", default=DEFAULT_BASE_URL,
        help=f"LLM API base URL for infrastructure models (default: {DEFAULT_BASE_URL})",
    )
    run_p.add_argument(
        "--test-base-url", default=None,
        help="API base URL for the model under test. Defaults to --base-url if not set.",
    )
    run_p.add_argument(
        "--cases", default=None,
        help="Comma-separated case IDs. Default: official 30 benchmark cases.",
    )
    run_p.add_argument(
        "--max-turns", type=int, default=DEFAULT_MAX_TURNS,
        help=f"Max dialogue turns per case (default: {DEFAULT_MAX_TURNS})",
    )
    run_p.add_argument(
        "-K", type=int, default=DEFAULT_K,
        help=f"Evaluation interval — assess every K turns (default: {DEFAULT_K})",
    )
    run_p.add_argument(
        "--workers", type=int, default=1,
        help="Number of parallel workers (default: 1)",
    )
    run_p.add_argument(
        "--output-dir", default=None,
        help="Output directory (default: results/benchmark_runs/<model>_<timestamp>)",
    )
    run_p.add_argument(
        "--actor-model", default=DEFAULT_INFRA_MODEL,
        help=f"Model for Actor agent (default: {DEFAULT_INFRA_MODEL})",
    )
    run_p.add_argument(
        "--judger-model", default=DEFAULT_INFRA_MODEL,
        help=f"Model for Judger agent (default: {DEFAULT_INFRA_MODEL})",
    )
    run_p.add_argument(
        "--director-model", default=DEFAULT_INFRA_MODEL,
        help=f"Model for Director agent (default: {DEFAULT_INFRA_MODEL})",
    )

    # --- list-cases ---
    sub.add_parser("list-cases", help="List available benchmark cases")

    # --- evaluate ---
    eval_p = sub.add_parser("evaluate", help="Generate EPM-Q report from results")
    eval_p.add_argument(
        "results_dir", type=str,
        help="Path to benchmark results directory",
    )
    eval_p.add_argument(
        "--format", choices=["csv", "excel", "markdown", "all"], default="all",
        help="Output format (default: all)",
    )
    eval_p.add_argument(
        "--output", default=None,
        help="Output base path (without extension)",
    )

    # --- visualize ---
    viz_p = sub.add_parser("visualize", help="Generate trajectory visualization")
    viz_p.add_argument(
        "results_dir", type=str,
        help="Path to benchmark results directory",
    )
    viz_p.add_argument(
        "--model-name", default=None,
        help="Model name for the plot title (default: inferred from directory)",
    )
    viz_p.add_argument(
        "--output", default=None,
        help="Output image path (default: <results_dir>/multiview_layout.png)",
    )

    # --- compare ---
    cmp_p = sub.add_parser(
        "compare",
        help="Compare multiple models (bar charts, radar grids)",
    )
    cmp_p.add_argument(
        "base_dir", type=str,
        help="Parent directory containing one sub-folder per model",
    )
    cmp_p.add_argument(
        "--models", default=None,
        help=(
            "Comma-separated folder names to include "
            "(default: auto-discover all models in base_dir)"
        ),
    )
    cmp_p.add_argument(
        "--chart", choices=["bars", "radar", "table", "summary", "all"], default="all",
        help="Which output(s) to generate (default: all)",
    )
    cmp_p.add_argument(
        "--radar-type", default=None,
        help=(
            "Comma-separated radar chart ids: categories,mechanism,persona "
            "(default: all three)"
        ),
    )
    cmp_p.add_argument(
        "--output", default=None,
        help="Output directory (default: <base_dir>/comparison/)",
    )

    # --- version ---
    sub.add_parser("version", help="Print version")

    args = parser.parse_args(argv)

    verbose = getattr(args, "verbose", False)
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.command == "version":
        from empa import __version__
        print(f"empa {__version__}")
    elif args.command == "list-cases":
        _cmd_list_cases()
    elif args.command == "run":
        _cmd_run(args)
    elif args.command == "evaluate":
        _cmd_evaluate(args)
    elif args.command == "visualize":
        _cmd_visualize(args)
    elif args.command == "compare":
        _cmd_compare(args)
    else:
        parser.print_help()


def _cmd_evaluate(args: argparse.Namespace) -> None:
    from empa.evaluation.report import generate_report
    generate_report(
        args.results_dir,
        output_base=args.output,
        formats=args.format,
    )


def _cmd_visualize(args: argparse.Namespace) -> None:
    from empa.visualization.trajectory import load_trajectories, plot_multiview

    results_dir = Path(args.results_dir)
    trajectories = load_trajectories(results_dir)
    if not trajectories:
        print(f"Error: no trajectory data found in {results_dir}", file=sys.stderr)
        sys.exit(1)

    model_name = args.model_name
    if not model_name:
        model_name = results_dir.name.replace("_resampled", "").replace("_", " ").title()

    output_path = args.output or str(results_dir / "multiview_layout.png")

    print(f"📊 Generating multiview trajectory for {model_name} ({len(trajectories)} cases)...")
    plot_multiview(trajectories, output_path, model_name)


def _cmd_compare(args: argparse.Namespace) -> None:
    from empa.visualization.comparison import (
        discover_models,
        generate_comparison_table,
        generate_epmq_summary_table,
        plot_errorbar_bars,
        plot_radar_grid,
    )

    base = Path(args.base_dir)
    if not base.is_dir():
        print(f"Error: {base} is not a directory", file=sys.stderr)
        sys.exit(1)

    filter_names = None
    if args.models:
        filter_names = [m.strip() for m in args.models.split(",")]

    models = discover_models(base, filter_names=filter_names)
    if not models:
        print(f"Error: no model results found in {base}", file=sys.stderr)
        sys.exit(1)

    print(f"📊 Found {len(models)} model(s) for comparison:")
    for i, (name, path) in enumerate(models.items(), 1):
        print(f"   [{i}] {name}  ({path.name})")

    output_dir = Path(args.output) if args.output else base / "comparison"

    chart = args.chart
    if chart in ("bars", "all"):
        plot_errorbar_bars(models, output_dir)
    if chart in ("radar", "all"):
        radar_ids = None
        if args.radar_type:
            radar_ids = [r.strip() for r in args.radar_type.split(",")]
        plot_radar_grid(models, output_dir, chart_ids=radar_ids)
    if chart in ("table", "all"):
        generate_comparison_table(models, output_dir)
    if chart in ("summary", "all"):
        generate_epmq_summary_table(models, output_dir)

    print(f"\n✅ Comparison outputs saved to: {output_dir}")


def _cmd_list_cases() -> None:
    print(f"Official benchmark cases ({len(OFFICIAL_30_CASES)}):")
    for c in OFFICIAL_30_CASES:
        print(f"  {c}")


def _cmd_run(args: argparse.Namespace) -> None:
    infra_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
    if not infra_key:
        print(
            "Error: --api-key or OPENROUTER_API_KEY environment variable required.",
            file=sys.stderr,
        )
        sys.exit(1)

    test_key = args.test_api_key or infra_key
    test_base = args.test_base_url or args.base_url

    from empa.llm import OpenAICompatibleClient
    from empa.agents import Actor, Director, Judger, TestModel
    from empa.rubric.empathy_v2.config import EmpathyRubricV2
    from empa.orchestrator.chat_loop import run_chat_loop

    rubric = EmpathyRubricV2()

    if args.cases:
        case_ids = [c.strip() for c in args.cases.split(",")]
    else:
        case_ids = list(OFFICIAL_30_CASES)

    model_short = args.model.split("/")[-1] if "/" in args.model else args.model
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path(f"results/benchmark_runs/{model_short}_{timestamp}")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    # --- Setup log file: tee stdout to both terminal and file ---
    log_file = output_dir / "run.log"

    class TeeStream:
        """Duplicates writes to both the original stream and a log file."""
        def __init__(self, original, filepath):
            self.original = original
            self.log = open(str(filepath), "a", encoding="utf-8", buffering=1)

        def write(self, data):
            self.original.write(data)
            self.log.write(data)

        def flush(self):
            self.original.flush()
            self.log.flush()

    tee = TeeStream(sys.stdout, log_file)
    sys.stdout = tee
    sys.stderr = TeeStream(sys.stderr, log_file)

    print("=" * 70)
    print("🚀 EMPA Benchmark")
    print("=" * 70)
    print()
    print("📋 Configuration:")
    print(f"   Test model: {args.model}")
    print(f"   Test model API: {test_base}")
    print(f"   Infrastructure model: {args.actor_model}")
    print(f"   Max turns: {args.max_turns}")
    print(f"   Evaluation interval K: {args.K}")
    print(f"   Workers: {args.workers}")
    print(f"   Cases: {len(case_ids)}")
    print(f"   案例: {', '.join(case_ids[:5])}{'...' if len(case_ids) > 5 else ''}")
    print()
    print(f"📁 Output: {output_dir}")
    print(f"📝 Log: {log_file}")
    print()
    print("=" * 70)
    print()

    max_consecutive_failures = 5
    consecutive_failures = 0

    def run_single(case_id: str) -> dict:
        from empa.data.loader import load_config
        config = load_config(case_id)

        test_llm = OpenAICompatibleClient(
            args.model, api_key=test_key, base_url=test_base,
        )
        actor_llm = OpenAICompatibleClient(
            args.actor_model, api_key=infra_key, base_url=args.base_url,
        )
        judger_llm = OpenAICompatibleClient(
            args.judger_model, api_key=infra_key, base_url=args.base_url,
        )
        director_llm = OpenAICompatibleClient(
            args.director_model, api_key=infra_key, base_url=args.base_url,
        )

        actor = Actor(actor_llm)
        judger = Judger(judger_llm)
        director = Director(
            director_llm,
            scenario=config["scenario"],
            actor_prompt=config["actor_prompt"],
        )
        test_model = TestModel(
            test_llm,
            system_prompt=rubric.generate_test_model_system_prompt(),
        )

        result = run_chat_loop(
            actor=actor,
            director=director,
            judger=judger,
            test_model=test_model,
            rubric=rubric,
            script_id=case_id,
            max_turns=args.max_turns,
            K=args.K,
            test_model_name=args.model,
        )

        out_path = output_dir / f"{case_id}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)

        tt = result["total_turns"]
        term = result.get("termination_type", "N/A")
        print(f"  [done] {case_id} — {tt} turns, {term}")
        return result

    results: list[dict] = []
    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(run_single, cid): cid for cid in case_ids}
            for fut in as_completed(futures):
                cid = futures[fut]
                try:
                    results.append(fut.result())
                    consecutive_failures = 0
                except Exception as exc:
                    consecutive_failures += 1
                    print(f"  [FAIL] {cid}: {exc}", file=sys.stderr)
                    if consecutive_failures >= max_consecutive_failures:
                        print(f"\n  Aborting: {max_consecutive_failures} consecutive failures.", file=sys.stderr)
                        break
    else:
        for cid in case_ids:
            try:
                results.append(run_single(cid))
                consecutive_failures = 0
            except Exception as exc:
                consecutive_failures += 1
                print(f"  [FAIL] {cid}: {exc}", file=sys.stderr)
                if consecutive_failures >= max_consecutive_failures:
                    print(f"\n  Aborting: {max_consecutive_failures} consecutive failures.", file=sys.stderr)
                    break

    # Write summary
    avg_turns = sum(r["total_turns"] for r in results) / max(len(results), 1)
    summary = {
        "model": args.model,
        "infra_model": args.actor_model,
        "K": args.K,
        "max_turns": args.max_turns,
        "total_cases": len(case_ids),
        "completed": len(results),
        "failed": len(case_ids) - len(results),
        "avg_turns": round(avg_turns, 1),
        "results": [
            {
                "script_id": r["script_id"],
                "turns": r["total_turns"],
                "termination": r.get("termination_type", "N/A"),
            }
            for r in results
        ],
    }
    with open(output_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print()
    print("=" * 70)
    print(f"✅ Completed: {summary['completed']}/{summary['total_cases']} cases")
    print(f"   Avg turns: {summary['avg_turns']}")
    print(f"   Failed: {summary['failed']}")
    print(f"📁 Results: {output_dir}")
    print(f"📝 Full log: {log_file}")
    print("=" * 70)


if __name__ == "__main__":
    main()
