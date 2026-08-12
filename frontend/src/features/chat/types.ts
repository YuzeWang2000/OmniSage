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
  status?: "streaming" | "error" | "stopped";
  citations?: ChatCitation[];
  citationError?: string | null;
  canRegenerate?: boolean;
}

export interface ChatControls {
  model: string;
  ragEnabled: boolean;
  wikiEnabled: boolean;
  knowledgeBaseId: number | null;
}
