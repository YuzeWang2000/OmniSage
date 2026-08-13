import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

export interface UserPreferences {
  defaultModelKey: string;
  ragEnabled: boolean;
  wikiEnabled: boolean;
}

interface PreferencesState extends UserPreferences {
  setPreferences: (preferences: UserPreferences) => void;
}

const initialPreferences: UserPreferences = {
  defaultModelKey: "",
  ragEnabled: false,
  wikiEnabled: false,
};

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      ...initialPreferences,
      setPreferences: (preferences) => set(preferences),
    }),
    {
      name: "omnisage-device-preferences",
      storage: createJSONStorage(() => localStorage),
      partialize: ({ defaultModelKey, ragEnabled, wikiEnabled }) => ({
        defaultModelKey,
        ragEnabled,
        wikiEnabled,
      }),
    },
  ),
);
