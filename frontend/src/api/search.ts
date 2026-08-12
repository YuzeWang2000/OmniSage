import { apiRequest } from "@/api/client";
import type { ApiSchemas } from "@/api/types";

export function searchKnowledgeBase(
  knowledgeBaseId: number,
  query: string,
  options: { topK?: number; minScore?: number; signal?: AbortSignal } = {},
) {
  return apiRequest<ApiSchemas["KnowledgeBaseSearchResponse"]>({
    method: "GET",
    url: `/rag/knowledge-bases/${knowledgeBaseId}/search`,
    params: {
      query,
      top_k: options.topK ?? 5,
      min_score: options.minScore,
    },
    signal: options.signal,
  });
}

export function searchWiki(query: string, options: { limit?: number; signal?: AbortSignal } = {}) {
  return apiRequest<ApiSchemas["WikiSearchResponse"]>({
    method: "GET",
    url: "/rag/wiki/search",
    params: { query, limit: options.limit ?? 5 },
    signal: options.signal,
  });
}
