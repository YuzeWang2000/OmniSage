import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { KnowledgeList } from "@/features/knowledge/knowledge-list";

describe("KnowledgeList", () => {
  it("shows an actionable empty state", () => {
    render(
      <KnowledgeList
        items={[]}
        activeId={null}
        loading={false}
        error={false}
        onRetry={vi.fn()}
        onCreate={vi.fn()}
        onSelect={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "还没有知识库" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "创建知识库" })).toBeInTheDocument();
  });
});
