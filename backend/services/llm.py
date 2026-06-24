"""Thin wrapper around Loom — the project's single LLM inference layer.

Every agent calls the LLM through here, so all provider/model routing, caching,
retries, and cost tracking live in one place. Loom (`pip install loom-router`)
is a provider-abstraction layer; orchestration (agents, parallelism, state) is
our own code on top of it.

Two Loom features are showcased here:
  * Router  — cheap-first model selection with a validator (escalate only if the
              cheap model's output is too thin / fails validation).
  * Cost    — every Loom response carries usage + cost; we accumulate it per job
              via a contextvar so the parallel agents roll up into one total.
"""
from __future__ import annotations

import contextvars
import json
from dataclasses import dataclass, field
from typing import Any

from loom import AsyncLoom, Router

# Initialized once; reads provider API keys from the environment.
_client = AsyncLoom.from_env()

# Cheap-first router: try the cheap model, escalate only if validation fails.
# Both candidates are OpenAI so failover works with just OPENAI_API_KEY. Add
# cross-provider failover by appending e.g. ("anthropic", "text",
# "claude-haiku-4-5") or ("gemini", "text", "gemini-1.5-flash") once those keys
# are set — no other code changes needed.
default_router = Router(
    candidates=[
        ("openai", "text", "gpt-4o-mini"),
        ("openai", "text", "gpt-4o"),
    ],
    validator=lambda r: len(r.get("text", "").strip()) > 40,
)


# --------------------------------------------------------------------------- #
# Per-job cost / usage tracking
# --------------------------------------------------------------------------- #
@dataclass
class CallRecord:
    provider: str
    model: str
    cost_usd: float
    input_tokens: int
    output_tokens: int


@dataclass
class CostTracker:
    calls: list[CallRecord] = field(default_factory=list)

    @property
    def total_usd(self) -> float:
        return sum(c.cost_usd for c in self.calls)

    @property
    def total_tokens(self) -> int:
        return sum(c.input_tokens + c.output_tokens for c in self.calls)

    def by_model(self) -> dict[str, float]:
        out: dict[str, float] = {}
        for c in self.calls:
            key = f"{c.provider}/{c.model}"
            out[key] = out.get(key, 0.0) + c.cost_usd
        return out

    def summary(self) -> dict[str, Any]:
        return {
            "total_usd": round(self.total_usd, 6),
            "total_tokens": self.total_tokens,
            "calls": len(self.calls),
            "by_model": {k: round(v, 6) for k, v in self.by_model().items()},
        }


# Shared by reference across asyncio.gather child tasks (they copy the context
# mapping but the CostTracker object itself is shared), so parallel agents all
# append to the same tracker.
_tracker: contextvars.ContextVar[CostTracker | None] = contextvars.ContextVar(
    "loom_cost_tracker", default=None
)


def start_tracking() -> CostTracker:
    """Begin a fresh cost accumulation for the current job; returns the tracker."""
    tracker = CostTracker()
    _tracker.set(tracker)
    return tracker


def get_tracker() -> CostTracker | None:
    return _tracker.get()


def _record(result: dict[str, Any]) -> None:
    tracker = _tracker.get()
    if tracker is None:
        return
    usage = result.get("usage") or {}
    cost = result.get("cost") or {}
    tracker.calls.append(
        CallRecord(
            provider=result.get("provider", ""),
            model=result.get("model", ""),
            cost_usd=float(cost.get("usd") or 0.0),
            input_tokens=int(usage.get("input_tokens") or 0),
            output_tokens=int(usage.get("output_tokens") or 0),
        )
    )


# --------------------------------------------------------------------------- #
# Public API used by agents
# --------------------------------------------------------------------------- #
async def complete(prompt: str, *, params: dict[str, Any] | None = None) -> str:
    """Run a completion through the cheap-first Router and return the text.

    Cost/usage from the chosen candidate is recorded on the active tracker.
    """
    result = await _client.route(default_router, prompt=prompt, params=params or {})
    _record(result)
    return result["text"]


async def complete_json(prompt: str, *, params: dict[str, Any] | None = None) -> Any:
    """Like `complete`, but parse the result as JSON (tolerates ```json fences)."""
    text = await complete(prompt, params=params)
    return _parse_json(text)


def strip_code_fence(text: str) -> str:
    """Remove a wrapping ```lang ... ``` fence if the whole text is fenced.

    Models often wrap a full Markdown report in ```markdown ... ```, which would
    otherwise render as one literal code block. Inner fences are left intact.
    """
    stripped = text.strip()
    if not stripped.startswith("```"):
        return text
    lines = stripped.splitlines()
    lines = lines[1:]  # drop opening fence (``` or ```markdown)
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]  # drop closing fence
    return "\n".join(lines).strip()


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
