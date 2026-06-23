"""Base agent contract.

Each agent reads from and writes to the shared workflow context (a plain dict
managed by the workflow runner). This is *our* orchestration layer — Loom only
provides the LLM calls underneath.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

Context = dict[str, Any]


class BaseAgent(ABC):
    #: stable stage id used in progress events (e.g. "company")
    name: str = "agent"

    @abstractmethod
    async def run(self, ctx: Context) -> Context:
        """Do the work, mutate/return the shared context."""
        raise NotImplementedError
