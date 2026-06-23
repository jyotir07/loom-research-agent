"""Company Research Agent — finds and ranks key organizations."""
from __future__ import annotations

from agents.base import BaseAgent, Context
from models.schemas import Company
from services import llm, search

_PROMPT = """Identify the most important companies for this research topic.

Topic: {topic}
Search context:
{context}

Return ONLY JSON: {{"companies": [{{"name": "...", "industry": "...", \
"description": "...", "website": "..."}}]}}"""


class CompanyAgent(BaseAgent):
    name = "company"

    async def run(self, ctx: Context) -> Context:
        topic = ctx["topic"]
        sources = await search.search(f"top companies {topic}")
        context = "\n".join(f"- {s.title}: {s.snippet}" for s in sources)
        data = await llm.complete_json(_PROMPT.format(topic=topic, context=context))
        ctx["companies"] = [Company(**c) for c in data.get("companies", [])]
        return ctx
