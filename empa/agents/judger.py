"""
Judger agent — fills psychometric rating forms via LLM.

In the EMPA architecture the Judger acts as a **sensor**: it translates
qualitative dialogue observations into structured numeric ratings that the
scoring engine can process.  The Judger never makes termination decisions.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, Dict, List, Optional

from empa.agents.base import BaseJudger
from empa.llm.base import LLMClient, Message

logger = logging.getLogger(__name__)


class Judger(BaseJudger):
    """Concrete Judger backed by an LLM."""

    def __init__(self, llm: LLMClient, *, max_retries: int = 3) -> None:
        self._llm = llm
        self._max_retries = max_retries

    # ------------------------------------------------------------------
    # BaseJudger interface
    # ------------------------------------------------------------------

    def fill_initial_assessment(
        self, script_content: Dict[str, Any]
    ) -> Dict[str, int]:
        """Fill the IEDR form at T=0."""
        from empa.rubric.empathy_v2.iedr_prompt import generate_iedr_prompt

        prompt = generate_iedr_prompt(script_content)
        logger.info("[Judger] T=0: filling IEDR")

        resp = self._llm.complete(
            [Message(role="user", content=prompt)],
            max_tokens=8000,
            response_format={"type": "json_object"},
        )

        raw = self._parse_json(resp.content or "")
        return self._convert_iedr(raw)

    def fill_progress_form(
        self,
        recent_turns: list,
        script_context: Optional[Dict[str, Any]] = None,
        full_history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """Fill the MDEP-PR form every K turns."""
        from empa.rubric.empathy_v2.mdep_prompt import generate_mdep_pr_prompt

        prompt = generate_mdep_pr_prompt(recent_turns, script_context, full_history)

        print(f"═══ [Judger/传感器] T>0: 填写 MDEP-PR 量表 ═══")
        print(f"   评估轮次: 最近 {len(recent_turns)} 轮")

        last_err: Optional[str] = None
        for attempt in range(self._max_retries):
            if attempt > 0:
                logger.warning("[Judger] retry %d/%d", attempt, self._max_retries)
                time.sleep(2)
            try:
                resp = self._llm.complete(
                    [Message(role="user", content=prompt)],
                    max_tokens=6000,
                    response_format={"type": "json_object"},
                )
                if not resp.content:
                    last_err = "empty response"
                    continue

                print(f"📊 [Judger] 收到响应（前100字符）: {resp.content[:100]}...")
                print(f"📊 [Judger] 响应总长度: {len(resp.content)} 字符")

                raw = self._parse_json(resp.content)
                print(f"✅ [Judger] JSON解析成功（直接解析）")

                result = self._convert_mdep(raw)
                result["detailed_analysis"] = raw
                logger.info(
                    "[Judger] MDEP-PR: C(%+d/%+d) A(%+d/%+d) P(%+d/%+d)",
                    result.get("C.Prog", 0), result.get("C.Neg", 0),
                    result.get("A.Prog", 0), result.get("A.Neg", 0),
                    result.get("P.Prog", 0), result.get("P.Neg", 0),
                )
                return result
            except Exception as exc:
                last_err = str(exc)

        logger.error("[Judger] MDEP-PR failed after %d retries: %s", self._max_retries, last_err)
        return {
            "C.Prog": 0, "C.Neg": 0,
            "A.Prog": 0, "A.Neg": 0,
            "P.Prog": 0, "P.Neg": 0,
            "reasoning": f"Judger failed ({last_err}), using defaults",
        }

    # ------------------------------------------------------------------
    # JSON parsing helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_json(text: str) -> dict:
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
            if match:
                return json.loads(match.group(1).strip())
            raise ValueError("Cannot extract JSON from Judger response")

    @staticmethod
    def _convert_iedr(raw: dict) -> Dict[str, int]:
        indicators = [
            "C.1", "C.2", "C.3",
            "A.1", "A.2", "A.3",
            "P.1", "P.2", "P.3",
        ]
        result: Dict[str, int] = {}
        for ind in indicators:
            level_key = f"{ind}_level"
            result[ind] = raw.get(level_key, raw.get(ind, 1))
        return result

    @staticmethod
    def _convert_mdep(raw: dict) -> Dict[str, Any]:
        if "C_Prog_level" in raw:
            return {
                "C.Prog": raw.get("C_Prog_level", 0),
                "C.Neg": raw.get("C_Neg_level", 0),
                "A.Prog": raw.get("A_Prog_level", 0),
                "A.Neg": raw.get("A_Neg_level", 0),
                "P.Prog": raw.get("P_Prog_level", 0),
                "P.Neg": raw.get("P_Neg_level", 0),
            }
        return raw
