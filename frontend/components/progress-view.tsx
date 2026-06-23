"use client";

import { Check, CircleDashed, Loader2, X } from "lucide-react";

import { cn } from "@/lib/utils";
import { STAGES, type StageStatus } from "@/lib/types";

export function ProgressView({
  statuses,
}: {
  statuses: Record<string, StageStatus>;
}) {
  return (
    <ol className="space-y-2">
      {STAGES.map((stage) => {
        const status = statuses[stage.id] ?? "pending";
        return (
          <li
            key={stage.id}
            className={cn(
              "flex items-center gap-3 rounded-lg border px-4 py-3 text-sm transition-colors",
              status === "running" && "border-primary/50 bg-accent",
              status === "error" && "border-destructive/50"
            )}
          >
            <StageIcon status={status} />
            <span
              className={cn(
                status === "pending" && "text-muted-foreground",
                status === "done" && "text-foreground"
              )}
            >
              {stage.label}
            </span>
          </li>
        );
      })}
    </ol>
  );
}

function StageIcon({ status }: { status: StageStatus }) {
  switch (status) {
    case "done":
      return <Check className="h-4 w-4 text-green-600" />;
    case "running":
      return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
    case "error":
      return <X className="h-4 w-4 text-destructive" />;
    default:
      return <CircleDashed className="h-4 w-4 text-muted-foreground" />;
  }
}
