import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { login, register } from "@/api/auth";
import { ApiError } from "@/api/client";
import { AuthForm } from "@/features/auth/auth-form";
import { useAuthStore } from "@/stores/auth-store";
import { renderWithProviders } from "@/test/render";

vi.mock("@/api/auth", () => ({
  login: vi.fn(),
  register: vi.fn(),
}));

const mockedLogin = vi.mocked(login);
const mockedRegister = vi.mocked(register);

describe("AuthForm", () => {
  beforeEach(() => {
    mockedLogin.mockReset();
    mockedRegister.mockReset();
    useAuthStore.setState({ token: null, user: null, hasHydrated: true });
  });

  it("logs in and stores the authenticated user", async () => {
    mockedLogin.mockResolvedValue({
      access_token: "jwt-token",
      token_type: "bearer",
      user_id: 12,
      username: "sage",
    });
    const user = userEvent.setup();
    renderWithProviders(
      <Routes>
        <Route path="/login" element={<AuthForm />} />
        <Route path="/" element={<h1>Workspace</h1>} />
      </Routes>,
      { route: "/login" },
    );

    await user.type(screen.getByLabelText("用户名"), "sage");
    await user.type(screen.getByLabelText("密码"), "secret");
    await user.click(screen.getByRole("button", { name: "登录" }));

    expect(await screen.findByRole("heading", { name: "Workspace" })).toBeInTheDocument();
    expect(mockedLogin).toHaveBeenCalledWith({ username: "sage", password: "secret" });
    expect(useAuthStore.getState().token).toBe("jwt-token");
    expect(useAuthStore.getState().user?.username).toBe("sage");
  });

  it("shows a safe login failure message", async () => {
    mockedLogin.mockRejectedValue(
      new ApiError("用户名或密码错误", { status: 401, kind: "unauthorized" }),
    );
    const user = userEvent.setup();
    renderWithProviders(<AuthForm />, { route: "/login" });

    await user.type(screen.getByLabelText("用户名"), "sage");
    await user.type(screen.getByLabelText("密码"), "wrong");
    await user.click(screen.getByRole("button", { name: "登录" }));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("用户名或密码错误");
    });
    expect(useAuthStore.getState().token).toBeNull();
  });
});
