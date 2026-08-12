import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

export interface UserPreferences {
  defaultModel: string;
  ragEnabled: boolean;
  wikiEnabled: boolean;
}

interface PreferencesState extends UserPreferences {
  setPreferences: (preferences: UserPreferences) => void;
}

const initialPreferences: UserPreferences = {
  defaultModel: "",
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
      partialize: ({ defaultModel, ragEnabled, wikiEnabled }) => ({
        defaultModel,
        ragEnabled,
        wikiEnabled,
      }),
    },
  ),
);
