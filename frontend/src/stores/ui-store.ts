import { create } from "zustand";

interface UiState {
  mobileNavigationOpen: boolean;
  setMobileNavigationOpen: (open: boolean) => void;
  reset: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  mobileNavigationOpen: false,
  setMobileNavigationOpen: (mobileNavigationOpen) => set({ mobileNavigationOpen }),
  reset: () => set({ mobileNavigationOpen: false }),
}));
