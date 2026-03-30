import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import LoginPage from "./../app/auth/login/page";
import { AuthProvider } from "../app/auth/AuthContext";

jest.mock("next/navigation", () => ({
  useRouter: () => ({ push: jest.fn() }),
}));

jest.mock("../app/lib/apiClient", () => ({
  apiClient: {
    login: jest.fn().mockResolvedValue({ access_token: "token", token_type: "bearer" }),
  },
}));

function renderWithProviders() {
  return render(
    <AuthProvider>
      <LoginPage />
    </AuthProvider>
  );
}

test("submits login form and calls API", async () => {
  renderWithProviders();

  fireEvent.change(screen.getByLabelText(/email/i), { target: { value: "user@example.com" } });
  fireEvent.change(screen.getByLabelText(/password/i), { target: { value: "password123" } });

  fireEvent.click(screen.getByRole("button", { name: /login/i }));

  await waitFor(() => {
    expect(screen.getByRole("button", { name: /logging in/i })).toBeInTheDocument();
  });
});
