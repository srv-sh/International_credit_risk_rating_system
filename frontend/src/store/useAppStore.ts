import { create } from 'zustand'
import { createJSONStorage, persist } from 'zustand/middleware'
import type { OcrResponse, RecordIds, ScoreResponse, SheetKey, StatementResult, Table } from '../api/types'

export interface UserInfo {
  name: string
  address: string
  phone: string
  email: string
}

/** Replaces Streamlit's st.session_state. */
interface AppState {
  user: UserInfo
  ocr: OcrResponse | null
  tables: Partial<Record<SheetKey, Table>> // edited statements (session_state.bs / is / cfs)
  statements: Partial<Record<SheetKey, StatementResult>>
  stale: Partial<Record<SheetKey, boolean>> // table edited since its last calculation
  records: RecordIds // db ids (was json/variables.json)
  qualitativeAnswers: string[]
  result: ScoreResponse | null

  setUser: (user: UserInfo) => void
  setOcr: (ocr: OcrResponse) => void
  setTable: (sheet: SheetKey, table: Table) => void
  setStatement: (sheet: SheetKey, result: StatementResult) => void
  setRecord: (key: keyof RecordIds, id: number) => void
  setQualitativeAnswers: (answers: string[]) => void
  setResult: (result: ScoreResponse) => void
  reset: () => void
}

const initial = {
  user: { name: '', address: '', phone: '', email: '' },
  ocr: null,
  tables: {},
  statements: {},
  stale: {},
  records: {},
  qualitativeAnswers: [],
  result: null,
}

const safeLocalStorage = {
  getItem: (k: string) => {
    try { return localStorage.getItem(k) } catch { return null }
  },
  setItem: (k: string, v: string) => {
    try { localStorage.setItem(k, v) } catch { /* quota exceeded: state stays in memory */ }
  },
  removeItem: (k: string) => {
    try { localStorage.removeItem(k) } catch { /* ignore */ }
  },
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      ...initial,
      setUser: (user) => set({ user }),
      // New OCR results replace any earlier edits
      setOcr: (ocr) => set({ ocr, tables: { bs: ocr.bs.table, is: ocr.is.table, cfs: ocr.cfs.table }, statements: {}, stale: {}, result: null }),
      setTable: (sheet, table) => set((s) => ({ tables: { ...s.tables, [sheet]: table }, stale: { ...s.stale, [sheet]: !!s.statements[sheet] } })),
      setStatement: (sheet, result) => set((s) => ({ statements: { ...s.statements, [sheet]: result }, stale: { ...s.stale, [sheet]: false } })),
      setRecord: (key, id) => set((s) => ({ records: { ...s.records, [key]: id } })),
      setQualitativeAnswers: (qualitativeAnswers) => set({ qualitativeAnswers }),
      setResult: (result) => set({ result }),
      reset: () => set(initial),
    }),
    {
      // Survives refreshes and closing the tab (unlike session_state). Images are dropped to stay under the quota.
      name: 'credit-risk-session',
      storage: createJSONStorage(() => safeLocalStorage),
      partialize: (s) => ({
        ...s,
        ocr: s.ocr && {
          ...s.ocr,
          bs: { ...s.ocr.bs, image: null },
          is: { ...s.ocr.is, image: null },
          cfs: { ...s.ocr.cfs, image: null },
        },
      }),
    },
  ),
)
