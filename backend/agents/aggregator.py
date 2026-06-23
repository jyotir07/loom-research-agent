"""Aggregator Agent — merges the parallel agent outputs into one dataset."""
from __future__ import annotations

from agents.base import BaseAgent, Context
from models.schemas import ResearchData


class AggregatorAgent(BaseAgent):
    name = "aggregating"

    async def run(self, ctx: Context) -> Context:
        # Structural merge + dedupe. Items are already validated Pydantic models
        # written by the parallel research agents into shared state.
        ctx["research_data"] = ResearchData(
            companies=_dedupe(ctx.get("companies", []), key=lambda c: c.name.lower()),
            funding=ctx.get("funding", []),
            trends=_dedupe(ctx.get("trends", []), key=lambda t: t.title.lower()),
            competitors=_dedupe(
                ctx.get("competitors", []), key=lambda c: c.name.lower()
            ),
        )
        return ctx


def _dedupe(items, key):
    seen, out = set(), []
    for item in items:
        k = key(item)
        if k not in seen:
            seen.add(k)
            out.append(item)
    return out
