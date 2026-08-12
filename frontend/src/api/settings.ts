import { apiRequest } from "@/api/client";
import type { ApiKey, ApiSchemas } from "@/api/types";

export interface WikiStatusResponse {
  success: boolean;
  mode: "online" | "offline" | "unavailable" | string;
  stats: {
    total_articles?: number;
    database_size_mb?: number;
    [key: string]: unknown;
  };
}

export interface WikiModeResponse extends WikiStatusResponse {
  message: string;
}

export function getWikiStatus(signal?: AbortSignal) {
  return apiRequest<WikiStatusResponse>({ method: "GET", url: "/rag/wiki/status", signal });
}

export function switchWikiMode(mode: "online" | "offline", signal?: AbortSignal) {
  return apiRequest<WikiModeResponse>({
    method: "POST",
    url: "/rag/wiki/switch-mode",
    params: { mode },
    signal,
  });
}

export function getApiKeys(userId: number, signal?: AbortSignal) {
  return apiRequest<ApiSchemas["ApiKeyListResponse"]>({
    method: "GET",
    url: `/api-keys/user/${userId}`,
    params: { include_inactive: true },
    signal,
  }).then((response) => response.api_keys);
}

export function createApiKey(payload: ApiSchemas["ApiKeyCreate"], signal?: AbortSignal) {
  return apiRequest<ApiKey, ApiSchemas["ApiKeyCreate"]>({
    method: "POST",
    url: "/api-keys/",
    data: payload,
    signal,
  });
}

export function updateApiKey(
  apiKeyId: number,
  payload: ApiSchemas["ApiKeyUpdate"],
  signal?: AbortSignal,
) {
  return apiRequest<ApiKey, ApiSchemas["ApiKeyUpdate"]>({
    method: "PUT",
    url: `/api-keys/${apiKeyId}`,
    data: payload,
    signal,
  });
}

export function deleteApiKey(apiKeyId: number, signal?: AbortSignal) {
  return apiRequest<{ message: string }>({
    method: "DELETE",
    url: `/api-keys/${apiKeyId}`,
    signal,
  });
}
