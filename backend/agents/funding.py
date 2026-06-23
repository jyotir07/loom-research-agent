"""Funding Agent — researches funding rounds and investors."""
from __future__ import annotations

from agents.base import BaseAgent, Context
from models.schemas import Funding
from services import llm, search

_PROMPT = """Research funding and investment activity for this topic.

Topic: {topic}
Search context:
{context}

Return ONLY JSON: {{"funding": [{{"company": "...", "round": "...", \
"amount": "...", "investors": ["..."]}}]}}"""


class FundingAgent(BaseAgent):
    name = "funding"

    async def run(self, ctx: Context) -> Context:
        topic = ctx["topic"]
        sources = await search.search(f"funding investment {topic}")
        context = "\n".join(f"- {s.title}: {s.snippet}" for s in sources)
        data = await llm.complete_json(_PROMPT.format(topic=topic, context=context))
        ctx["funding"] = [Funding(**f) for f in data.get("funding", [])]
        return ctx
