"""
Function-calling tool definitions for the Director agent.

These schemas tell the LLM which actions the Director can take
during the dialogue loop (release story fragments, adjust strategy, etc.).
"""

from __future__ import annotations

from typing import Any, Dict, List

DIRECTOR_FUNCTIONS: List[Dict[str, Any]] = [
    {
        "name": "select_and_reveal_fragment",
        "description": (
            "Release a pre-authored story fragment to the Actor. "
            "The same fragment may be released more than once if "
            "the actor_guidance provides a fresh interpretation angle."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "stage_index": {
                    "type": "integer",
                    "description": "Index of the story stage to reveal (0-based).",
                    "minimum": 0,
                },
                "reason": {
                    "type": "string",
                    "description": "Why this stage should be released now.",
                },
                "actor_guidance": {
                    "type": "string",
                    "description": (
                        "Specific acting guidance for the Actor (in-character perspective only). "
                        "When re-releasing a stage, supply a novel angle."
                    ),
                },
            },
            "required": ["stage_index", "reason"],
        },
    },
    {
        "name": "observe_and_wait",
        "description": "Do not intervene; continue observing.",
        "parameters": {
            "type": "object",
            "properties": {
                "observation": {
                    "type": "string",
                    "description": "Current observation of the conversation state.",
                },
                "wait_reason": {
                    "type": "string",
                    "description": "Why intervention is not needed yet.",
                },
            },
            "required": ["observation", "wait_reason"],
        },
    },
    {
        "name": "continue_without_new_info",
        "description": "Provide acting advice without releasing new information.",
        "parameters": {
            "type": "object",
            "properties": {
                "focus_suggestion": {
                    "type": "string",
                    "description": "What the Actor should focus on.",
                },
                "reason": {"type": "string", "description": "Decision rationale."},
            },
            "required": ["focus_suggestion", "reason"],
        },
    },
    {
        "name": "reveal_memory",
        "description": (
            "Release a memory fragment from the character's backstory. "
            "Available periods: childhood, adolescence, young adulthood, current."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "memory_period": {
                    "type": "string",
                    "enum": ["童年经历", "少年经历", "青年经历", "角色现状"],
                    "description": "Which life period to release.",
                },
                "reason": {"type": "string", "description": "Decision rationale."},
            },
            "required": ["memory_period", "reason"],
        },
    },
    {
        "name": "adjust_empathy_strategy",
        "description": (
            "Adjust the Actor's empathy expression strategy. "
            "The actor_guidance should leverage the character's background "
            "to provide concrete, information-rich direction."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "focus_aspect": {
                    "type": "string",
                    "enum": ["动机共情", "情感共情", "认知共情"],
                    "description": "Which empathy dimension to focus on.",
                },
                "reason": {
                    "type": "string",
                    "description": "Internal analysis (may reference EPJ vectors).",
                },
                "actor_guidance": {
                    "type": "string",
                    "description": (
                        "Guidance for the Actor (character perspective only, "
                        "no technical jargon). Should reference character backstory."
                    ),
                },
            },
            "required": ["focus_aspect", "reason", "actor_guidance"],
        },
    },
    {
        "name": "introduce_turning_point",
        "description": (
            "Introduce a turning point combining plot progression and strategy shift. "
            "Use when simultaneous story release and strategy adjustment are needed."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "stage_index": {
                    "type": "integer",
                    "description": "Story stage index (-1 for no plot release).",
                    "minimum": -1,
                },
                "empathy_aspect": {
                    "type": "string",
                    "enum": ["动机共情", "情感共情", "认知共情", ""],
                    "description": "Empathy dimension to focus on (empty = none).",
                },
                "reason": {"type": "string", "description": "Internal rationale."},
                "actor_guidance": {
                    "type": "string",
                    "description": "Guidance for the Actor (character perspective).",
                },
            },
            "required": ["stage_index", "empathy_aspect", "reason"],
        },
    },
    {
        "name": "end_conversation",
        "description": (
            "End the conversation. Only permitted when EPM victory conditions "
            "(spatial improvement AND energy sufficiency) are both met."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Must specify which EPM conditions are satisfied.",
                },
            },
            "required": ["reason"],
        },
    },
]


def get_director_tools() -> List[Dict[str, Any]]:
    """Return Director functions in OpenAI tool-call format."""
    return [{"type": "function", "function": f} for f in DIRECTOR_FUNCTIONS]
