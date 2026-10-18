import { Link } from 'react-router-dom'
import type { SheetKey, Table } from '../api/types'
import { Notice } from '../components/Status'
import { useAppStore } from '../store/useAppStore'

const SHEETS: { key: SheetKey; label: string }[] = [
  { key: 'bs', label: 'Balance Sheet' },
  { key: 'is', label: 'Income Sheet' },
  { key: 'cfs', label: 'Cashflow Sheet' },
]

function ReadOnlyTable({ table }: { table: Table }) {
  const cols = Object.keys(table)
  const n = cols.length ? table[cols[0]].length : 0
  return (
    <div className="scroll">
      <table className="data">
        <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>
          {Array.from({ length: n }, (_, i) => (
            <tr key={i}>{cols.map((c) => <td key={c}>{table[c][i]}</td>)}</tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/** Raw OCR output for all three statements (was pages/ocr_display.py). */
export default function Ocr() {
  const ocr = useAppStore((s) => s.ocr)
  if (!ocr) return <section className="page"><Notice>No OCR data yet. <Link to="/">Upload statements</Link> first.</Notice></section>

  return (
    <section className="page">
      <h1>OCR results <small>({ocr.source})</small></h1>
      {SHEETS.map(({ key, label }) => (
        <div key={key} className="two-col">
          <div>
            <h2>{label}</h2>
            {ocr[key].image ? <img className="statement" src={ocr[key].image!} alt={label} /> : <p className="hint">No image</p>}
            {ocr[key].llm_error && <div className="alert error">{ocr[key].llm_error}</div>}
          </div>
          <ReadOnlyTable table={ocr[key].table} />
        </div>
      ))}
    </section>
  )
}
