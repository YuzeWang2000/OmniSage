import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import type { User } from "@/api/types";

interface AuthState {
  token: string | null;
  user: User | null;
  hasHydrated: boolean;
  setAuthenticated: (token: string, user: User) => void;
  clearAuth: () => void;
  markHydrated: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      hasHydrated: false,
      setAuthenticated: (token, user) => set({ token, user }),
      clearAuth: () => set({ token: null, user: null }),
      markHydrated: () => set({ hasHydrated: true }),
    }),
    {
      name: "omnisage-auth",
      storage: createJSONStorage(() => sessionStorage),
      partialize: ({ token, user }) => ({ token, user }),
      onRehydrateStorage: () => (state) => state?.markHydrated(),
    },
  ),
);
