"use client";

import { AuthProvider } from "./auth/AuthContext";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}
