import { keepPreviousData, useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { calculateStatement, getFormulas, getStatementItems, score } from '../api/endpoints'
import type { SheetKey } from '../api/types'
import Latex from '../components/Latex'
import { ErrorBox } from '../components/Status'
import { useAppStore } from '../store/useAppStore'

const SHEET_NAMES: Record<SheetKey, string> = { bs: 'Balance sheet', is: 'Income statement', cfs: 'Cash flow' }

export default function Formulas() {
  const formulas = useQuery({ queryKey: ['formulas'], queryFn: getFormulas, staleTime: Infinity })
  const itemsQuery = useQuery({ queryKey: ['statement-items'], queryFn: getStatementItems, staleTime: Infinity })
  const { tables, statements, setStatement } = useAppStore()
  const values = Object.assign({}, ...Object.values(statements).map((s) => s.values)) as Record<string, number>
  const sheetsDone = Object.keys(statements).length

  // Live ratio preview from the current values (not saved)
  const preview = useQuery({
    queryKey: ['score-preview', values],
    queryFn: () => score({ values }),
    enabled: sheetsDone > 0,
    placeholderData: keepPreviousData,
  })
  const ratioByKey = Object.fromEntries((preview.data?.ratios ?? []).map((r) => [r.key, r]))

  // Dictionary updater (was the right column of pages/formula.py)
  const sheetItems = itemsQuery.data?.items
  const allItems = sheetItems ? (Object.keys(sheetItems) as SheetKey[]).flatMap((s) => sheetItems[s].map((item) => ({ sheet: s, item }))) : []
  const [selected, setSelected] = useState('')
  const [particular, setParticular] = useState('')
  const current = allItems.find((i) => i.item === selected) ?? allItems[0]
  const sheet = current?.sheet
  const result = sheet ? statements[sheet] : undefined
  const table = sheet ? tables[sheet] : undefined
  const particularsCol = result?.particulars_column ?? (table ? Object.keys(table)[0] : '')
  const particulars = table ? [...new Set(table[particularsCol].map((p) => String(p ?? '').trim()).filter(Boolean))] : []
  const currentTerms = current && result ? result.mapping[current.item] ?? [] : []

  const recalc = useMutation({
    mutationFn: async (terms: string[]) => {
      if (!sheet || !table || !result || !current) throw new Error('Calculate this statement first')
      const mapping = { ...result.mapping, [current.item]: terms }
      return calculateStatement(sheet, { table, mapping, year_column: result.year_column })
    },
    onSuccess: (res) => setStatement(res.sheet, res),
  })

  const add = () => {
    if (particular && !currentTerms.some((t) => t.toLowerCase() === particular.toLowerCase())) recalc.mutate([...currentTerms, particular])
  }
  const remove = (term: string) => recalc.mutate(currentTerms.filter((t) => t !== term))

  const categories = [...new Set(formulas.data?.map((f) => f.category))]

  return (
    <section className="page">
      <h1>Calculation of Quantitative Indicators</h1>
      <ErrorBox error={formulas.error} />
      <div className="two-col">
        <div>
          <h2>Formulas</h2>
          {categories.map((cat) => (
            <div key={cat}>
              <h3>{cat}</h3>
              {formulas.data!.filter((f) => f.category === cat).map((f) => {
                const r = ratioByKey[f.key]
                return (
                  <div key={f.key} className="formula">
                    <h4>{f.name} <small>{f.preference} · max {f.max_score}</small></h4>
                    {f.latex.map((tex) => <Latex key={tex} math={tex} />)}
                    {r && (
                      <p className="hint">
                        = <strong>{r.value === null ? '∞' : r.value.toLocaleString(undefined, { maximumFractionDigits: 4 })}</strong>
                        {' '}→ score {r.score}/{r.max_score} ({r.label})
                      </p>
                    )}
                  </div>
                )
              })}
            </div>
          ))}
        </div>
        <div>
          <h2>Dictionary updater</h2>
          <ErrorBox error={itemsQuery.error} />
          {current && (
            <>
              <div className="actions">
                <label>
                  Item{' '}
                  <select value={current.item} onChange={(e) => { setSelected(e.target.value); setParticular('') }}>
                    {allItems.map((i) => <option key={i.item} value={i.item}>{i.item}</option>)}
                  </select>
                </label>
                <span className="hint">{SHEET_NAMES[current.sheet]}</span>
              </div>
              {!result ? (
                <p className="hint">Calculate the {SHEET_NAMES[current.sheet].toLowerCase()} first to edit this item.</p>
              ) : (
                <>
                  <p>
                    Current particulars:{' '}
                    {currentTerms.length === 0 && <em>none (valued at 0)</em>}
                    {currentTerms.map((t) => (
                      <button key={t} title="Remove" disabled={recalc.isPending} onClick={() => remove(t)}>{t} ×</button>
                    ))}
                  </p>
                  <p className="hint">
                    Value ({result.year_column}): <strong>{(result.values[current.item] ?? 0).toLocaleString()}</strong>
                  </p>
                  {currentTerms.length > 0 && result.missing.includes(current.item) && (
                    <div className="alert">
                      None of these particulars has a number in the "{result.year_column}" column, so the item counts as 0.
                      Fix the cell on the {SHEET_NAMES[current.sheet]} page, or pick another particular.
                    </div>
                  )}
                  <div className="actions">
                    <label>
                      Particular{' '}
                      <select value={particular} onChange={(e) => setParticular(e.target.value)}>
                        <option value="">Select…</option>
                        {particulars.map((p) => <option key={p} value={p}>{p}</option>)}
                      </select>
                    </label>
                    <button className="primary" disabled={!particular || recalc.isPending} onClick={add}>
                      {recalc.isPending ? 'Updating…' : 'Add value'}
                    </button>
                  </div>
                </>
              )}
              <ErrorBox error={recalc.error} />
            </>
          )}

          <h2>Input values</h2>
          {sheetsDone < 3 && <p className="hint">{sheetsDone}/3 statements calculated. Missing items count as 0.</p>}
          <ErrorBox error={preview.error} />
          <table className="data">
            <thead><tr><th>Item</th><th>Value</th><th>From particulars</th></tr></thead>
            <tbody>
              {Object.values(statements).flatMap((s) => Object.entries(s.values).map(([item, v]) => (
                <tr key={item} className={s.missing.includes(item) ? 'missing' : ''}>
                  <td>{item}</td>
                  <td className="num">{v.toLocaleString()}</td>
                  <td>{s.mapping[item]?.join(' + ') || 'not found'}</td>
                </tr>
              )))}
            </tbody>
          </table>
          {preview.data && (
            <p>Quantitative score: <strong>{preview.data.quantitative_total}/{preview.data.quantitative_max}</strong> ({preview.data.quantitative_label})</p>
          )}
          <Link className="button primary" to="/parameters">Next</Link>
        </div>
      </div>
    </section>
  )
}
