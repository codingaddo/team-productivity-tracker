"use client";

import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { apiClient } from "../lib/apiClient";

export interface User {
  id: number;
  email: string;
  full_name?: string | null;
}

interface AuthContextValue {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = window.sessionStorage.getItem("tp_token");
    if (stored) {
      setToken(stored);
      apiClient.setToken(stored);
      apiClient
        .getMe()
        .then((u) => setUser(u))
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = useCallback(async (newToken: string) => {
    setToken(newToken);
    window.sessionStorage.setItem("tp_token", newToken);
    apiClient.setToken(newToken);
    const u = await apiClient.getMe();
    setUser(u);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    window.sessionStorage.removeItem("tp_token");
    apiClient.setToken(null);
  }, []);

  const value = useMemo(
    () => ({ user, token, loading, login, logout }),
    [user, token, loading, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};
