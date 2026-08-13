import { apiRequest } from "@/api/client";

export interface HealthResponse { status: string }
export interface ModelCapabilities {
  streaming?: boolean | null; reasoning?: boolean | null; reasoning_toggle?: boolean | null;
  reasoning_efforts: string[]; tools?: boolean | null; structured_output?: boolean | null;
  json_output?: boolean | null; function_calling?: boolean | null;
}
export interface AIModel {
  key: string; connection_id: string; provider: "ollama" | "deepseek" | "dashscope"; id: string;
  display_name: string; source: "provider_api" | "provider_override" | "manual" | "local_runtime";
  available: boolean; task_types: string[]; input_modalities: string[]; output_modalities: string[];
  capabilities: ModelCapabilities; metadata?: Record<string, unknown>; stale: boolean; vision: boolean;
}
export function getHealth(signal?: AbortSignal) { return apiRequest<HealthResponse>({ method: "GET", url: "/health", signal }); }
export function getModels(signal?: AbortSignal, filters: { chatOnly?: boolean } = {}) {
  const params = filters.chatOnly ? { task_type: "chat", input_modality: "text", available_only: true } : { available_only: true };
  return apiRequest<AIModel[]>({ method: "GET", url: "/ai/models", params, signal });
}
