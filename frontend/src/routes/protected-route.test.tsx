import { screen } from "@testing-library/react";
import { Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it } from "vitest";

import { ProtectedRoute } from "@/routes/protected-route";
import { useAuthStore } from "@/stores/auth-store";
import { renderWithProviders } from "@/test/render";

describe("ProtectedRoute", () => {
  beforeEach(() => {
    useAuthStore.setState({ token: null, user: null, hasHydrated: true });
  });

  it("redirects unauthenticated visitors to login", () => {
    renderWithProviders(
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/private" element={<h1>Private workspace</h1>} />
        </Route>
        <Route path="/login" element={<h1>Login</h1>} />
      </Routes>,
      { route: "/private?tab=recent" },
    );

    expect(screen.getByRole("heading", { name: "Login" })).toBeInTheDocument();
    expect(screen.queryByText("Private workspace")).not.toBeInTheDocument();
  });

  it("renders protected content for an authenticated user", () => {
    useAuthStore.setState({
      token: "test-token",
      user: { user_id: 7, username: "reader" },
      hasHydrated: true,
    });

    renderWithProviders(
      <Routes>
        <Route element={<ProtectedRoute />}>
          <Route path="/private" element={<h1>Private workspace</h1>} />
        </Route>
      </Routes>,
      { route: "/private" },
    );

    expect(screen.getByRole("heading", { name: "Private workspace" })).toBeInTheDocument();
  });
});
