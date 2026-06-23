"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Loader2, Search } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { startResearch } from "@/lib/api";

const EXAMPLE =
  "Analyze the Indian AI startup ecosystem in 2026 and identify the top companies, funding trends, major players, challenges, and future opportunities.";

export function TopicForm() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (topic.trim().length < 3) return;
    setLoading(true);
    setError(null);
    try {
      const job = await startResearch(topic.trim());
      router.push(`/research/${job.job_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setLoading(false);
    }
  }

  return (
    <form onSubmit={onSubmit} className="w-full space-y-3">
      <div className="flex gap-2">
        <Input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="What would you like to research?"
          disabled={loading}
          className="h-11 text-base"
        />
        <Button type="submit" size="lg" disabled={loading} className="h-11">
          {loading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Search className="h-4 w-4" />
          )}
          Research
        </Button>
      </div>
      <button
        type="button"
        onClick={() => setTopic(EXAMPLE)}
        className="text-left text-xs text-muted-foreground hover:text-foreground"
      >
        Try an example →
      </button>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </form>
  );
}
