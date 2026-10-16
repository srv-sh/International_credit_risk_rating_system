// Mirrors api/schemas.py

export type Label = 'Excellent' | 'Good' | 'Marginal' | 'Unacceptable'
export type SheetKey = 'bs' | 'is' | 'cfs'
export type Table = Record<string, (string | number | null)[]>

export interface OcrSheet {
  table: Table
  ocr_text: string[]
  ocr_bbox: number[][]
  image: string | null
  llm_error: string | null
}
export interface OcrResponse extends Record<SheetKey, OcrSheet> {
  source: 'backend' | 'saved'
}

export interface StatementRequest {
  table: Table
  mapping?: Record<string, string[] | null>
  year_column?: string
  use_llm?: boolean
}
export interface StatementResult {
  sheet: SheetKey
  particulars_column: string
  year_column: string
  values: Record<string, number>
  mapping: Record<string, string[]>
  missing: string[]
  markdown: string
}

export interface QualitativeQuestion {
  index: number
  category: string
  question: string
  max_score: number
  options: { label: string; score: number }[]
}
export interface CategoryScore {
  name: string
  score: number
  max_score: number
}
export interface QualitativeResult {
  answers: { index: number; category: string; question: string; answer: string; score: number; max_score: number }[]
  categories: CategoryScore[]
  total: number
  max_score: number
  percentage: number
}

export interface RecordIds {
  bs_id?: number | null
  is_id?: number | null
  cfs_id?: number | null
  llm_id?: number | null
}
export interface ScoreRequest {
  values: Record<string, number>
  qualitative?: { answers: string[] }
  save?: boolean
  records?: RecordIds
}
export interface RatioResult {
  key: string
  name: string
  category: string
  value: number | null
  score: number
  max_score: number
  label: Label
  preference: string
}
export interface ScoreResponse {
  ratios: RatioResult[]
  categories: CategoryScore[]
  quantitative_total: number
  quantitative_max: number
  quantitative_percentage: number
  quantitative_label: Label
  qualitative: QualitativeResult | null
  overall_total: number
  overall_max: number
  overall_percentage: number
  overall_label: Label
  score_id: number | null
}

export interface Formula {
  key: string
  name: string
  category: string
  latex: string[]
  inputs: string[]
  preference: string
  max_score: number
}

export interface StatementItems {
  items: Record<SheetKey, string[]>
  default_mapping: Record<string, string[]>
}

// Plotly figure JSON from fig.to_json()
export interface PlotlyFigure {
  data: Plotly.Data[]
  layout: Partial<Plotly.Layout>
}

export type Band = 'Excellent' | 'Good' | 'Marginal' | 'Unacceptable'

export interface Indicator {
  key: string
  name: string
  category: string
  group: string
  scale: number
  scoring: Record<Band, number>
}
