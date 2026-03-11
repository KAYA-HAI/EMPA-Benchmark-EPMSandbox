"""
Abstract base classes for dialogue agents.

All concrete agent implementations inherit from these bases, ensuring a
uniform interface that the orchestrator can depend on.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAgent(ABC):
    """Common interface shared by all agents."""

    @abstractmethod
    def generate_reply(self, history: List[Dict[str, str]], **kwargs: Any) -> str:
        """Generate a reply given the conversation history."""
        ...


class BaseJudger(ABC):
    """Interface for the evaluation judge."""

    @abstractmethod
    def fill_initial_assessment(
        self, script_content: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Fill the initial assessment form (e.g. IEDR).

        Returns a dict mapping indicator IDs to selected levels.
        """
        ...

    @abstractmethod
    def fill_progress_form(
        self,
        recent_turns: list,
        script_context: Optional[Dict[str, Any]] = None,
        full_history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        Fill the progress form (e.g. MDEP-PR).

        Returns a dict mapping indicator IDs to selected levels,
        plus optional ``detailed_analysis`` and ``reasoning`` fields.
        """
        ...
