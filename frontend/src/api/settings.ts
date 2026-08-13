import { apiRequest } from "@/api/client";
import type { ModelCapabilities } from "@/api/system";

export interface WikiStatusResponse { success: boolean; mode: string; stats: { total_articles?: number; [key: string]: unknown } }
export interface WikiModeResponse extends WikiStatusResponse { message: string }
export interface ProviderConnection {
  id: string; provider: "ollama" | "deepseek" | "dashscope"; display_name: string; protocol: string;
  region?: string | null; base_url: string; workspace_id?: string | null; config: { manual_models?: string[]; manual_model_capabilities?: Record<string, ModelCapabilities> };
  is_active: boolean; has_credential: boolean; masked_credential?: string | null; credential_version: number;
  last_tested_at?: string | null; last_test_status?: string | null; last_test_message?: string | null;
}
export interface ConnectionPayload {
  provider: ProviderConnection["provider"]; display_name: string; region?: string | null; base_url?: string | null;
  workspace_id?: string | null; api_key?: string | null; manual_models?: string[]; is_active: boolean;
  manual_model_capabilities?: Record<string, ModelCapabilities>;
}
export function getWikiStatus(signal?: AbortSignal) { return apiRequest<WikiStatusResponse>({ method: "GET", url: "/rag/wiki/status", signal }); }
export function switchWikiMode(mode: "online" | "offline", signal?: AbortSignal) { return apiRequest<WikiModeResponse>({ method: "POST", url: "/rag/wiki/switch-mode", params: { mode }, signal }); }
export function getConnections(signal?: AbortSignal) { return apiRequest<ProviderConnection[]>({ method: "GET", url: "/ai/connections", signal }); }
export function createConnection(payload: ConnectionPayload, signal?: AbortSignal) { return apiRequest<ProviderConnection, ConnectionPayload>({ method: "POST", url: "/ai/connections", data: payload, signal }); }
export function updateConnection(id: string, payload: Partial<ConnectionPayload>, signal?: AbortSignal) { return apiRequest<ProviderConnection, Partial<ConnectionPayload>>({ method: "PUT", url: `/ai/connections/${id}`, data: payload, signal }); }
export function deleteConnection(id: string, signal?: AbortSignal) { return apiRequest<void>({ method: "DELETE", url: `/ai/connections/${id}`, signal }); }
export function testConnection(id: string, signal?: AbortSignal) { return apiRequest<{ ok: boolean; message: string }>({ method: "POST", url: `/ai/connections/${id}/test`, signal }); }
export function refreshConnectionModels(id: string, signal?: AbortSignal) { return apiRequest<unknown[]>({ method: "POST", url: `/ai/connections/${id}/models/refresh`, signal }); }
