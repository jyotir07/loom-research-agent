import type { Metadata } from "next";
import Link from "next/link";

import { ThemeProvider } from "@/components/theme-provider";
import { ThemeToggle } from "@/components/theme-toggle";
import "./globals.css";

export const metadata: Metadata = {
  title: "Deep Research Agent",
  description: "Multi-agent AI research, powered by Loom.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="min-h-screen antialiased">
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <header className="border-b">
            <div className="container flex h-14 items-center">
              <Link href="/" className="font-semibold">
                Deep Research Agent
              </Link>
              <span className="ml-2 text-xs text-muted-foreground">
                powered by Loom
              </span>
              <div className="ml-auto">
                <ThemeToggle />
              </div>
            </div>
          </header>
          <main className="container py-10">{children}</main>
        </ThemeProvider>
      </body>
    </html>
  );
}
