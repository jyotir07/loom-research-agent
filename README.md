# Deep Research Agent

A production-grade AI research system: enter a topic, and a team of AI agents
collaborates to produce a comprehensive, downloadable research report — with live
progress streamed to the UI.

This is a showcase project for [**Loom**](https://github.com/jyotir07/loom), used
here as the unified LLM inference layer.

> **Example**
> _Input:_ "Analyze the Indian AI startup ecosystem in 2026 — top companies,
> funding trends, major players, challenges, and opportunities."
> _Output:_ a structured Markdown report (Executive Summary → Market Overview →
> Top Companies → Funding → Competitive Landscape → Trends → Opportunities →
> Challenges → Conclusion).

---

## How it works

```
User Query
    │
    ▼
Planner Agent            decompose topic into research tasks
    │
    ├───────────┬───────────┬───────────┐   ← run in parallel (asyncio.gather)
    ▼           ▼           ▼           ▼
 Company     Funding      Trends    Competitor
    │           │           │           │
    └───────────┴───────────┴───────────┘
                    │
                    ▼
            Aggregator Agent     merge + dedupe → unified dataset
                    │
                    ▼
              Writer Agent       dataset → Markdown report
                    │
                    ▼
              Final Report
```

Each stage emits a progress event, streamed to the client over **SSE** so the
user can watch the research build in real time.

## Where Loom fits

**Loom is an LLM provider abstraction layer** (one API across OpenAI, Anthropic,
Gemini, and 14+ providers — with caching, retries, model routing, and cost
tracking). It is **not** an agent/workflow framework.

So this project splits responsibilities cleanly:

| Concern | Owned by |
| --- | --- |
| LLM calls, provider/model routing, fallback, caching, cost | **Loom** (`services/llm.py`) |
| Agents, parallel execution, shared state, progress, workflow | **This app** (`agents/`, `workflows/`) |

Every agent's model call goes through `services/llm.py`, the single point of
contact with Loom. `services/llm.py` also wires a cheap-first `Router` to
demonstrate Loom's cost-optimized model fallback.

## Tech stack

- **Backend:** FastAPI · Loom (`loom-router`) · Pydantic · SSE
- **Frontend:** Next.js · TypeScript · TailwindCSS · ShadCN _(not yet scaffolded)_
- **Persistence:** in-memory for now; PostgreSQL/Redis planned

## Project structure

```
backend/
├── main.py                      # FastAPI app, CORS, /health
├── config.py                    # settings (env / .env)
├── requirements.txt
├── .env.example
├── agents/                      # planner, company, funding, trends,
│                                #   competitor, aggregator, writer
├── workflows/
│   └── research_workflow.py     # orchestration: plan → parallel → aggregate → write
├── services/
│   ├── llm.py                   # Loom wrapper (the only Loom touchpoint)
│   └── search.py                # web search (stubbed until SEARCH_API_KEY set)
├── models/
│   └── schemas.py               # Pydantic data contracts + progress events
└── api/
    ├── routes.py                # start / stream / fetch / download
    └── store.py                 # in-memory job + progress store
```

## Getting started

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate      # Windows; use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt

cp .env.example .env               # add at least one provider key (e.g. OPENAI_API_KEY)

uvicorn main:app --reload          # http://localhost:8000
```

API docs are served at `http://localhost:8000/docs`.

## API

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/research` | Start a research job (`{"topic": "..."}`); returns a `job_id` |
| `GET` | `/api/research/{job_id}` | Fetch job status + report when ready |
| `GET` | `/api/research/{job_id}/stream` | SSE stream of progress events |
| `GET` | `/api/research/{job_id}/download?format=md` | Download the report (Markdown) |
| `GET` | `/health` | Health check |

Quick smoke test:

```bash
JOB=$(curl -s -X POST localhost:8000/api/research \
  -H 'content-type: application/json' \
  -d '{"topic":"Indian AI startup ecosystem 2026"}' | jq -r .job_id)

curl -N localhost:8000/api/research/$JOB/stream      # watch progress
curl localhost:8000/api/research/$JOB/download -o report.md
```

## Status

| Area | State |
| --- | --- |
| Backend skeleton (agents, workflow, API, SSE) | ✅ Implemented |
| Loom inference wrapper | ✅ Implemented (verify against installed `loom-router`) |
| Web search | ⏳ Stubbed (returns fake results until `SEARCH_API_KEY` set) |
| Persistence (Postgres/Redis) | ⏳ In-memory only |
| PDF / JSON export | ⏳ Markdown only |
| Frontend (Next.js) | ⏳ Not started |

## Roadmap

- Real web search provider (Tavily/Serper) in `services/search.py`
- Next.js frontend: Home → live Progress view → Results + downloads
- Persistence + multi-report history
- PDF/JSON export
- Stretch: follow-up questions without re-running the full pipeline, per-fact
  source tracking
