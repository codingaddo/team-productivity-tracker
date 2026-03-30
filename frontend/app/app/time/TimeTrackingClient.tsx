"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiClient, TimeEntry } from "../../lib/apiClient";
import { useAuth } from "../../auth/AuthContext";

export default function TimeTrackingClient() {
  const { user, token, logout } = useAuth();
  const router = useRouter();
  const [entries, setEntries] = useState<TimeEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [manualDescription, setManualDescription] = useState("");
  const [manualStart, setManualStart] = useState("");
  const [manualEnd, setManualEnd] = useState("");
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      router.replace("/auth/login");
      return;
    }
    const load = async () => {
      try {
        const data = await apiClient.listEntries();
        setEntries(data);
      } catch (err: any) {
        setError(err.message || "Failed to load entries");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [token, router]);

  const refreshEntries = async () => {
    const data = await apiClient.listEntries();
    setEntries(data);
  };

  const handleStart = async () => {
    setError(null);
    setActionMessage(null);
    try {
      await apiClient.startTimer();
      setActionMessage("Timer started");
      await refreshEntries();
    } catch (err: any) {
      setError(err.message || "Failed to start timer");
    }
  };

  const handleStop = async () => {
    setError(null);
    setActionMessage(null);
    try {
      await apiClient.stopTimer();
      setActionMessage("Timer stopped");
      await refreshEntries();
    } catch (err: any) {
      setError(err.message || "Failed to stop timer");
    }
  };

  const handleManualSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setActionMessage(null);
    try {
      await apiClient.manualEntry({
        description: manualDescription || undefined,
        start_time: manualStart,
        end_time: manualEnd,
      });
      setManualDescription("");
      setManualStart("");
      setManualEnd("");
      setActionMessage("Manual entry created");
      await refreshEntries();
    } catch (err: any) {
      setError(err.message || "Failed to create manual entry");
    }
  };

  if (!token) {
    return null;
  }

  return (
    <div className="w-full max-w-3xl space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Time tracking</h1>
          {user && <p className="text-sm text-slate-600">Signed in as {user.email}</p>}
        </div>
        <button
          onClick={() => {
            logout();
            router.push("/auth/login");
          }}
          className="text-sm text-red-600 underline"
        >
          Logout
        </button>
      </header>

      <section className="flex gap-3">
        <button
          onClick={handleStart}
          className="px-4 py-2 rounded bg-emerald-600 text-white text-sm font-medium hover:bg-emerald-700"
        >
          Start timer
        </button>
        <button
          onClick={handleStop}
          className="px-4 py-2 rounded bg-rose-600 text-white text-sm font-medium hover:bg-rose-700"
        >
          Stop timer
        </button>
      </section>

      <section className="bg-white shadow rounded p-4">
        <h2 className="font-semibold mb-3 text-sm">Manual entry</h2>
        <form onSubmit={handleManualSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-3 items-end">
          <div className="md:col-span-2">
            <label className="block text-xs font-medium mb-1" htmlFor="description">
              Description
            </label>
            <input
              id="description"
              type="text"
              value={manualDescription}
              onChange={(e) => setManualDescription(e.target.value)}
              className="w-full border rounded px-2 py-1 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" htmlFor="start">
              Start time
            </label>
            <input
              id="start"
              type="datetime-local"
              required
              value={manualStart}
              onChange={(e) => setManualStart(e.target.value)}
              className="w-full border rounded px-2 py-1 text-sm"
            />
          </div>
          <div>
            <label className="block text-xs font-medium mb-1" htmlFor="end">
              End time
            </label>
            <input
              id="end"
              type="datetime-local"
              required
              value={manualEnd}
              onChange={(e) => setManualEnd(e.target.value)}
              className="w-full border rounded px-2 py-1 text-sm"
            />
          </div>
          <div className="md:col-span-4 flex justify-end">
            <button
              type="submit"
              className="px-4 py-2 rounded bg-sky-600 text-white text-sm font-medium hover:bg-sky-700"
            >
              Save manual entry
            </button>
          </div>
        </form>
      </section>

      {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
      {actionMessage && <p className="text-sm text-emerald-700" role="status">{actionMessage}</p>}

      <section className="bg-white shadow rounded p-4">
        <h2 className="font-semibold mb-3 text-sm">Recent entries</h2>
        {loading ? (
          <p className="text-sm text-slate-600">Loading...</p>
        ) : entries.length === 0 ? (
          <p className="text-sm text-slate-600">No entries yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b bg-slate-50">
                  <th className="text-left py-2 px-2">Description</th>
                  <th className="text-left py-2 px-2">Start</th>
                  <th className="text-left py-2 px-2">End</th>
                </tr>
              </thead>
              <tbody>
                {entries.map((entry) => (
                  <tr key={entry.id} className="border-b last:border-0">
                    <td className="py-2 px-2">{entry.description || "—"}</td>
                    <td className="py-2 px-2">{new Date(entry.start_time).toLocaleString()}</td>
                    <td className="py-2 px-2">
                      {entry.end_time ? new Date(entry.end_time).toLocaleString() : "In progress"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
