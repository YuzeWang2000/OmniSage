import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useCallback, useState } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getKnowledgeBases } from "@/api/knowledge";
import { getWikiStatus, switchWikiMode } from "@/api/settings";
import { getModels } from "@/api/system";
import { ChatComposer } from "@/features/chat/chat-composer";
import type { ChatControls } from "@/features/chat/types";
import { renderWithProviders } from "@/test/render";

vi.mock("@/api/system", () => ({ getModels: vi.fn() }));
vi.mock("@/api/knowledge", () => ({ getKnowledgeBases: vi.fn() }));
vi.mock("@/api/settings", () => ({ getWikiStatus: vi.fn(), switchWikiMode: vi.fn() }));

function Harness() {
  const [controls, setControls] = useState<ChatControls>({
    model: "qwen-local",
    ragEnabled: false,
    wikiEnabled: false,
    knowledgeBaseId: null,
  });
  const update = useCallback((changes: Partial<ChatControls>) => {
    setControls((current) => ({ ...current, ...changes }));
  }, []);
  return (
    <ChatComposer
      userId={7}
      value=""
      controls={controls}
      streaming={false}
      hasConversation
      onValueChange={vi.fn()}
      onControlsChange={update}
      onSubmit={vi.fn()}
      onStop={vi.fn()}
    />
  );
}

describe("ChatComposer", () => {
  beforeEach(() => {
    vi.mocked(getModels).mockResolvedValue({
      local_models: ["qwen-local"],
      online_models: [],
      all_models: ["qwen-local"],
    });
    vi.mocked(getKnowledgeBases).mockResolvedValue([]);
    vi.mocked(getWikiStatus).mockResolvedValue({ success: true, mode: "online", stats: {} });
    vi.mocked(switchWikiMode).mockResolvedValue({
      success: true,
      mode: "online",
      stats: {},
      message: "ok",
    });
  });

  it("lets the user independently toggle RAG and Wiki", async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness />);

    const rag = screen.getByRole("switch", { name: "启用 RAG" });
    const wiki = screen.getByRole("switch", { name: "启用 Wiki" });
    expect(rag).toHaveAttribute("aria-checked", "false");
    expect(wiki).toHaveAttribute("aria-checked", "false");

    await user.click(rag);
    expect(rag).toHaveAttribute("aria-checked", "true");
    await user.click(wiki);
    expect(wiki).toHaveAttribute("aria-checked", "true");
  });
});
