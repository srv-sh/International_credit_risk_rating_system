import { keepPreviousData, useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { calculateStatement, getFormulas, score } from '../api/endpoints'
import type { SheetKey } from '../api/types'
import AnimatedNumber from '../components/AnimatedNumber'
import FlowFooter from '../components/FlowFooter'
import Latex from '../components/Latex'
import { ErrorBox } from '../components/Status'
import { useToast } from '../components/blocks/ToastStack'
import { useAppStore } from '../store/useAppStore'

const SHEET_NAMES: Record<SheetKey, string> = { bs: 'Balance sheet', is: 'Income statement', cfs: 'Cash flow' }

export default function Formulas() {
  const formulas = useQuery({ queryKey: ['formulas'], queryFn: getFormulas, staleTime: Infinity })
  const { tables, statements, records, setStatement, setResult } = useAppStore()
  const toast = useToast()
  const [showMissingOnly, setShowMissingOnly] = useState(false)
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

  /**
   * The final rating. This used to sit behind the qualitative questionnaire;
   * the rating is now quantitative only, so it is produced here, at the end of
   * the step that decides the inputs. Saving is best effort: if storage is
   * down the rating is still shown, just without an id.
   */
  const rate = useMutation({
    mutationFn: async () => {
      try {
        return await score({ values, records, save: true })
      } catch {
        toast.push('warn', 'Rated, but the storage service is unreachable so this was not saved.')
        return await score({ values })
      }
    },
    onSuccess: (res) => {
      setResult(res)
      toast.push('ok', `Rated ${res.quantitative_total} of ${res.quantitative_max} (${res.quantitative_label}).`)
    },
    onError: () => toast.push('error', 'The rating could not be calculated.'),
  })

  /**
   * Re-point one item at a single line, straight from the FROM column. This
   * replaced the old dictionary card: it does the same job in place. The one
   * thing it cannot do is combine several lines into one item; a combined
   * mapping that already exists keeps working and shows as one option.
   */
  const remap = useMutation({
    mutationFn: async ({ sheet: sk, item, line }: { sheet: SheetKey; item: string; line: string }) => {
      const r = statements[sk]
      const tb = tables[sk]
      if (!r || !tb) throw new Error('Calculate this statement first')
      const mapping = { ...r.mapping, [item]: line ? [line] : [] }
      return calculateStatement(sk, { table: tb, mapping, year_column: r.year_column })
    },
    onSuccess: (res) => setStatement(res.sheet, res),
    onError: () => toast.push('error', 'Could not re-map that item.'),
  })

  // Lines available per sheet, for the FROM dropdowns
  const particularsBySheet = Object.fromEntries(
    (Object.keys(statements) as SheetKey[]).map((sk) => {
      const tb = tables[sk]
      if (!tb) return [sk, []]
      const col = statements[sk]?.particulars_column ?? Object.keys(tb)[0]
      return [sk, [...new Set(tb[col].map((p) => String(p ?? '').trim()).filter(Boolean))]]
    }),
  ) as Record<SheetKey, string[]>

  const categories = [...new Set(formulas.data?.map((f) => f.category))]
  const allValues = Object.values(statements).flatMap((s) =>
    Object.entries(s.values).map(([item, v]) => ({
      sheet: s.sheet, item, v, missing: s.missing.includes(item), from: s.mapping[item],
    })))
  const missingTotal = allValues.filter((v) => v.missing).length
  const shownValues = showMissingOnly ? allValues.filter((v) => v.missing) : allValues

  return (
    <section className="page">
      <div className="page-head">
        <h1>Quantitative indicators</h1>
        <p className="lede">
          Each ratio below is calculated from the statement values and scored against its band.
          Continue to turn these into the final rating.
        </p>
      </div>

      <FlowFooter
        busy={rate.isPending}
        continueLabel={rate.isPending ? 'Calculating rating…' : 'Calculate rating'}
        blockedBy={sheetsDone === 0 ? 'Calculate at least one statement first' : null}
        onContinue={async () => {
          await rate.mutateAsync()
          return true
        }}
      />
      <ErrorBox error={rate.error} />

      <div className="stat-row">
        <div className="stat">
          <span>Statements calculated</span>
          <strong>{sheetsDone} of 3</strong>
          {sheetsDone < 3 && <em>Items from the rest count as zero</em>}
        </div>
        <div className="stat">
          <span>Values found</span>
          <strong>{allValues.length - missingTotal} of {allValues.length}</strong>
          {missingTotal > 0 && <em>{missingTotal} counted as zero</em>}
        </div>
        {preview.data && (
          <div className={`stat stat-accent band-${preview.data.quantitative_label.toLowerCase()}`}>
            <span>Rating so far</span>
            <strong><AnimatedNumber value={preview.data.quantitative_total} decimals={1} /> / {preview.data.quantitative_max}</strong>
            <em>{preview.data.quantitative_label}</em>
          </div>
        )}
      </div>

      <ErrorBox error={formulas.error} />
      <ErrorBox error={preview.error} />

      <div className="card tight">
        <div className="card-head">
          <h2>Input values</h2>
          <label className="checkbox checkbox-inline">
            <input
              type="checkbox"
              checked={showMissingOnly}
              onChange={(e) => setShowMissingOnly(e.target.checked)}
            />
            <span>Show missing only</span>
          </label>
          {missingTotal > 0 && <span className="pill pill-warn">{missingTotal} missing</span>}
        </div>
        <p className="hint">
          Each value names the statement line it is read from. Pick a different line to re-point it;
          the statement recalculates straight away. A missing item counts as zero until it is mapped.
        </p>
        <div className="scroll scroll-tall">
          <table className="data sticky">
            <thead><tr><th>Item</th><th className="num">Value</th><th>From</th></tr></thead>
            <tbody>
              {shownValues.map(({ sheet: sk, item, v, missing, from }) => {
                const lines = particularsBySheet[sk] ?? []
                const single = from?.length === 1 ? from[0] : null
                return (
                  <tr key={item} className={missing ? 'missing' : ''}>
                    <td>
                      {item}
                      <small className="row-meta">{SHEET_NAMES[sk]}</small>
                    </td>
                    <td className="num tabular">{v.toLocaleString()}</td>
                    <td className="from">
                      <select
                        className="from-select"
                        aria-label={`Line ${item} is read from`}
                        disabled={remap.isPending}
                        value={from && from.length > 1 ? '__multi__' : single ?? ''}
                        onChange={(e) => {
                          if (e.target.value !== '__multi__') remap.mutate({ sheet: sk, item, line: e.target.value })
                        }}
                      >
                        {from && from.length > 1 && <option value="__multi__">{from.join(' + ')}</option>}
                        <option value="">not mapped</option>
                        {single && !lines.includes(single) && <option value={single}>{single}</option>}
                        {lines.map((p) => <option key={p} value={p}>{p}</option>)}
                      </select>
                    </td>
                  </tr>
                )
              })}
              {shownValues.length === 0 && (
                <tr><td colSpan={3} className="empty-cell">Nothing missing. Every item has a value.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {categories.map((cat) => (
        <div key={cat} className="card tight">
          <div className="card-head"><h2>{cat}</h2></div>
          <div className="formula-rows">
            {formulas.data!.filter((f) => f.category === cat).map((f) => {
              const r = ratioByKey[f.key]
              return (
                <article key={f.key} className={`formula-row${r ? ` band-${r.label.toLowerCase()}` : ''}`}>
                  <header>
                    <h3>{f.name}</h3>
                    <span className="formula-meta">{f.preference} &middot; max {f.max_score}</span>
                  </header>
                  <div className="formula-math">
                    {f.latex.map((tex) => <Latex key={tex} math={tex} />)}
                  </div>
                  {r && (
                    <footer className="formula-result">
                      <span className="formula-value">
                        {r.value === null
                          ? 'undefined'
                          : r.value.toLocaleString(undefined, { maximumFractionDigits: 4 })}
                      </span>
                      <span className="pill pill-band">{r.label}</span>
                      <span className="formula-score">{r.score} / {r.max_score}</span>
                    </footer>
                  )}
                </article>
              )
            })}
          </div>
        </div>
      ))}
    </section>
  )
}
