"""In-memory job store + per-job progress event logs.

Skeleton-grade: swap for Postgres/Redis later (see config.database_url). Each
job keeps an append-only event log so any number of SSE subscribers, including
ones that connect late or reconnect, can replay its full progress history.
"""
from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from models.schemas import ProgressEvent, ResearchJob


@dataclass
class _EventLog:
    events: list[ProgressEvent] = field(default_factory=list)
    finished: bool = False
    changed: asyncio.Condition = field(default_factory=asyncio.Condition)


_jobs: dict[str, ResearchJob] = {}
_logs: dict[str, _EventLog] = {}
# Legacy single-consumer queues, still drained by the SSE route until it moves
# to subscribe().
_queues: dict[str, asyncio.Queue[ProgressEvent | None]] = {}


def create_job(topic: str) -> ResearchJob:
    job = ResearchJob(topic=topic)
    _jobs[job.job_id] = job
    _logs[job.job_id] = _EventLog()
    _queues[job.job_id] = asyncio.Queue()
    return job


def get_job(job_id: str) -> ResearchJob | None:
    return _jobs.get(job_id)


async def publish(event: ProgressEvent) -> None:
    log = _logs.get(event.job_id)
    if log is not None:
        async with log.changed:
            log.events.append(event)
            log.changed.notify_all()
    queue = _queues.get(event.job_id)
    if queue is not None:
        await queue.put(event)


async def finish(job_id: str) -> None:
    """Mark the job's event log complete so subscribers stop after replaying it."""
    log = _logs.get(job_id)
    if log is not None:
        async with log.changed:
            log.finished = True
            log.changed.notify_all()
    queue = _queues.get(job_id)
    if queue is not None:
        await queue.put(None)


def subscribe(job_id: str) -> AsyncIterator[ProgressEvent] | None:
    """Replay the job's events so far, then follow live ones until it finishes.

    Returns None for an unknown job so the caller can 404 before streaming.
    """
    log = _logs.get(job_id)
    if log is None:
        return None
    return _follow(log)


async def _follow(log: _EventLog) -> AsyncIterator[ProgressEvent]:
    seen = 0
    while True:
        async with log.changed:
            await log.changed.wait_for(lambda: len(log.events) > seen or log.finished)
            new = log.events[seen:]
            finished = log.finished
        # Yield outside the lock so a slow client never blocks publishers.
        for event in new:
            yield event
        seen += len(new)
        if finished:
            return


def queue_for(job_id: str) -> asyncio.Queue[ProgressEvent | None] | None:
    return _queues.get(job_id)
