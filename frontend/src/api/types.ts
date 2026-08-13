import type { components } from "@/api/schema";

export type ApiSchemas = components["schemas"];
export type AuthResponse = ApiSchemas["AuthResponse"];
export type User = ApiSchemas["UserResponse"];
export type UserLogin = ApiSchemas["UserLogin"];
export type UserCreate = ApiSchemas["UserCreate"];
export type Conversation = ApiSchemas["ConversationResponse"];
export type ChatMessage = ApiSchemas["ChatMessageResponse"];
export type KnowledgeBase = ApiSchemas["KnowledgeBaseResponse"];
export type KnowledgeBaseStats = ApiSchemas["KnowledgeBaseStats"];
export type KnowledgeFile = ApiSchemas["KnowledgeFileResponse"];
export type SearchResult = ApiSchemas["KnowledgeBaseSearchResult"];
