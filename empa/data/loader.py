"""
Data loader for benchmark cases and precomputed results.

Handles loading actor prompts (script_XXX.md), scenario configurations
(character_stories.json), and precomputed IEDR results.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA_DIR = Path(__file__).parent


def get_data_dir() -> Path:
    """Return the path to the built-in data directory."""
    return _DATA_DIR


def load_official_cases() -> List[str]:
    """Return the official 30 benchmark case IDs shipped with the package."""
    official = _DATA_DIR / "official_cases.txt"
    if official.exists():
        return [line.strip() for line in official.read_text().splitlines() if line.strip()]
    return []


def load_case_ids(case_file: str | Path | None = None) -> List[str]:
    """
    Load benchmark case IDs from a text file (one ID per line).

    If no file is given, returns the official 30 benchmark cases.
    Falls back to scanning the cases directory if no official list exists.
    """
    if case_file is not None:
        path = Path(case_file)
        return [line.strip() for line in path.read_text().splitlines() if line.strip()]

    official = load_official_cases()
    if official:
        return official

    cases_dir = _DATA_DIR / "cases"
    if not cases_dir.exists():
        return []
    return sorted(
        p.stem for p in cases_dir.glob("script_*.md")
    )


def load_actor_prompt(script_id: str, cases_dir: str | Path | None = None) -> str:
    """Load the actor prompt markdown for a given script ID."""
    base = Path(cases_dir) if cases_dir else _DATA_DIR / "cases"
    path = base / f"{script_id}.md"
    if not path.exists():
        raise FileNotFoundError(f"Actor prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def load_scenario(script_id: str, scenarios_file: str | Path | None = None) -> Dict[str, Any]:
    """Load the scenario configuration for a given script ID."""
    path = Path(scenarios_file) if scenarios_file else _DATA_DIR / "scenarios" / "character_stories.json"
    if not path.exists():
        raise FileNotFoundError(f"Scenarios file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        all_scenarios = json.load(f)

    for scenario in all_scenarios:
        if scenario.get("剧本编号") == script_id:
            return scenario

    raise KeyError(f"Scenario not found for script_id: {script_id}")


def load_config(script_id: str, data_dir: str | Path | None = None) -> Dict[str, Any]:
    """
    Load full configuration for a benchmark case.

    Returns a dict with ``actor_prompt`` and ``scenario``.
    """
    base = Path(data_dir) if data_dir else _DATA_DIR
    actor_prompt = load_actor_prompt(script_id, base / "cases")
    scenario = load_scenario(script_id, base / "scenarios" / "character_stories.json")
    return {"actor_prompt": actor_prompt, "scenario": scenario}


def list_benchmark_cases(case_file: str | Path | None = None) -> List[str]:
    """Convenience alias for :func:`load_case_ids`."""
    return load_case_ids(case_file)


def load_precomputed_iedr(
    script_id: str, precomputed_file: str | Path | None = None
) -> Optional[Dict[str, Any]]:
    """
    Load precomputed IEDR data for a given script ID.

    Returns None if no precomputed data is available.
    """
    path = (
        Path(precomputed_file)
        if precomputed_file
        else _DATA_DIR / "precomputed" / "iedr_batch_results.json"
    )
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data.get(script_id)
    if isinstance(data, list):
        for item in data:
            if item.get("script_id") == script_id:
                return item
    return None
