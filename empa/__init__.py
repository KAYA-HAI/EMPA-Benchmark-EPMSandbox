"""
EMPA: A Vector-Based Evaluation Framework for Empathic Dialogue Systems

EMPA provides a generic, extensible framework for evaluating dialogue
systems through vector-space progress tracking and energy dynamics. The
framework separates the evaluation *engine* (vector math, energy physics,
orchestration) from the evaluation *rubric* (scoring keys, prompt templates,
dimension definitions), allowing researchers to plug in custom rubrics for
any dialogue evaluation task.

Quick start (CLI)::

    pip install .
    export OPENROUTER_API_KEY="sk-or-..."
    empa run --model openai/gpt-4o

Architecture overview:

- **core**: Generic vector engine, energy dynamics, and scoring engine.
  Dimension-agnostic — works with any N-dimensional rubric.
- **rubric**: Abstract ``RubricConfig`` interface and official rubrics
  (e.g. ``empathy_v2``). A rubric defines dimensions, scoring keys,
  prompt templates, and termination parameters.
- **agents**: Actor, Director, Judger, and TestModel abstractions.
- **orchestrator**: Chat loop and EPJ state management.
- **llm**: LLM provider adapters (OpenAI-compatible, Volcengine, etc.).
- **evaluation**: Post-run metrics (EPM-Q index, descriptive statistics).
- **visualization**: Trajectory plots, radar charts, outcome summaries.
"""

__version__ = "0.1.0"
