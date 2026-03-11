"""
OpenAI-compatible LLM adapter.

Works with OpenAI, OpenRouter, vLLM, SGLang, and any provider that
exposes an ``/v1/chat/completions`` endpoint.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from empa.llm.base import LLMClient, LLMResponse, Message, ToolCall

logger = logging.getLogger(__name__)


class OpenAICompatibleClient(LLMClient):
    """Thin wrapper around the ``openai`` Python SDK."""

    def __init__(
        self,
        model: str,
        *,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        timeout: float = 120.0,
        max_retries: int = 2,
        default_headers: Dict[str, str] | None = None,
    ) -> None:
        from openai import OpenAI

        self._model = model
        self._client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers or {},
        )

    @property
    def name(self) -> str:
        return self._model

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
        api_messages = [{"role": m.role, "content": m.content} for m in messages]

        params: Dict[str, Any] = {
            "model": self._model,
            "messages": api_messages,
            "temperature": temperature,
            "frequency_penalty": 0.7,
            "presence_penalty": 0.7,
        }
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        if response_format is not None:
            params["response_format"] = response_format
        if tools is not None:
            params["tools"] = tools
        if extra_params:
            params.update(extra_params)

        print(f"--- [API层] 正在通过 OpenRouter 向模型 '{self._model}' 发送请求... ---")
        if tools:
            print(f"--- [API层] 启用Function Calling，可用函数数量: {len(tools)} ---")

        raw = self._client.chat.completions.create(**params)
        msg = raw.choices[0].message
        finish = raw.choices[0].finish_reason

        tool_calls: List[ToolCall] = []
        if msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"--- [API层] LLM调用了函数：{tc.function.name} ---")
                tool_calls.append(
                    ToolCall(
                        name=tc.function.name,
                        arguments=json.loads(tc.function.arguments),
                    )
                )
        else:
            print(f"--- [API层] 成功接收完整响应 ---")

        return LLMResponse(
            content=msg.content if msg.content else None,
            tool_calls=tool_calls,
            finish_reason=finish or "stop",
            raw=raw,
        )
