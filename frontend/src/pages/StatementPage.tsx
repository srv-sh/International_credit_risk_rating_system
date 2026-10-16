import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { calculateStatement, storeOcrData } from '../api/endpoints'
import type { RecordIds, SheetKey } from '../api/types'
import EditableTable from '../components/EditableTable'
import { ErrorBox, Notice } from '../components/Status'
import { useAppStore } from '../store/useAppStore'

const RECORD_KEY: Record<SheetKey, keyof RecordIds> = { bs: 'bs_id', is: 'is_id', cfs: 'cfs_id' }

interface Props {
  sheet: SheetKey
  title: string
  next: string
}

/** Shared page for the three statements (was pages/bs.py, is.py, cfs.py). */
export default function StatementPage({ sheet, title, next }: Props) {
  const navigate = useNavigate()
  const { ocr, tables, statements, stale, setTable, setStatement, setRecord } = useAppStore()
  const table = tables[sheet]
  const result = statements[sheet]
  const [yearColumn, setYearColumn] = useState<string>('')
  const [saveWarning, setSaveWarning] = useState<string | null>(null)

  const calculate = useMutation({
    mutationFn: async () => {
      const res = await calculateStatement(sheet, { table: table!, year_column: yearColumn || undefined })
      setStatement(sheet, res)
      try {
        const stored = await storeOcrData({ sheet, page_number: 1, response: res.markdown })
        setRecord(RECORD_KEY[sheet], stored.id)
        setSaveWarning(null)
      } catch {
        setSaveWarning('Calculated, but the storage API (db_api) is not reachable, so nothing was saved.')
      }
      return res
    },
  })

  if (!table) {
    return <section className="page"><Notice>No {title.toLowerCase()} data yet. <Link to="/">Upload statements</Link> first.</Notice></section>
  }

  const valueColumns = Object.keys(table).slice(1)

  return (
    <section className="page">
      <h1>{title}</h1>
      <div className="two-col">
        <div>
          {ocr?.[sheet].image
            ? <img className="statement" src={ocr[sheet].image!} alt={title} />
            : <p className="hint">Image not available (images are not kept after a page refresh).</p>}
        </div>
        <div>
          <EditableTable table={table} onChange={(t) => setTable(sheet, t)} />
          <div className="actions">
            <label>
              Year column{' '}
              <select value={yearColumn} onChange={(e) => setYearColumn(e.target.value)}>
                <option value="">{valueColumns[0] ?? '—'} (default)</option>
                {valueColumns.slice(1).map((c) => <option key={c} value={c}>{c}</option>)}
              </select>
            </label>
            <button className="primary" disabled={calculate.isPending} onClick={() => calculate.mutate()}>
              {calculate.isPending ? 'Calculating…' : 'Calculate'}
            </button>
            <button onClick={() => navigate(next)}>Next</button>
          </div>
          {stale[sheet] && <div className="alert">The table changed since the last calculation. Click Calculate to update the values.</div>}
          <ErrorBox error={calculate.error} />
          {saveWarning && <div className="alert">{saveWarning}</div>}
        </div>
      </div>

      {result && (
        <>
          <h2>Extracted values ({result.year_column})</h2>
          <table className="data">
            <thead><tr><th>Item</th><th>Value</th><th>From particulars</th></tr></thead>
            <tbody>
              {Object.entries(result.values).map(([item, value]) => (
                <tr key={item} className={result.missing.includes(item) ? 'missing' : ''}>
                  <td>{item}</td>
                  <td className="num">{value.toLocaleString()}</td>
                  <td>{result.mapping[item].join(' + ') || 'not found'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  )
}
