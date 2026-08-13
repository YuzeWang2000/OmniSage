import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import * as settingsApi from "@/api/settings";
import * as systemApi from "@/api/system";
import { ProviderConnections } from "@/features/settings/provider-connections";
import { renderWithProviders } from "@/test/render";
import { ApiError } from "@/api/client";

vi.mock("@/api/settings", async () => {
  const actual = await vi.importActual<typeof import("@/api/settings")>("@/api/settings");
  return { ...actual, getConnections: vi.fn(), createConnection: vi.fn(), updateConnection: vi.fn(), deleteConnection: vi.fn(), testConnection: vi.fn(), refreshConnectionModels: vi.fn() };
});
vi.mock("@/api/system", async () => {
  const actual = await vi.importActual<typeof import("@/api/system")>("@/api/system");
  return { ...actual, getModels: vi.fn() };
});

const connection = {
  id: "c1", provider: "deepseek" as const, display_name: "Personal DeepSeek", protocol: "openai_compatible",
  base_url: "https://api.deepseek.com", config: {}, is_active: true, has_credential: true,
  masked_credential: "sk-••••ret", credential_version: 3, last_test_status: "success",
};

describe("ProviderConnections", () => {
  it("shows masked credentials, source, stale state and capability tags", async () => {
    vi.mocked(settingsApi.getConnections).mockResolvedValue([connection]);
    vi.mocked(systemApi.getModels).mockResolvedValue([{
      key: "deepseek::c1::live", connection_id: "c1", provider: "deepseek", id: "live",
      display_name: "Live Model", source: "provider_api", available: true, task_types: ["chat"],
      input_modalities: ["text"], output_modalities: ["text"], capabilities: { reasoning: true, reasoning_efforts: ["high"] },
      metadata: { authorization_unverified: true }, stale: true, vision: false,
    }]);
    renderWithProviders(<ProviderConnections />);
    expect(await screen.findByText("Personal DeepSeek")).toBeInTheDocument();
    expect(screen.getByText(/sk-••••ret/)).toBeInTheDocument();
    expect(screen.getByText("provider_api")).toBeInTheDocument();
    expect(screen.getByText("stale")).toBeInTheDocument();
    expect(screen.getByText("推理")).toBeInTheDocument();
    expect(screen.getByText("权限待调用验证")).toBeInTheDocument();
    expect(screen.getByText("对话")).toBeInTheDocument();
    expect(screen.getByText("输入：文本 · 输出：文本")).toBeInTheDocument();
  });

  it("keeps form input when connection loading fails", async () => {
    vi.mocked(settingsApi.getConnections).mockRejectedValue(new Error("offline"));
    vi.mocked(systemApi.getModels).mockResolvedValue([]);
    renderWithProviders(<ProviderConnections />);
    const input = screen.getByLabelText("连接名称");
    await userEvent.clear(input);
    await userEvent.type(input, "Unsaved name");
    expect(await screen.findByText("连接列表加载失败，表单内容已保留。")).toBeInTheDocument();
    expect(input).toHaveValue("Unsaved name");
  });

  it("labels the provider API key and explains DashScope workspace rules", async () => {
    vi.mocked(settingsApi.getConnections).mockResolvedValue([]);
    vi.mocked(systemApi.getModels).mockResolvedValue([]);
    renderWithProviders(<ProviderConnections />);
    await userEvent.selectOptions(screen.getByLabelText("供应商"), "deepseek");
    expect(screen.getByText("DeepSeek API Key")).toBeInTheDocument();
    expect(screen.getByLabelText("API Key")).toHaveAttribute("placeholder", "输入 DeepSeek API Key");
    await userEvent.selectOptions(screen.getByLabelText("供应商"), "dashscope");
    expect(screen.getByText("阿里云百炼 API Key")).toBeInTheDocument();
    expect(screen.getByText(/北京\/新加坡可不填/)).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "北京（Workspace 可选）" })).toBeInTheDocument();
    expect(screen.getByText(/留空获取全部候选/)).toBeInTheDocument();
    expect(screen.getByLabelText("模型白名单")).toBeInTheDocument();
  });

  it("shows the concrete API key validation error and preserves input", async () => {
    vi.mocked(settingsApi.getConnections).mockResolvedValue([]);
    vi.mocked(systemApi.getModels).mockResolvedValue([]);
    vi.mocked(settingsApi.createConnection).mockRejectedValue(new ApiError("提交内容有误", {
      status: 422,
      kind: "validation",
      fieldErrors: { api_key: "String should have at least 8 characters" },
    }));
    renderWithProviders(<ProviderConnections />);
    await userEvent.selectOptions(screen.getByLabelText("供应商"), "deepseek");
    await userEvent.type(screen.getByLabelText("API Key"), "shortkey");
    await userEvent.click(screen.getByRole("button", { name: "添加连接" }));
    expect(await screen.findByText("String should have at least 8 characters")).toBeInTheDocument();
    expect(screen.getByLabelText("API Key")).toHaveValue("shortkey");
  });
});
