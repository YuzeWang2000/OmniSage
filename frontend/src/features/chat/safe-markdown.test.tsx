import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SafeMarkdown } from "@/features/chat/safe-markdown";

describe("SafeMarkdown", () => {
  it("does not render executable HTML, unsafe links, or remote images", () => {
    const { container } = render(
      <SafeMarkdown
        content={
          '<script>alert("xss")</script>\n\n[危险链接](javascript:alert(1))\n\n[安全链接](https://example.com)\n\n![追踪图片](https://tracker.example/pixel.png)'
        }
      />,
    );

    expect(container.querySelector("script")).not.toBeInTheDocument();
    expect(container.querySelector("img")).not.toBeInTheDocument();
    expect(screen.getByText("危险链接").closest("a")).toBeNull();
    expect(screen.getByRole("link", { name: "安全链接" })).toHaveAttribute(
      "rel",
      "noopener noreferrer nofollow",
    );
    expect(screen.getByText(/已隐藏图片：追踪图片/)).toBeInTheDocument();
  });
});
