import { apiRequest } from "@/api/client";

export interface HealthResponse {
  status: "ok" | string;
}

export interface ModelsResponse {
  local_models: string[];
  online_models: string[];
  all_models: string[];
  ollama_available?: boolean;
  ollama_error?: string | null;
}

export function getHealth(signal?: AbortSignal) {
  return apiRequest<HealthResponse>({ method: "GET", url: "/health", signal });
}

export function getModels(signal?: AbortSignal) {
  return apiRequest<ModelsResponse>({ method: "GET", url: "/models", signal });
}
