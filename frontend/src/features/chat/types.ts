export interface ChatCitation {
  id: string;
  title: string;
  excerpt: string;
  kind: "knowledge" | "wiki";
  source?: string | null;
  page?: number | null;
  section?: string | null;
  score?: number | null;
  url?: string | null;
}

export interface DisplayChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  reasoning?: string;
  status?: "streaming" | "error" | "stopped";
  citations?: ChatCitation[];
  citationError?: string | null;
  canRegenerate?: boolean;
}

export interface ChatControls {
  modelKey: string;
  reasoning: "off" | "auto" | "on";
  reasoningEffort: string | null;
  workflow: "direct_chat" | "grounded_chat" | "agent";
  ragEnabled: boolean;
  wikiEnabled: boolean;
  knowledgeBaseId: number | null;
}
