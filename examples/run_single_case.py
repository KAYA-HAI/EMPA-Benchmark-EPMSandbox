#!/usr/bin/env python3
"""
Example: Run EMPA on a single benchmark case.

Usage::

    export OPENROUTER_API_KEY="sk-or-..."
    python examples/run_single_case.py --model openai/gpt-4o --case script_003
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from empa.llm import OpenAICompatibleClient
from empa.agents import Actor, Director, Judger, TestModel
from empa.rubric.empathy_v2.config import EmpathyRubricV2
from empa.data.loader import load_config
from empa.orchestrator.chat_loop import run_chat_loop


def main():
    parser = argparse.ArgumentParser(description="Run EMPA on a single case")
    parser.add_argument("--model", required=True, help="Model to evaluate")
    parser.add_argument("--case", default="script_003", help="Case ID")
    parser.add_argument("--api-key", default=None)
    parser.add_argument("--base-url", default="https://openrouter.ai/api/v1")
    parser.add_argument("--max-turns", type=int, default=45)
    parser.add_argument("-K", type=int, default=1)
    args = parser.parse_args()

    api_key = args.api_key or os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: set OPENROUTER_API_KEY or pass --api-key")
        sys.exit(1)

    rubric = EmpathyRubricV2()
    config = load_config(args.case)

    test_llm = OpenAICompatibleClient(args.model, api_key=api_key, base_url=args.base_url)
    actor_llm = OpenAICompatibleClient("google/gemini-2.5-pro", api_key=api_key, base_url=args.base_url)
    judger_llm = OpenAICompatibleClient("google/gemini-2.5-pro", api_key=api_key, base_url=args.base_url)
    director_llm = OpenAICompatibleClient("google/gemini-2.5-pro", api_key=api_key, base_url=args.base_url)

    actor = Actor(actor_llm)
    judger = Judger(judger_llm)
    director = Director(director_llm, scenario=config["scenario"], actor_prompt=config["actor_prompt"])
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
        script_id=args.case,
        max_turns=args.max_turns,
        K=args.K,
        test_model_name=args.model,
    )

    out_file = f"result_{args.case}_{args.model.replace('/', '_')}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)

    print(f"\nResult saved to {out_file}")
    print(f"  Turns: {result['total_turns']}")
    print(f"  Termination: {result['termination_type']}")
    print(f"  P_0: {result['epj']['P_0_initial_deficit']}")
    print(f"  P_final: {result['epj']['P_final_position']}")


if __name__ == "__main__":
    main()
