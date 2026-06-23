"""Web search service.

Returns a stub when no SEARCH_API_KEY is configured so the workflow runs
end-to-end during development. Swap in a real provider (Tavily, Serper, Bing)
in `_search_<provider>` when ready.
"""
from __future__ import annotations

from config import settings
from models.schemas import Source


async def search(query: str, *, max_results: int = 5) -> list[Source]:
    """Search the web and return ranked sources."""
    if not settings.search_api_key:
        return _stub(query, max_results)

    provider = settings.search_provider.lower()
    if provider == "tavily":
        return await _search_tavily(query, max_results)
    # TODO: add serper / bing / etc.
    raise NotImplementedError(f"Unknown search provider: {provider}")


async def _search_tavily(query: str, max_results: int) -> list[Source]:
    # TODO: implement real Tavily call with httpx.AsyncClient.
    raise NotImplementedError("Tavily search not implemented yet")


def _stub(query: str, max_results: int) -> list[Source]:
    return [
        Source(
            title=f"[stub] Result {i + 1} for {query!r}",
            url=f"https://example.com/search?q={query}&r={i + 1}",
            snippet="Stub snippet — configure SEARCH_API_KEY for real results.",
        )
        for i in range(max_results)
    ]
