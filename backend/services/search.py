"""Web search service.

Returns a stub when no SEARCH_API_KEY is configured so the workflow runs
end-to-end during development. With a key set, calls a real provider
(SEARCH_PROVIDER): "tavily" or "serper".
"""
from __future__ import annotations

import logging

import httpx

from config import settings
from models.schemas import Source

logger = logging.getLogger(__name__)

_TAVILY_URL = "https://api.tavily.com/search"
_SERPER_URL = "https://google.serper.dev/search"
_TIMEOUT = httpx.Timeout(20.0)


async def search(query: str, *, max_results: int = 5) -> list[Source]:
    """Search the web and return ranked sources.

    Network/provider errors are logged and downgraded to an empty list so a
    single failed search doesn't abort the whole research workflow.
    """
    if not settings.search_api_key:
        return _stub(query, max_results)

    provider = settings.search_provider.lower()
    try:
        if provider == "tavily":
            return await _search_tavily(query, max_results)
        if provider == "serper":
            return await _search_serper(query, max_results)
        raise NotImplementedError(f"Unknown search provider: {provider!r}")
    except NotImplementedError:
        raise
    except Exception:  # noqa: BLE001 - keep the workflow resilient
        logger.exception("Search failed (provider=%s, query=%r)", provider, query)
        return []


async def _search_tavily(query: str, max_results: int) -> list[Source]:
    payload = {
        "api_key": settings.search_api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(_TAVILY_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()

    return [
        Source(
            title=r.get("title"),
            url=r.get("url"),
            snippet=r.get("content"),
        )
        for r in data.get("results", [])[:max_results]
    ]


async def _search_serper(query: str, max_results: int) -> list[Source]:
    headers = {
        "X-API-KEY": settings.search_api_key or "",
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": max_results}
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(_SERPER_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    return [
        Source(
            title=r.get("title"),
            url=r.get("link"),
            snippet=r.get("snippet"),
        )
        for r in data.get("organic", [])[:max_results]
    ]


def _stub(query: str, max_results: int) -> list[Source]:
    return [
        Source(
            title=f"[stub] Result {i + 1} for {query!r}",
            url=f"https://example.com/search?q={query}&r={i + 1}",
            snippet="Stub snippet — configure SEARCH_API_KEY for real results.",
        )
        for i in range(max_results)
    ]
