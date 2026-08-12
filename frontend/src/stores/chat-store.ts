import { create } from "zustand";

interface ChatState {
  activeConversationId: number | null;
  setActiveConversationId: (id: number | null) => void;
  reset: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  activeConversationId: null,
  setActiveConversationId: (activeConversationId) => set({ activeConversationId }),
  reset: () => set({ activeConversationId: null }),
}));
