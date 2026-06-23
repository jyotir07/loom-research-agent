"""Trends Agent — researches market direction and emerging tech."""
from __future__ import annotations

from agents.base import BaseAgent, Context
from models.schemas import Trend
from services import llm, search

_PROMPT = """Identify emerging trends and market shifts for this topic.

Topic: {topic}
Search context:
{context}

Return ONLY JSON: {{"trends": [{{"title": "...", "description": "..."}}]}}"""


class TrendsAgent(BaseAgent):
    name = "trends"

    async def run(self, ctx: Context) -> Context:
        topic = ctx["topic"]
        sources = await search.search(f"trends emerging technology {topic}")
        context = "\n".join(f"- {s.title}: {s.snippet}" for s in sources)
        data = await llm.complete_json(_PROMPT.format(topic=topic, context=context))
        ctx["trends"] = [Trend(**t) for t in data.get("trends", [])]
        return ctx
