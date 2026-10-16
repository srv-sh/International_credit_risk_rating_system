import { keepPreviousData, useMutation, useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { calculateStatement, getFormulas, getStatementItems, score } from '../api/endpoints'
import type { SheetKey } from '../api/types'
import FlowFooter from '../components/FlowFooter'
import Latex from '../components/Latex'
import { ErrorBox } from '../components/Status'
import { useToast } from '../components/blocks/ToastStack'
import { useAppStore } from '../store/useAppStore'

const SHEET_NAMES: Record<SheetKey, string> = { bs: 'Balance sheet', is: 'Income statement', cfs: 'Cash flow' }

export default function Formulas() {
  const formulas = useQuery({ queryKey: ['formulas'], queryFn: getFormulas, staleTime: Infinity })
  const itemsQuery = useQuery({ queryKey: ['statement-items'], queryFn: getStatementItems, staleTime: Infinity })
  const { tables, statements, records, setStatement, setResult } = useAppStore()
  const toast = useToast()
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
  const allItems = sheetItems
    ? (Object.keys(sheetItems) as SheetKey[]).flatMap((s) => sheetItems[s].map((item) => ({ sheet: s, item })))
    : []
  const [selected, setSelected] = useState('')
  const [particular, setParticular] = useState('')
  const current = allItems.find((i) => i.item === selected) ?? allItems[0]
  const sheet = current?.sheet
  const result = sheet ? statements[sheet] : undefined
  const table = sheet ? tables[sheet] : undefined
  const particularsCol = result?.particulars_column ?? (table ? Object.keys(table)[0] : '')
  const particulars = table
    ? [...new Set(table[particularsCol].map((p) => String(p ?? '').trim()).filter(Boolean))]
    : []
  const currentTerms = current && result ? result.mapping[current.item] ?? [] : []

  const recalc = useMutation({
    mutationFn: async (terms: string[]) => {
      if (!sheet || !table || !result || !current) throw new Error('Calculate this statement first')
      const mapping = { ...result.mapping, [current.item]: terms }
      return calculateStatement(sheet, { table, mapping, year_column: result.year_column })
    },
    onSuccess: (res) => setStatement(res.sheet, res),
  })

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

  const add = () => {
    if (particular && !currentTerms.some((t) => t.toLowerCase() === particular.toLowerCase())) {
      recalc.mutate([...currentTerms, particular])
    }
  }
  const remove = (term: string) => recalc.mutate(currentTerms.filter((t) => t !== term))

  const categories = [...new Set(formulas.data?.map((f) => f.category))]
  const allValues = Object.values(statements).flatMap((s) =>
    Object.entries(s.values).map(([item, v]) => ({
      item, v, missing: s.missing.includes(item), from: s.mapping[item],
    })))
  const missingTotal = allValues.filter((v) => v.missing).length

  return (
    <section className="page">
      <div className="page-head">
        <h1>Quantitative indicators</h1>
        <p className="lede">
          Each ratio below is calculated from the statement values and scored against its band.
          Continue to turn these into the final rating.
        </p>
      </div>

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
            <strong>{preview.data.quantitative_total} / {preview.data.quantitative_max}</strong>
            <em>{preview.data.quantitative_label}</em>
          </div>
        )}
      </div>

      <ErrorBox error={formulas.error} />
      <ErrorBox error={preview.error} />

      <div className="split">
        <div className="split-main">
          {categories.map((cat) => (
            <div key={cat} className="card tight">
              <div className="card-head"><h2>{cat}</h2></div>
              <div className="formula-list">
                {formulas.data!.filter((f) => f.category === cat).map((f) => {
                  const r = ratioByKey[f.key]
                  return (
                    <article key={f.key} className={`formula${r ? ` band-${r.label.toLowerCase()}` : ''}`}>
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
        </div>

        <aside className="split-side">
          <div className="card tight">
            <div className="card-head"><h2>Dictionary</h2></div>
            <p className="hint">
              Point an item at the lines it should be read from. Changing this recalculates that
              statement straight away.
            </p>
            <ErrorBox error={itemsQuery.error} />
            {current && (
              <>
                <label className="field">
                  <span>Item</span>
                  <select
                    value={current.item}
                    onChange={(e) => { setSelected(e.target.value); setParticular('') }}
                  >
                    {allItems.map((i) => <option key={i.item} value={i.item}>{i.item}</option>)}
                  </select>
                  <small>{SHEET_NAMES[current.sheet]}</small>
                </label>

                {!result ? (
                  <p className="hint">
                    Calculate the {SHEET_NAMES[current.sheet].toLowerCase()} first to edit this item.
                  </p>
                ) : (
                  <>
                    <div className="terms">
                      {currentTerms.length === 0
                        ? <em className="hint">Nothing mapped, so this item is zero.</em>
                        : currentTerms.map((t) => (
                          <button
                            key={t} type="button" className="term" disabled={recalc.isPending}
                            onClick={() => remove(t)} aria-label={`Remove ${t}`}
                          >
                            {t}<span aria-hidden="true">&times;</span>
                          </button>
                        ))}
                    </div>
                    <p className="hint">
                      Value ({result.year_column}):{' '}
                      <strong>{(result.values[current.item] ?? 0).toLocaleString()}</strong>
                    </p>
                    {currentTerms.length > 0 && result.missing.includes(current.item) && (
                      <div className="alert warn">
                        None of these lines has a number in the {result.year_column} column, so the
                        item counts as zero. Fix the cell on the {SHEET_NAMES[current.sheet]} step, or
                        map a different line.
                      </div>
                    )}
                    <label className="field">
                      <span>Add a line</span>
                      <select value={particular} onChange={(e) => setParticular(e.target.value)}>
                        <option value="">Select a line…</option>
                        {particulars.map((p) => <option key={p} value={p}>{p}</option>)}
                      </select>
                    </label>
                    <button
                      type="button" className="secondary"
                      disabled={!particular || recalc.isPending} onClick={add}
                    >
                      {recalc.isPending ? 'Updating…' : 'Add to item'}
                    </button>
                  </>
                )}
                <ErrorBox error={recalc.error} />
              </>
            )}
          </div>

          <div className="card tight">
            <div className="card-head">
              <h2>Input values</h2>
              {missingTotal > 0 && <span className="pill pill-warn">{missingTotal} missing</span>}
            </div>
            <div className="scroll scroll-tall">
              <table className="data">
                <thead><tr><th>Item</th><th className="num">Value</th><th>From</th></tr></thead>
                <tbody>
                  {allValues.map(({ item, v, missing, from }) => (
                    <tr key={item} className={missing ? 'missing' : ''}>
                      <td>{item}</td>
                      <td className="num">{v.toLocaleString()}</td>
                      <td className="from">{from?.join(' + ') || <em>not found</em>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </aside>
      </div>

      <ErrorBox error={rate.error} />
      <FlowFooter
        busy={rate.isPending}
        continueLabel={rate.isPending ? 'Calculating rating…' : 'Calculate rating'}
        blockedBy={sheetsDone === 0 ? 'Calculate at least one statement first' : null}
        onContinue={async () => {
          await rate.mutateAsync()
          return true
        }}
      />
    </section>
  )
}
