export const MAX_KNOWLEDGE_FILE_BYTES = 10 * 1024 * 1024;
export const KNOWLEDGE_FILE_EXTENSIONS = ["pdf", "txt", "md", "doc", "docx"] as const;

export function validateKnowledgeFile(file: File) {
  const extension = file.name.split(".").pop()?.toLowerCase();
  if (
    !extension ||
    !KNOWLEDGE_FILE_EXTENSIONS.includes(extension as (typeof KNOWLEDGE_FILE_EXTENSIONS)[number])
  ) {
    return "仅支持 PDF、TXT、Markdown、DOC 和 DOCX 文件。";
  }
  if (file.size <= 0) return "文件为空，无法上传。";
  if (file.size > MAX_KNOWLEDGE_FILE_BYTES) return "文件不能超过 10MB。";
  return null;
}
