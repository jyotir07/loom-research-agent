"""Writer Agent — turns the unified dataset into a Markdown report."""
from __future__ import annotations

from agents.base import BaseAgent, Context
from models.schemas import Report, ResearchData
from services import llm

_PROMPT = """You are a professional research writer. Using the structured data \
below, write a polished Markdown report on "{topic}".

Sections (use ## headings): Executive Summary, Market Overview, Top Companies, \
Funding Analysis, Competitive Landscape, Emerging Trends, Opportunities, \
Challenges, Conclusion.

Data (JSON):
{data}

Return ONLY the Markdown report."""


class WriterAgent(BaseAgent):
    name = "writing"

    async def run(self, ctx: Context) -> Context:
        topic = ctx["topic"]
        data: ResearchData = ctx["research_data"]
        markdown = await llm.complete(
            _PROMPT.format(topic=topic, data=data.model_dump_json(indent=2)),
            params={"max_tokens": 4000},
        )
        ctx["report"] = Report(topic=topic, markdown=llm.strip_code_fence(markdown))
        return ctx
