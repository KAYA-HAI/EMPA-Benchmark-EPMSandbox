"""
Abstract LLM client interface.

All LLM adapters must implement :meth:`complete`.  The orchestrator and agents
communicate with LLMs exclusively through this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    role: str
    content: str


@dataclass
class ToolCall:
    """A single function invocation requested by the model."""

    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Structured response from an LLM completion call.

    ``content`` is the text reply (may be ``None`` for pure tool-call responses).
    ``tool_calls`` contains any function invocations the model requested.
    """

    content: Optional[str] = None
    tool_calls: List[ToolCall] = field(default_factory=list)
    finish_reason: str = "stop"
    raw: Any = None


class LLMClient(ABC):
    """Abstract base for all LLM provider adapters."""

    @abstractmethod
    def complete(
        self,
        messages: List[Message],
        *,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        response_format: Dict[str, Any] | None = None,
        tools: List[Dict[str, Any]] | None = None,
        extra_params: Dict[str, Any] | None = None,
    ) -> LLMResponse:
        """
        Send messages and return a structured :class:`LLMResponse`.

        Args:
            messages: Conversation history.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in the response.
            response_format: E.g. ``{"type": "json_object"}``.
            tools: OpenAI-format function/tool definitions.
            extra_params: Provider-specific overrides (thinking budget, etc.).
        """
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Return a human-readable model identifier."""
        ...
