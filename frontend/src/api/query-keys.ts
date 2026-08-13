export const queryKeys = {
  system: {
    health: ["system", "health"] as const,
    models: ["system", "models"] as const,
    chatModels: ["system", "models", "chat"] as const,
  },
  conversations: {
    all: (userId: number) => ["conversations", userId] as const,
    recent: (userId: number) => ["conversations", userId, "recent"] as const,
    messages: (conversationId: number) => ["conversations", conversationId, "messages"] as const,
  },
  knowledge: {
    all: (userId: number) => ["knowledge", userId] as const,
    recent: (userId: number) => ["knowledge", userId, "recent"] as const,
    stats: (userId: number) => ["knowledge", userId, "stats"] as const,
    files: (knowledgeBaseId: number) => ["knowledge", knowledgeBaseId, "files"] as const,
  },
  settings: {
    wiki: ["settings", "wiki"] as const,
    connections: ["settings", "connections"] as const,
  },
  search: {
    results: (source: "wiki" | "knowledge", target: number | null, query: string) =>
      ["search", source, target, query] as const,
  },
};
