import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getModels } from "@/api/system";
import { PreferencesForm } from "@/features/settings/preferences-form";
import { usePreferencesStore } from "@/stores/preferences-store";
import { renderWithProviders } from "@/test/render";

vi.mock("@/api/system", () => ({
  getModels: vi.fn(),
}));

const mockedGetModels = vi.mocked(getModels);

describe("PreferencesForm", () => {
  beforeEach(() => {
    localStorage.clear();
    mockedGetModels.mockReset();
    mockedGetModels.mockResolvedValue({
      local_models: ["qwen-local"],
      online_models: ["deepseek-chat"],
      all_models: ["qwen-local", "deepseek-chat"],
    });
    usePreferencesStore.setState({
      defaultModel: "",
      ragEnabled: false,
      wikiEnabled: false,
    });
  });

  it("persists the RAG and Wiki defaults only after saving", async () => {
    const user = userEvent.setup();
    renderWithProviders(<PreferencesForm />);

    await screen.findByRole("option", { name: "qwen-local" });
    await user.click(screen.getByRole("switch", { name: "默认启用 RAG" }));
    await user.click(screen.getByRole("switch", { name: "默认启用 Wiki" }));

    expect(usePreferencesStore.getState().ragEnabled).toBe(false);
    expect(usePreferencesStore.getState().wikiEnabled).toBe(false);

    await user.click(screen.getByRole("button", { name: "保存默认设置" }));

    await waitFor(() => {
      expect(usePreferencesStore.getState().ragEnabled).toBe(true);
      expect(usePreferencesStore.getState().wikiEnabled).toBe(true);
    });
    expect(screen.getByText("默认设置已保存到当前设备")).toBeInTheDocument();
  });
});
