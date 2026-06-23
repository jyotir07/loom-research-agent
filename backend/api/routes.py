"""HTTP API: start research, stream progress (SSE), fetch & download report."""
from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse, StreamingResponse

from api import store
from models.schemas import ProgressEvent, ResearchJob, ResearchRequest, StageStatus
from workflows.research_workflow import run_research

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["research"])


@router.post("/research", response_model=ResearchJob)
async def start_research(req: ResearchRequest) -> ResearchJob:
    """Create a job and run the workflow in the background."""
    job = store.create_job(req.topic)
    asyncio.create_task(_execute(job))
    return job


@router.get("/research/{job_id}", response_model=ResearchJob)
async def get_research(job_id: str) -> ResearchJob:
    job = store.get_job(job_id)
    if job is None:
        raise HTTPException(404, "job not found")
    return job


@router.get("/research/{job_id}/stream")
async def stream_research(job_id: str) -> StreamingResponse:
    """Server-Sent Events stream of progress updates."""
    queue = store.queue_for(job_id)
    if queue is None:
        raise HTTPException(404, "job not found")

    async def event_source():
        while True:
            event = await queue.get()
            if event is None:  # end-of-stream sentinel
                yield "event: done\ndata: {}\n\n"
                break
            yield f"data: {event.model_dump_json()}\n\n"

    return StreamingResponse(event_source(), media_type="text/event-stream")


@router.get("/research/{job_id}/download")
async def download_report(job_id: str, format: str = "md") -> PlainTextResponse:
    job = store.get_job(job_id)
    if job is None or job.report is None:
        raise HTTPException(404, "report not ready")
    if format != "md":
        raise HTTPException(400, "only 'md' supported in skeleton (TODO: pdf/json)")
    return PlainTextResponse(
        job.report.markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f'attachment; filename="report-{job_id}.md"'},
    )


async def _execute(job: ResearchJob) -> None:
    """Background driver: run the workflow, persist result, publish progress."""
    job.status = StageStatus.RUNNING
    try:
        report = await run_research(job.job_id, job.topic, on_progress=_publish)
        job.report = report
        job.status = StageStatus.DONE
    except Exception:  # noqa: BLE001 - job-level failure already emitted per-stage
        logger.exception("Research job %s failed", job.job_id)
        job.status = StageStatus.ERROR
    finally:
        await store.finish(job.job_id)


async def _publish(event: ProgressEvent) -> None:
    await store.publish(event)
