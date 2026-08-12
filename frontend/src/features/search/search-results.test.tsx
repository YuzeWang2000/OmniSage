import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { SearchResults } from "@/features/search/search-results";

describe("SearchResults", () => {
  it("shows structured metadata and opens the complete result", async () => {
    const user = userEvent.setup();
    render(
      <SearchResults
        loading={false}
        error={false}
        searched
        onRetry={vi.fn()}
        results={[
          {
            id: "result-1",
            title: "safety-manual.pdf",
            content: "这是检索到的完整段落内容。",
            source: "safety-manual.pdf",
            kind: "knowledge",
            score: 0.912,
            page: 8,
            section: "应急处置",
          },
        ]}
      />,
    );

    expect(screen.getByText("相关度 91.2%")).toBeInTheDocument();
    expect(screen.getByText("第 8 页")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "查看搜索结果：safety-manual.pdf" }));
    expect(screen.getByRole("dialog")).toHaveTextContent("这是检索到的完整段落内容。");
    expect(screen.getByRole("dialog")).toHaveTextContent("章节：应急处置");
  });
});
