# Deep Research Agent (Loom Showcase Project)

Build a production-grade AI research system that demonstrates the core capabilities of Loom. The goal is to showcase multi-agent orchestration, routing, parallel execution, shared state, and workflow management through a real-world application.

## Project Goal

Create a web application where a user enters a research topic, and a team of AI agents collaborates to produce a comprehensive research report.

Example input:

```text
Analyze the Indian AI startup ecosystem in 2026 and identify the top companies, funding trends, major players, challenges, and future opportunities.
```

Example output:

```text
Executive Summary
Market Overview
Top Companies
Funding Analysis
Competitive Landscape
Emerging Trends
Opportunities
Challenges
References
Conclusion
```

The user should be able to watch the research progress in real time and download the final report as Markdown or PDF.

---

## Primary Purpose

This project exists to demonstrate Loom's strengths:

* Agent orchestration
* Workflow routing
* Parallel execution
* Shared state management
* Context propagation
* Fault-tolerant workflows
* Extensible agent pipelines

The architecture should clearly show why Loom is useful compared to manually wiring multiple LLM calls together.

---

# Architecture

## Workflow Overview

```text
User Query
    │
    ▼
Planner Agent
    │
    ├─────────────┬─────────────┬─────────────┐
    ▼             ▼             ▼             ▼
Company      Funding      Trends      Competitor
Agent        Agent        Agent       Agent
    │             │             │             │
    └─────────────┴─────────────┴─────────────┘
                          │
                          ▼
                   Aggregator Agent
                          │
                          ▼
                    Writer Agent
                          │
                          ▼
                     Final Report
```

---

# Agent Responsibilities

## 1. Planner Agent

Responsible for decomposing the user query into research tasks.

Input:

```text
Analyze the Indian AI startup ecosystem
```

Output:

```json
{
  "tasks": [
    "Identify major startups",
    "Analyze funding landscape",
    "Identify competitors",
    "Find market trends",
    "Discover opportunities"
  ]
}
```

Responsibilities:

* Understand user intent
* Break research into subproblems
* Generate structured plan
* Store plan in workflow state

---

## 2. Company Research Agent

Responsible for finding key organizations related to the topic.

Output example:

```json
{
  "companies": [
    {
      "name": "Example AI",
      "industry": "Healthcare AI",
      "description": "...",
      "website": "..."
    }
  ]
}
```

Responsibilities:

* Search web
* Extract company information
* Remove duplicates
* Rank importance

---

## 3. Funding Agent

Researches funding and investment activity.

Output:

```json
{
  "funding": [
    {
      "company": "Example AI",
      "round": "Series A",
      "amount": "$20M",
      "investors": []
    }
  ]
}
```

Responsibilities:

* Funding rounds
* Investor information
* Capital trends
* Investment analysis

---

## 4. Trends Agent

Researches market direction.

Output:

```json
{
  "trends": [
    "Agentic AI",
    "Voice AI",
    "Small Language Models"
  ]
}
```

Responsibilities:

* Emerging technologies
* Market shifts
* Growth patterns
* Industry insights

---

## 5. Competitor Agent

Finds competitors and alternatives.

Output:

```json
{
  "competitors": [
    {
      "name": "...",
      "strengths": [],
      "weaknesses": []
    }
  ]
}
```

Responsibilities:

* Market competition
* Positioning analysis
* Competitive advantages

---

## 6. Aggregator Agent

Combines outputs from all previous agents.

Input:

```python
{
    "companies": [...],
    "funding": [...],
    "trends": [...],
    "competitors": [...]
}
```

Output:

```python
{
    "research_data": {...}
}
```

Responsibilities:

* Merge results
* Deduplicate information
* Validate structure
* Create unified dataset

---

## 7. Writer Agent

Produces the final report.

Output:

```markdown
# Research Report

## Executive Summary

...

## Market Overview

...

## Companies

...

## Funding

...

## Trends

...

## Conclusion
```

Responsibilities:

* Professional formatting
* Structured writing
* Citations
* Executive summary

---

# Loom Integration Requirements

The project must heavily showcase Loom features.

## Routing

Example:

```python
router.route(task)
```

Different task types should be routed automatically to different agents.

---

## Parallel Execution

Company, Funding, Trends, and Competitor agents should execute concurrently.

Example:

```python
workflow.parallel(
    company_agent,
    funding_agent,
    trends_agent,
    competitor_agent
)
```

This should be one of the main Loom demonstrations.

---

## Shared State

Use a central workflow context.

Example:

```python
ctx["plan"]
ctx["companies"]
ctx["funding"]
ctx["trends"]
ctx["competitors"]
ctx["report"]
```

All agents should read and write to shared state.

---

## Workflow Visualization

Display workflow progress.

Example:

```text
Planning            ✓
Company Research    ✓
Funding Analysis    ✓
Trend Analysis      ✓
Competition Study   ✓
Writing Report      ✓
```

This should update live.

---

# Backend

Use:

* FastAPI
* Loom
* OpenAI or Gemini
* PostgreSQL
* Redis (optional)
* Pydantic

Structure:

```text
backend/
├── agents/
│   ├── planner.py
│   ├── company.py
│   ├── funding.py
│   ├── trends.py
│   ├── competitor.py
│   ├── aggregator.py
│   └── writer.py
│
├── workflows/
│   └── research_workflow.py
│
├── models/
│   └── schemas.py
│
├── services/
│   ├── llm.py
│   └── search.py
│
├── api/
│   └── routes.py
│
└── main.py
```

---

# Frontend

Use:

* Next.js
* TypeScript
* TailwindCSS
* ShadCN

Pages:

### Home

Input box:

```text
What would you like to research?
```

---

### Progress View

Show workflow execution in real time.

```text
✓ Planning

✓ Company Research

✓ Funding Analysis

⟳ Writing Report
```

Use WebSockets or SSE.

---

### Results View

Show:

* Executive Summary
* Report Sections
* Sources
* Download Buttons

Buttons:

```text
Download Markdown
Download PDF
```

---

# Stretch Features

Implement if time permits.

### Follow-Up Questions

User can ask:

```text
Compare these companies in more detail.
```

without rerunning entire research.

---

### Source Tracking

Every fact should retain source metadata.

Example:

```json
{
  "statement": "...",
  "source": "..."
}
```

---

### Multi-Report History

Store previous reports.

---

### Export Formats

* PDF
* Markdown
* JSON

---

# Success Criteria

A user enters any research topic.

The system:

1. Creates a research plan.
2. Runs multiple agents concurrently.
3. Aggregates findings.
4. Generates a professional report.
5. Shows progress in real time.
6. Demonstrates Loom's routing, orchestration, state management, and parallel execution capabilities clearly.

The finished project should serve as Loom's flagship example repository and be impressive enough that a developer can immediately understand Loom's value by looking at the codebase and demo.
