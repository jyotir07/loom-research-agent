"""Research workflow orchestrator.

This is the heart of the app's orchestration layer (built by us, not Loom):

    Planner -> [Company | Funding | Trends | Competitor]  (parallel)
            -> Aggregator -> Writer -> Report

Progress is emitted via an async callback so the API can stream it over SSE.
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable

from agents import (
    AggregatorAgent,
    CompanyAgent,
    CompetitorAgent,
    FundingAgent,
    PlannerAgent,
    TrendsAgent,
    WriterAgent,
)
from agents.base import BaseAgent, Context
from models.schemas import ProgressEvent, Report, StageStatus

ProgressCallback = Callable[[ProgressEvent], Awaitable[None]]

# Agents that fan out concurrently after planning.
RESEARCH_AGENTS: list[BaseAgent] = [
    CompanyAgent(),
    FundingAgent(),
    TrendsAgent(),
    CompetitorAgent(),
]


async def run_research(
    job_id: str,
    topic: str,
    on_progress: ProgressCallback | None = None,
) -> Report:
    """Execute the full pipeline and return the final Report."""
    ctx: Context = {"topic": topic}

    async def emit(stage: str, status: StageStatus, message: str | None = None) -> None:
        if on_progress is not None:
            await on_progress(
                ProgressEvent(job_id=job_id, stage=stage, status=status, message=message)
            )

    # 1. Plan
    await _stage(emit, PlannerAgent(), ctx)

    # 2. Parallel research fan-out
    await asyncio.gather(*(_stage(emit, a, ctx) for a in RESEARCH_AGENTS))

    # 3. Aggregate -> 4. Write
    await _stage(emit, AggregatorAgent(), ctx)
    await _stage(emit, WriterAgent(), ctx)

    return ctx["report"]


async def _stage(emit, agent: BaseAgent, ctx: Context) -> None:
    """Run one agent with progress + error reporting around it."""
    await emit(agent.name, StageStatus.RUNNING)
    try:
        await agent.run(ctx)
    except Exception as exc:  # noqa: BLE001 - surface failure to the UI
        await emit(agent.name, StageStatus.ERROR, str(exc))
        raise
    await emit(agent.name, StageStatus.DONE)
