import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import App from "@/App";
import { getHealth } from "@/api/system";
import { useAuthStore } from "@/stores/auth-store";
import { useUiStore } from "@/stores/ui-store";
import { renderWithProviders } from "@/test/render";

vi.mock("@/api/system", () => ({
  getHealth: vi.fn(),
}));

describe("AppShell", () => {
  beforeEach(() => {
    vi.mocked(getHealth).mockResolvedValue({ status: "ok" });
    useAuthStore.setState({
      token: "test-token",
      user: { user_id: 7, username: "reader" },
      hasHydrated: true,
    });
    useUiStore.getState().reset();
  });

  it("provides accessible navigation and route-level lazy loading", async () => {
    const user = userEvent.setup();
    renderWithProviders(<App />, { route: "/" });

    expect(await screen.findByRole("heading", { name: "你好，reader" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "主导航" })).toBeInTheDocument();
    await user.click(screen.getByRole("link", { name: "搜索" }));
    expect(await screen.findByRole("heading", { name: "知识搜索" })).toBeInTheDocument();
  });

  it("opens and closes the mobile navigation drawer", async () => {
    const user = userEvent.setup();
    renderWithProviders(<App />, { route: "/knowledge" });

    await screen.findByRole("heading", { name: "知识库" });
    await user.click(screen.getByRole("button", { name: "打开导航" }));
    expect(screen.getByRole("button", { name: "关闭导航" })).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "关闭导航" }));
    expect(screen.queryByRole("button", { name: "关闭导航" })).not.toBeInTheDocument();
    expect(screen.getAllByRole("navigation", { name: "主导航" })).toHaveLength(1);
  });
});
