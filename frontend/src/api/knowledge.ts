import { apiRequest, uploadRequest } from "@/api/client";
import type { ApiSchemas, KnowledgeBase, KnowledgeBaseStats } from "@/api/types";

export function getKnowledgeBases(
  userId: number,
  options: { limit?: number; signal?: AbortSignal } = {},
) {
  return apiRequest<ApiSchemas["KnowledgeBaseListResponse"]>({
    method: "GET",
    url: `/rag/knowledge-bases/${userId}`,
    params: options.limit ? { limit: options.limit } : undefined,
    signal: options.signal,
  }).then((response) => response.knowledge_bases);
}

export function getKnowledgeStats(userId: number, signal?: AbortSignal) {
  return apiRequest<KnowledgeBaseStats>({
    method: "GET",
    url: `/rag/stats/${userId}`,
    signal,
  });
}

export function createKnowledgeBase(
  payload: Pick<ApiSchemas["KnowledgeBaseCreate"], "name" | "description" | "embedding_model">,
  signal?: AbortSignal,
) {
  return apiRequest<KnowledgeBase, typeof payload>({
    method: "POST",
    url: "/rag/knowledge-bases",
    data: payload,
    signal,
  });
}

export function deleteKnowledgeBase(knowledgeBaseId: number, signal?: AbortSignal) {
  return apiRequest<{ message: string }>({
    method: "DELETE",
    url: `/rag/knowledge-bases/${knowledgeBaseId}`,
    signal,
  });
}

export function updateKnowledgeBase(
  knowledgeBaseId: number,
  payload: Pick<ApiSchemas["KnowledgeBaseUpdate"], "name" | "description">,
  signal?: AbortSignal,
) {
  return apiRequest<KnowledgeBase, typeof payload>({
    method: "PATCH",
    url: `/rag/knowledge-bases/${knowledgeBaseId}`,
    data: payload,
    signal,
  });
}

export function getKnowledgeFiles(knowledgeBaseId: number, signal?: AbortSignal) {
  return apiRequest<ApiSchemas["KnowledgeFileListResponse"]>({
    method: "GET",
    url: `/rag/knowledge-bases/${knowledgeBaseId}/files`,
    signal,
  });
}

export function uploadKnowledgeFile(
  knowledgeBaseId: number,
  file: File,
  options: { signal?: AbortSignal; onProgress?: (progress: number) => void } = {},
) {
  const data = new FormData();
  data.append("file", file);
  return uploadRequest<ApiSchemas["FileUploadResponse"]>({
    method: "POST",
    url: `/rag/knowledge-bases/${knowledgeBaseId}/files`,
    data,
    signal: options.signal,
    onProgress: options.onProgress,
  });
}

export function deleteKnowledgeFile(knowledgeBaseId: number, fileId: number, signal?: AbortSignal) {
  return apiRequest<{ message: string }>({
    method: "DELETE",
    url: `/rag/knowledge-bases/${knowledgeBaseId}/files/${fileId}`,
    signal,
  });
}
