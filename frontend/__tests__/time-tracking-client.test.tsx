import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import TimeTrackingClient from "../app/app/time/TimeTrackingClient";
import { AuthProvider } from "../app/auth/AuthContext";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ replace: jest.fn(), push: jest.fn() }),
}));

jest.mock("../app/lib/apiClient", () => ({
  apiClient: {
    listEntries: jest.fn().mockResolvedValue([]),
    startTimer: jest.fn().mockResolvedValue({}),
    stopTimer: jest.fn().mockResolvedValue({}),
    manualEntry: jest.fn().mockResolvedValue({}),
  },
}));

function renderWithProviders() {
  // Provide a fake token by mocking sessionStorage
  Object.defineProperty(window, "sessionStorage", {
    value: {
      getItem: () => "token",
      setItem: () => {},
      removeItem: () => {},
    },
    writable: true,
  });

  return render(
    <AuthProvider>
      <TimeTrackingClient />
    </AuthProvider>
  );
}

test("renders time tracking actions", async () => {
  renderWithProviders();

  await waitFor(() => {
    expect(screen.getByText(/time tracking/i)).toBeInTheDocument();
  });

  expect(screen.getByRole("button", { name: /start timer/i })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: /stop timer/i })).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: /start timer/i }));
  fireEvent.click(screen.getByRole("button", { name: /stop timer/i }));
});
