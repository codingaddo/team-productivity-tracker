export type AuthUser = {
  id: string;
  email: string;
  name: string;
  role: 'admin' | 'manager' | 'member';
};

export type LoginResponse = { token: string };
export type TimeEntry = {
  id: string;
  project: string;
  task?: string | null;
  start_time: string;
  end_time?: string | null;
  notes?: string | null;
};
export type ReportRow = { label: string; hours: number; project?: string; user?: string };

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init: RequestInit = {}, token?: string): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers, cache: 'no-store' });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) => request<LoginResponse>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  me: (token: string) => request<AuthUser>('/auth/me', {}, token),
  listTimeEntries: (token: string, params?: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return request<TimeEntry[]>(`/time-entries${qs ? `?${qs}` : ''}`, {}, token);
  },
  createTimeEntry: (token: string, payload: Partial<TimeEntry>) => request<TimeEntry>('/time-entries', { method: 'POST', body: JSON.stringify(payload) }, token),
  updateTimeEntry: (token: string, id: string, payload: Partial<TimeEntry>) => request<TimeEntry>(`/time-entries/${id}`, { method: 'PUT', body: JSON.stringify(payload) }, token),
  userSummary: (token: string, params?: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return request<ReportRow[]>(`/reports/user-summary${qs ? `?${qs}` : ''}`, {}, token);
  },
  projectSummary: (token: string, params?: Record<string, string>) => {
    const qs = new URLSearchParams(params).toString();
    return request<ReportRow[]>(`/reports/project-summary${qs ? `?${qs}` : ''}`, {}, token);
  },
};
