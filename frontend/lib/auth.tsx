'use client';
import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { api, AuthUser } from './api';

type AuthContextValue = {
  user: AuthUser | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};
const AuthContext = createContext<AuthContextValue | undefined>(undefined);
const TOKEN_KEY = 'tpt_token';
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { const saved = localStorage.getItem(TOKEN_KEY); if (saved) { setToken(saved); api.me(saved).then(setUser).catch(() => { localStorage.removeItem(TOKEN_KEY); setToken(null); }); } setLoading(false); }, []);
  const login = async (email: string, password: string) => { const { token: nextToken } = await api.login(email, password); localStorage.setItem(TOKEN_KEY, nextToken); setToken(nextToken); setUser(await api.me(nextToken)); };
  const logout = () => { localStorage.removeItem(TOKEN_KEY); setToken(null); setUser(null); };
  const value = useMemo(() => ({ user, token, loading, login, logout }), [user, token, loading]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
export function useAuth() { const ctx = useContext(AuthContext); if (!ctx) throw new Error('useAuth must be used within AuthProvider'); return ctx; }
