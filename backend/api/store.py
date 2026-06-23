"""In-memory job store + per-job progress queues.

Skeleton-grade: swap for Postgres/Redis later (see config.database_url). Holds
jobs and an asyncio.Queue per job that the SSE endpoint drains.
"""
from __future__ import annotations

import asyncio

from models.schemas import ProgressEvent, ResearchJob

_jobs: dict[str, ResearchJob] = {}
_queues: dict[str, asyncio.Queue[ProgressEvent | None]] = {}


def create_job(topic: str) -> ResearchJob:
    job = ResearchJob(topic=topic)
    _jobs[job.job_id] = job
    _queues[job.job_id] = asyncio.Queue()
    return job


def get_job(job_id: str) -> ResearchJob | None:
    return _jobs.get(job_id)


async def publish(event: ProgressEvent) -> None:
    queue = _queues.get(event.job_id)
    if queue is not None:
        await queue.put(event)


async def finish(job_id: str) -> None:
    """Signal end-of-stream to any SSE listeners (sentinel None)."""
    queue = _queues.get(job_id)
    if queue is not None:
        await queue.put(None)


def queue_for(job_id: str) -> asyncio.Queue[ProgressEvent | None] | None:
    return _queues.get(job_id)
