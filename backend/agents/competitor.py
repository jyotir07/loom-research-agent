"""Competitor Agent — finds competitors and positioning."""
from __future__ import annotations

from agents.base import BaseAgent, Context
from models.schemas import Competitor
from services import llm, search

_PROMPT = """Identify key competitors and their positioning for this topic.

Topic: {topic}
Search context:
{context}

Return ONLY JSON: {{"competitors": [{{"name": "...", "strengths": ["..."], \
"weaknesses": ["..."]}}]}}"""


class CompetitorAgent(BaseAgent):
    name = "competitor"

    async def run(self, ctx: Context) -> Context:
        topic = ctx["topic"]
        sources = await search.search(f"competitors alternatives {topic}")
        context = "\n".join(f"- {s.title}: {s.snippet}" for s in sources)
        data = await llm.complete_json(_PROMPT.format(topic=topic, context=context))
        ctx["competitors"] = [Competitor(**c) for c in data.get("competitors", [])]
        return ctx
