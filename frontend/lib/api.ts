import type { ResearchJob } from "@/lib/types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export async function startResearch(topic: string): Promise<ResearchJob> {
  const res = await fetch(`${API_BASE}/api/research`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic }),
  });
  if (!res.ok) throw new Error(`Failed to start research (${res.status})`);
  return res.json();
}

export async function getJob(jobId: string): Promise<ResearchJob> {
  const res = await fetch(`${API_BASE}/api/research/${jobId}`, {
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`Failed to fetch job (${res.status})`);
  return res.json();
}

export function streamUrl(jobId: string): string {
  return `${API_BASE}/api/research/${jobId}/stream`;
}

export function downloadUrl(jobId: string, format: "md" = "md"): string {
  return `${API_BASE}/api/research/${jobId}/download?format=${format}`;
}
