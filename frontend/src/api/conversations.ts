import { apiRequest } from "@/api/client";
import type { ApiSchemas, Conversation } from "@/api/types";

export function getConversations(
  userId: number,
  options: { limit?: number; signal?: AbortSignal } = {},
) {
  return apiRequest<ApiSchemas["ConversationListResponse"]>({
    method: "GET",
    url: `/conversations/user/${userId}`,
    params: options.limit ? { limit: options.limit } : undefined,
    signal: options.signal,
  }).then((response) => response.conversations);
}

export function createConversation(title = "新对话", signal?: AbortSignal) {
  return apiRequest<Conversation, ApiSchemas["ConversationCreate"]>({
    method: "POST",
    url: "/conversations/",
    data: { title },
    signal,
  });
}

export function getConversationMessages(conversationId: number, signal?: AbortSignal) {
  return apiRequest<ApiSchemas["ChatHistoryResponse"]>({
    method: "GET",
    url: `/conversations/${conversationId}/messages`,
    signal,
  });
}

export function renameConversation(conversationId: number, title: string, signal?: AbortSignal) {
  return apiRequest<{ message: string; title: string }, ApiSchemas["ConversationUpdate"]>({
    method: "PATCH",
    url: `/conversations/${conversationId}`,
    data: { title },
    signal,
  });
}

export function deleteConversation(conversationId: number, signal?: AbortSignal) {
  return apiRequest<{ message: string }>({
    method: "DELETE",
    url: `/conversations/${conversationId}`,
    signal,
  });
}
