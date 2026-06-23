"""Planner Agent — decomposes the user topic into research tasks."""
from __future__ import annotations

from agents.base import BaseAgent, Context
from models.schemas import ResearchPlan
from services import llm

_PROMPT = """You are a research planner. Break the topic below into 4-6 concrete \
research subtasks covering companies, funding, trends, and competitors.

Topic: {topic}

Return ONLY JSON: {{"tasks": ["...", "..."]}}"""


class PlannerAgent(BaseAgent):
    name = "planning"

    async def run(self, ctx: Context) -> Context:
        topic = ctx["topic"]
        data = await llm.complete_json(_PROMPT.format(topic=topic))
        ctx["plan"] = ResearchPlan(topic=topic, tasks=data.get("tasks", []))
        return ctx
