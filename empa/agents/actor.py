"""
Actor agent — plays the role of the user seeking empathy.

The Actor receives a system prompt (character profile) and optional
Director guidance each turn, then generates an in-character reply.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from empa.agents.base import BaseAgent
from empa.llm.base import LLMClient, Message

logger = logging.getLogger(__name__)


class Actor(BaseAgent):
    """Concrete Actor that drives the dialogue from the seeker's perspective."""

    def __init__(self, llm: LLMClient, *, thinking_budget: int = 128) -> None:
        self._llm = llm
        self._thinking_budget = thinking_budget
        self._system_prompt: Optional[str] = None

    def set_system_prompt(self, prompt: str) -> None:
        self._system_prompt = prompt
        logger.info("Actor system prompt set (%d chars)", len(prompt))

    def generate_reply(
        self,
        history: List[Dict[str, str]],
        *,
        director_guidance: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        if not self._system_prompt:
            raise RuntimeError("Actor system prompt not set. Call set_system_prompt() first.")

        user_prompt = self._build_user_prompt(history, director_guidance)

        extra: Dict[str, Any] = {}
        if "gemini-2.5" in self._llm.name.lower():
            extra["extra_body"] = {
                "google": {
                    "thinking_config": {
                        "thinking_budget_tokens": self._thinking_budget
                    }
                }
            }

        resp = self._llm.complete(
            [
                Message(role="system", content=self._system_prompt),
                Message(role="user", content=user_prompt),
            ],
            max_tokens=2500,
            extra_params=extra if extra else None,
        )
        return resp.content or ""

    # ------------------------------------------------------------------

    def _build_user_prompt(
        self,
        history: List[Dict[str, str]],
        guidance: Optional[str],
    ) -> str:
        if not history:
            formatted = "（对话刚开始，这是你的第一句话）"
        else:
            lines = []
            for i, msg in enumerate(history, 1):
                role = "你自己" if msg["role"] == "actor" else "网友"
                lines.append(f"{i}. {role}: {msg['content']}")
            formatted = "\n".join(lines)

        has_new_content = False
        guidance_section = ""
        if guidance and guidance.strip():
            has_new_content = any(
                kw in guidance for kw in ("阶段", "剧情内容", "回忆", "记忆", "经历")
            )
            label = "导演指导（包含新剧情/回忆）" if has_new_content else "导演指导"
            guidance_section = f"\n## {label}\n\n{guidance}\n"

        if has_new_content:
            content_req = (
                "**要求**：充分展开导演提供的新剧情/回忆内容（至少60-100字），"
                "详细描述具体场景、细节和情绪，不要只是提及。"
            )
        else:
            content_req = "**要求**：保持简洁自然（20-50字），推进对话，不要重复。"

        return (
            f"## 对话历史\n\n{formatted}\n"
            f"{guidance_section}\n"
            f"{content_req}\n\n"
            "## 防重复铁律\n"
            "- 不得重复之前任何轮次的话、例子、描述\n"
            "- 每一轮都必须引入新的信息、角度或情绪层次\n\n"
            "## 现在生成你的回复：\n"
        )
