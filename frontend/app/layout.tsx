import "./globals.css";
import type { ReactNode } from "react";
import { AppProviders } from "./providers";

export const metadata = {
  title: "Team Productivity Tracker",
  description: "Track time and productivity for your team",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <AppProviders>
          <main className="min-h-screen flex flex-col items-center justify-center p-4">
            {children}
          </main>
        </AppProviders>
      </body>
    </html>
  );
}
