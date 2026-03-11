"""
TestModel agent — wraps the model under evaluation.

The TestModel receives the dialogue history (from the perspective of an
AI assistant) and produces a reply.  This is the component that gets
*scored* by the EMPA benchmark.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List

from empa.agents.base import BaseAgent
from empa.llm.base import LLMClient, Message

logger = logging.getLogger(__name__)

_USER_PROMPT_TEMPLATE = """# 对话历史

{history}

---

**重要**：
- 以上是对话历史，仅供你参考理解上下文
- 你现在需要做的是：根据用户最新的消息，生成你的下一句回复
- 只输出你的回复内容，不要重复对话历史
- 不要在回复前加"你（启明）："或任何前缀，直接说话即可

现在请生成你的共情回复：
"""


class TestModel(BaseAgent):
    """Generic wrapper for any model being benchmarked."""

    def __init__(
        self,
        llm: LLMClient,
        *,
        system_prompt: str | None = None,
    ) -> None:
        self._llm = llm
        self._system_prompt = system_prompt

    def generate_reply(
        self,
        history: List[Dict[str, str]],
        **kwargs: Any,
    ) -> str:
        messages: List[Message] = []

        if self._system_prompt:
            messages.append(Message(role="system", content=self._system_prompt))

        user_prompt = self._format_history(history)
        messages.append(Message(role="user", content=user_prompt))

        resp = self._llm.complete(messages, max_tokens=2500)
        return resp.content or ""

    @staticmethod
    def _format_history(history: List[Dict[str, str]]) -> str:
        lines: list[str] = []
        for msg in history:
            role = msg["role"]
            if role == "actor":
                lines.append(f"用户: {msg['content']}")
            elif role == "test_model":
                lines.append(f"启明: {msg['content']}")

        formatted = "\n".join(lines) if lines else "（对话尚未开始）"
        return _USER_PROMPT_TEMPLATE.format(history=formatted)
