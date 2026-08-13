import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { KnowledgeDetail } from "@/features/knowledge/knowledge-detail";
import { createTestQueryClient, renderWithProviders } from "@/test/render";

const knowledgeBase = {
  id: 1,
  user_id: 2,
  name: "法律法规模",
  description: "旧描述",
  embedding_model: "nomic-embed-text",
  vector_db_path: "vectors",
  file_count: 0,
  document_count: 0,
  is_active: true,
  created_at: "2026-08-13T00:00:00Z",
  updated_at: "2026-08-13T00:00:00Z",
};

vi.mock("@/api/knowledge", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/api/knowledge")>();
  return { ...actual, getKnowledgeFiles: vi.fn().mockResolvedValue({ files: [] }) };
});

describe("KnowledgeDetail", () => {
  it("edits a knowledge-base display name", async () => {
    const update = vi.fn().mockResolvedValue(undefined);
    const user = userEvent.setup();
    const queryClient = createTestQueryClient();
    queryClient.setQueryDefaults(["knowledge", 1, "files"], { staleTime: Infinity });
    queryClient.setQueryData(["knowledge", 1, "files"], { files: [] });
    renderWithProviders(
      <KnowledgeDetail
        knowledgeBase={knowledgeBase}
        deletingKnowledgeBase={false}
        onDeleteKnowledgeBase={vi.fn()}
        updatingKnowledgeBase={false}
        onUpdateKnowledgeBase={update}
      />,
      { queryClient },
    );
    await user.click(screen.getByRole("button", { name: "重命名" }));
    const name = screen.getByLabelText("知识库名称");
    await user.clear(name);
    await user.type(name, "法律法规");
    await user.click(screen.getByRole("button", { name: "保存" }));
    expect(update).toHaveBeenCalledWith("法律法规", "旧描述");
  });
});
