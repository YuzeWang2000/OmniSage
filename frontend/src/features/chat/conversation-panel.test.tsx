import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ConversationPanel } from "@/features/chat/conversation-panel";

const conversations = [
  {
    id: 1,
    user_id: 7,
    title: "第一段对话",
    created_at: "2026-08-11T10:00:00Z",
    updated_at: "2026-08-11T10:00:00Z",
    is_active: true,
    message_count: 2,
  },
  {
    id: 2,
    user_id: 7,
    title: "第二段对话",
    created_at: "2026-08-11T11:00:00Z",
    updated_at: "2026-08-11T11:00:00Z",
    is_active: true,
    message_count: 4,
  },
];

describe("ConversationPanel", () => {
  it("switches to the selected conversation", async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();
    render(
      <ConversationPanel
        conversations={conversations}
        activeId={1}
        loading={false}
        error={false}
        creating={false}
        mutating={false}
        onRetry={vi.fn()}
        onCreate={vi.fn()}
        onSelect={onSelect}
        onRename={vi.fn()}
        onDelete={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: "选择对话：第一段对话" })).toHaveAttribute(
      "aria-current",
      "page",
    );
    await user.click(screen.getByRole("button", { name: "选择对话：第二段对话" }));
    expect(onSelect).toHaveBeenCalledWith(2);
  });
});
