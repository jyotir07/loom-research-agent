// Mirrors backend/models/schemas.py

export type StageStatus = "pending" | "running" | "done" | "error";

export interface ProgressEvent {
  job_id: string;
  stage: string;
  status: StageStatus;
  message?: string | null;
  timestamp: string;
}

export interface Source {
  title?: string | null;
  url?: string | null;
  snippet?: string | null;
}

export interface Report {
  topic: string;
  markdown: string;
  sources: Source[];
  created_at: string;
}

export interface ResearchJob {
  job_id: string;
  topic: string;
  status: StageStatus;
  report?: Report | null;
  created_at: string;
}

// Pipeline stages in display order; ids match the agents' `name` fields.
export const STAGES: { id: string; label: string }[] = [
  { id: "planning", label: "Planning" },
  { id: "company", label: "Company Research" },
  { id: "funding", label: "Funding Analysis" },
  { id: "trends", label: "Trend Analysis" },
  { id: "competitor", label: "Competition Study" },
  { id: "aggregating", label: "Aggregating Findings" },
  { id: "writing", label: "Writing Report" },
];
