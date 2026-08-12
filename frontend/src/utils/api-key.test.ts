import { describe, expect, it } from "vitest";

import { maskApiKey } from "@/utils/api-key";

describe("maskApiKey", () => {
  it("returns a fixed mask that cannot disclose a stored credential", () => {
    const mask = maskApiKey();

    expect(mask).toBe("•••• •••• ••••");
    expect(mask).not.toContain("sk-");
    expect(mask).not.toMatch(/[A-Za-z0-9]{8}/);
  });
});
