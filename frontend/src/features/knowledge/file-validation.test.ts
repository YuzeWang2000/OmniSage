import { describe, expect, it } from "vitest";

import {
  MAX_KNOWLEDGE_FILE_BYTES,
  validateKnowledgeFile,
} from "@/features/knowledge/file-validation";

describe("validateKnowledgeFile", () => {
  it("accepts a supported document", () => {
    expect(validateKnowledgeFile(new File(["notes"], "notes.md"))).toBeNull();
  });

  it("rejects unsupported and oversized files", () => {
    expect(validateKnowledgeFile(new File(["binary"], "payload.exe"))).toMatch(/仅支持/);
    const oversized = new File(["x"], "large.pdf");
    Object.defineProperty(oversized, "size", { value: MAX_KNOWLEDGE_FILE_BYTES + 1 });
    expect(validateKnowledgeFile(oversized)).toBe("文件不能超过 10MB。");
  });
});
