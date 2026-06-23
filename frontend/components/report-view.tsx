"use client";

import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Download } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { downloadUrl } from "@/lib/api";
import type { Report } from "@/lib/types";

export function ReportView({
  jobId,
  report,
}: {
  jobId: string;
  report: Report;
}) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-lg font-semibold">Research Report</h2>
        <Button asChild variant="outline" size="sm">
          <a href={downloadUrl(jobId, "md")} download>
            <Download className="h-4 w-4" />
            Download Markdown
          </a>
        </Button>
      </div>

      <Card>
        <CardContent className="prose prose-neutral max-w-none pt-6 dark:prose-invert">
          <Markdown remarkPlugins={[remarkGfm]}>{report.markdown}</Markdown>
        </CardContent>
      </Card>

      {report.sources.length > 0 && (
        <Card>
          <CardContent className="pt-6">
            <h3 className="mb-2 font-semibold">Sources</h3>
            <ul className="space-y-1 text-sm">
              {report.sources.map((s, i) => (
                <li key={i}>
                  {s.url ? (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-primary underline-offset-4 hover:underline"
                    >
                      {s.title ?? s.url}
                    </a>
                  ) : (
                    (s.title ?? s.snippet)
                  )}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
