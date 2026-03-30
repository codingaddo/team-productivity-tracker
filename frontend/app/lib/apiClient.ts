export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface TimeEntry {
  id: number;
  description: string | null;
  start_time: string;
  end_time: string | null;
}

const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(token: string | null) {
    this.token = token;
  }

  private get headers() {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`;
    }
    return headers;
  }

  async register(email: string, password: string, fullName?: string) {
    const res = await fetch(`${BASE_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Registration failed");
    }
    return res.json();
  }

  async login(email: string, password: string): Promise<LoginResponse> {
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);

    const res = await fetch(`${BASE_URL}/api/v1/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Login failed");
    }
    return res.json();
  }

  async getMe() {
    const res = await fetch(`${BASE_URL}/api/v1/auth/me`, {
      headers: this.headers,
    });
    if (!res.ok) {
      throw new Error("Failed to load user");
    }
    return res.json();
  }

  async startTimer(description?: string | null) {
    const res = await fetch(`${BASE_URL}/api/v1/time-entries/start`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify({ description: description ?? null }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Failed to start timer");
    }
    return res.json();
  }

  async stopTimer() {
    const res = await fetch(`${BASE_URL}/api/v1/time-entries/stop`, {
      method: "POST",
      headers: this.headers,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Failed to stop timer");
    }
    return res.json();
  }

  async manualEntry(input: { description?: string; start_time: string; end_time: string }) {
    const res = await fetch(`${BASE_URL}/api/v1/time-entries/manual`, {
      method: "POST",
      headers: this.headers,
      body: JSON.stringify(input),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.detail || "Failed to create manual entry");
    }
    return res.json();
  }

  async listEntries(): Promise<TimeEntry[]> {
    const res = await fetch(`${BASE_URL}/api/v1/time-entries/`, {
      headers: this.headers,
    });
    if (!res.ok) {
      throw new Error("Failed to load time entries");
    }
    return res.json();
  }
}

export const apiClient = new ApiClient();
