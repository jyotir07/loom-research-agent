"""Thin wrapper around Loom — the project's single LLM inference layer.

Every agent calls the LLM through here, so all provider/model routing, caching,
retries, and cost tracking live in one place. Loom (`pip install loom-router`)
is a provider-abstraction layer; orchestration (agents, parallelism, state) is
our own code on top of it.
"""
from __future__ import annotations

import json
from typing import Any

from loom import AsyncLoom, Router

from config import settings

# Initialized once; reads provider API keys from the environment.
_client = AsyncLoom.from_env()

async def complete(
    prompt: str,
    *,
    provider: str | None = None,
    model: str | None = None,
    params: dict[str, Any] | None = None,
) -> str:
    """Run a single completion and return the text."""
    result = await _client.generate(
        provider=provider or settings.llm_provider,
        modality="text",
        model=model or settings.llm_model,
        prompt=prompt,
        params=params or {},
    )
    return result["text"]


async def complete_json(
    prompt: str,
    *,
    provider: str | None = None,
    model: str | None = None,
    params: dict[str, Any] | None = None,
) -> Any:
    """Run a completion expected to return JSON and parse it.

    Tolerates fenced ```json blocks. Raises ValueError if unparseable.
    """
    text = await complete(prompt, provider=provider, model=model, params=params)
    return _parse_json(text)


# A cheap-first router with validation, demonstrating Loom's model fallback.
# Used where a task can run on a cheaper model but should fail over if the
# output is too thin. Wire into agents as needed.
default_router = Router(
    candidates=[
        ("openai", "text", "gpt-4o-mini"),
        ("anthropic", "text", "claude-haiku-4-5"),
    ],
    validator=lambda r: len(r.get("text", "")) > 40,
)


async def route(prompt: str, *, params: dict[str, Any] | None = None) -> str:
    """Run a prompt through the cheap-first router."""
    result = await _client.route(default_router, prompt=prompt, params=params or {})
    return result["text"]


def _parse_json(text: str) -> Any:
    text = text.strip()
    if text.startswith("```"):
        # strip ```json ... ``` fences
        text = text.split("```", 2)[1]
        if text.lstrip().lower().startswith("json"):
            text = text.lstrip()[4:]
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"LLM did not return valid JSON: {exc}\n---\n{text[:500]}")
