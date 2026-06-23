"""Pydantic models shared across agents, workflow state, and the API."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Source tracking (stretch goal: every fact can carry provenance)
# --------------------------------------------------------------------------- #
class Source(BaseModel):
    title: str | None = None
    url: str | None = None
    snippet: str | None = None


# --------------------------------------------------------------------------- #
# Planner output
# --------------------------------------------------------------------------- #
class ResearchPlan(BaseModel):
    topic: str
    tasks: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Per-agent research outputs
# --------------------------------------------------------------------------- #
class Company(BaseModel):
    name: str
    industry: str | None = None
    description: str | None = None
    website: str | None = None
    sources: list[Source] = Field(default_factory=list)


class Funding(BaseModel):
    company: str
    round: str | None = None
    amount: str | None = None
    investors: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)


class Trend(BaseModel):
    title: str
    description: str | None = None
    sources: list[Source] = Field(default_factory=list)


class Competitor(BaseModel):
    name: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Aggregator output: unified dataset handed to the Writer
# --------------------------------------------------------------------------- #
class ResearchData(BaseModel):
    companies: list[Company] = Field(default_factory=list)
    funding: list[Funding] = Field(default_factory=list)
    trends: list[Trend] = Field(default_factory=list)
    competitors: list[Competitor] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# Writer output
# --------------------------------------------------------------------------- #
class Report(BaseModel):
    topic: str
    markdown: str
    sources: list[Source] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


# --------------------------------------------------------------------------- #
# Workflow progress streaming (SSE)
# --------------------------------------------------------------------------- #
class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


class ProgressEvent(BaseModel):
    job_id: str
    stage: str  # e.g. "planning", "company", "writing"
    status: StageStatus
    message: str | None = None
    timestamp: datetime = Field(default_factory=_now)


# --------------------------------------------------------------------------- #
# API request / response
# --------------------------------------------------------------------------- #
class ResearchRequest(BaseModel):
    topic: str = Field(min_length=3)


class ResearchJob(BaseModel):
    job_id: str = Field(default_factory=lambda: uuid4().hex)
    topic: str
    status: StageStatus = StageStatus.PENDING
    report: Report | None = None
    created_at: datetime = Field(default_factory=_now)
