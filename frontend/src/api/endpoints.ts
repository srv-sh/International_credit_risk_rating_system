import { api, db } from './client'
import type {
  Formula, Indicator, OcrResponse, PlotlyFigure, QualitativeQuestion, QualitativeResult, ScoreRequest, ScoreResponse,
  SheetKey, StatementItems, StatementRequest, StatementResult,
} from './types'

const STATEMENT_PATH: Record<SheetKey, string> = {
  bs: '/balance-sheet/calculate',
  is: '/income/calculate',
  cfs: '/cashflow/calculate',
}

export async function runOcr(files: Record<SheetKey, File> | null, useSaved?: boolean) {
  const form = new FormData()
  if (files) {
    form.append('balance_sheet', files.bs)
    form.append('cash_flow', files.cfs)
    form.append('income_statement', files.is)
  }
  const params = useSaved === undefined ? {} : { use_saved: useSaved }
  return (await api.post<OcrResponse>('/ocr', form, { params })).data
}

export const calculateStatement = async (sheet: SheetKey, body: StatementRequest) =>
  (await api.post<StatementResult>(STATEMENT_PATH[sheet], body)).data

export const getStatementItems = async () => (await api.get<StatementItems>('/statements/items')).data

export const getQualitativeQuestions = async () =>
  (await api.get<QualitativeQuestion[]>('/qualitative/questions')).data

export const scoreQualitative = async (answers: string[]) =>
  (await api.post<QualitativeResult>('/qualitative/score', { answers })).data

export const score = async (body: ScoreRequest) => (await api.post<ScoreResponse>('/score', body)).data

export const getFormulas = async () => (await api.get<Formula[]>('/formulas')).data

export const getIndicators = async () => (await api.get<Indicator[]>('/indicators')).data

export const saveIndicators = async (rows: Indicator[]) => (await api.put<Indicator[]>('/indicators', rows)).data

export const getGraphIds = async () => (await api.get<string[]>('/graphs')).data

export const getGraph = async (graphId: string, scoreId: number) =>
  (await api.get<PlotlyFigure>(`/graphs/${graphId}`, { params: { score_id: scoreId } })).data

export const buildGraph = async (graphId: string, result: ScoreResponse) =>
  (await api.post<PlotlyFigure>(`/graphs/${graphId}`, result)).data

// ---- storage (db_api) ----

export const storeOcrData = async (payload: { sheet: SheetKey; page_number?: number; response?: string }) =>
  (await db.post<{ id: number }>('/store_ocr_data', payload)).data
