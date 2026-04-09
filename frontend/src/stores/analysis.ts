import { create } from "zustand";

type State = {
  sessionId: string | null;
  setSession: (sid: string | null) => void;
};

export const useAnalysisStore = create<State>((set) => ({
  sessionId: null,
  setSession: (sid) => set({ sessionId: sid }),
}));
