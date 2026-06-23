"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";

import { ProgressView } from "@/components/progress-view";
import { ReportView } from "@/components/report-view";
import { Card, CardContent } from "@/components/ui/card";
import { getJob, streamUrl } from "@/lib/api";
import type { ProgressEvent, Report, StageStatus } from "@/lib/types";

export default function ResearchPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const [statuses, setStatuses] = useState<Record<string, StageStatus>>({});
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    const es = new EventSource(streamUrl(jobId));

    es.onmessage = (e) => {
      const event: ProgressEvent = JSON.parse(e.data);
      setStatuses((prev) => ({ ...prev, [event.stage]: event.status }));
      if (event.status === "error") {
        setError(event.message ?? `Stage "${event.stage}" failed`);
      }
    };

    es.addEventListener("done", async () => {
      es.close();
      try {
        const job = await getJob(jobId);
        if (job.report) setReport(job.report);
        else if (job.status === "error") {
          // Keep the specific per-stage message if one already arrived.
          setError((prev) => prev ?? "Research failed. Check the backend logs.");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load report");
      }
    });

    es.onerror = () => {
      es.close();
      setError("Lost connection to the research stream.");
    };

    return () => es.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [jobId]);

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      {!report && (
        <div className="space-y-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              Researching…
            </h1>
            <p className="text-sm text-muted-foreground">
              Agents are working in parallel. This updates live.
            </p>
          </div>
          <ProgressView statuses={statuses} />
        </div>
      )}

      {error && (
        <Card className="border-destructive/50">
          <CardContent className="pt-6 text-sm text-destructive">
            {error}
          </CardContent>
        </Card>
      )}

      {report && <ReportView jobId={jobId} report={report} />}
    </div>
  );
}
