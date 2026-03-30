"use client";

import React, { useEffect, useState } from "react";
import { apiClient } from "../../lib/apiClient";
import { useAuth } from "../../auth/AuthContext";

interface ReportRow {
  key: string;
  label: string;
  total_seconds: number;
}

interface ApiReportRow {
  date?: string;
  user_id?: number;
  user_email?: string;
  task_name?: string;
  total_seconds: number;
}

function formatDuration(seconds: number): string {
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;
  return `${hrs.toString().padStart(2, "0")}:${mins
    .toString()
    .padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
}

const today = new Date();
const sevenDaysAgo = new Date();
sevenDaysAgo.setDate(today.getDate() - 6);

function toDateInputValue(d: Date): string {
  return d.toISOString().slice(0, 10);
}

const defaultStart = toDateInputValue(sevenDaysAgo);
const defaultEnd = toDateInputValue(today);

type TabKey = "day" | "user" | "task";

const tabConfig: Record<
  TabKey,
  { label: string; endpoint: string; buildLabel: (row: ApiReportRow) => string }
> = {
  day: {
    label: "By Day",
    endpoint: "/api/v1/reports/by-day",
    buildLabel: (row) => row.date ?? "Unknown date",
  },
  user: {
    label: "By User",
    endpoint: "/api/v1/reports/by-user",
    buildLabel: (row) => row.user_email ?? `User ${row.user_id ?? "?"}`,
  },
  task: {
    label: "By Task",
    endpoint: "/api/v1/reports/by-task",
    buildLabel: (row) => row.task_name ?? "Unspecified task",
  },
};

const ReportsClient: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState<TabKey>("day");
  const [startDate, setStartDate] = useState<string>(defaultStart);
  const [endDate, setEndDate] = useState<string>(defaultEnd);
  const [rows, setRows] = useState<ReportRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    setError(null);
    try {
      const cfg = tabConfig[activeTab];
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
      });
      const res = await apiClient.get<ApiReportRow[]>(
        `${cfg.endpoint}?${params.toString()}`
      );
      const data = res.data ?? [];
      const mapped: ReportRow[] = data.map((row, index) => ({
        key: `${activeTab}-${index}`,
        label: cfg.buildLabel(row),
        total_seconds: row.total_seconds,
      }));
      setRows(mapped);
    } catch (err: any) {
      console.error("Failed to load reports", err);
      setError(
        err?.response?.data?.detail ||
          err?.message ||
          "Failed to load reports. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await loadData();
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">Reports</h1>
      <p className="text-sm text-gray-600">
        View total tracked time by day, user, or task. Adjust the date range and
        switch tabs to change the aggregation.
      </p>

      <form
        onSubmit={handleSubmit}
        className="flex flex-wrap items-end gap-4 rounded-md border border-gray-200 bg-white p-4 shadow-sm"
        aria-label="Report filters"
      >
        <div className="flex flex-col">
          <label htmlFor="startDate" className="text-sm font-medium">
            Start date
          </label>
          <input
            id="startDate"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="mt-1 rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </div>
        <div className="flex flex-col">
          <label htmlFor="endDate" className="text-sm font-medium">
            End date
          </label>
          <input
            id="endDate"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="mt-1 rounded border border-gray-300 px-2 py-1 text-sm"
          />
        </div>
        <button
          type="submit"
          className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          Apply
        </button>
      </form>

      <div className="flex gap-2" role="tablist" aria-label="Report type">
        {(Object.keys(tabConfig) as TabKey[]).map((key) => {
          const cfg = tabConfig[key];
          const isActive = key === activeTab;
          return (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={isActive}
              className={`rounded px-3 py-1 text-sm font-medium border ${
                isActive
                  ? "border-blue-600 bg-blue-50 text-blue-700"
                  : "border-gray-200 bg-white text-gray-700 hover:bg-gray-50"
              }`}
              onClick={() => setActiveTab(key)}
            >
              {cfg.label}
            </button>
          );
        })}
      </div>

      {error && (
        <div
          role="alert"
          className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700"
        >
          {error}
        </div>
      )}

      <div className="overflow-x-auto rounded-md border border-gray-200 bg-white shadow-sm">
        <table className="min-w-full divide-y divide-gray-200 text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide text-gray-500"
              >
                {tabConfig[activeTab].label.replace("By ", "")}
              </th>
              <th
                scope="col"
                className="px-4 py-2 text-right text-xs font-semibold uppercase tracking-wide text-gray-500"
              >
                Total time
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 bg-white">
            {loading ? (
              <tr>
                <td colSpan={2} className="px-4 py-6 text-center text-gray-500">
                  Loading...
                </td>
              </tr>
            ) : rows.length === 0 ? (
              <tr>
                <td colSpan={2} className="px-4 py-6 text-center text-gray-500">
                  No data for the selected range.
                </td>
              </tr>
            ) : (
              rows.map((row) => (
                <tr key={row.key}>
                  <td className="px-4 py-2 text-gray-800">{row.label}</td>
                  <td className="px-4 py-2 text-right font-mono text-gray-900">
                    {formatDuration(row.total_seconds)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ReportsClient;
