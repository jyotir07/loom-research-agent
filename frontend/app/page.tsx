import { TopicForm } from "@/components/topic-form";

export default function HomePage() {
  return (
    <div className="mx-auto flex max-w-2xl flex-col items-center gap-8 py-16 text-center">
      <div className="space-y-3">
        <h1 className="text-4xl font-bold tracking-tight">
          Research any topic with a team of AI agents
        </h1>
        <p className="text-muted-foreground">
          A planner, four parallel researchers, an aggregator, and a writer
          collaborate to produce a comprehensive report — watch it build live.
        </p>
      </div>
      <TopicForm />
    </div>
  );
}
