import { useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import type { Label, RatioResult, SheetKey } from '../api/types'
import AnimatedNumber from '../components/AnimatedNumber'
import FlowFooter from '../components/FlowFooter'
import Reveal from '../components/Reveal'
import { Notice } from '../components/Status'
import RadialGauge from '../components/blocks/RadialGauge'
import StackedBars from '../components/blocks/StackedBars'
import { useToast } from '../components/blocks/ToastStack'
import { useAppStore } from '../store/useAppStore'

const SHEETS: { key: SheetKey; label: string; path: string }[] = [
  { key: 'bs', label: 'Balance sheet', path: '/balance-sheet' },
  { key: 'is', label: 'Income statement', path: '/income-sheet' },
  { key: 'cfs', label: 'Cash flow statement', path: '/cashflow-sheet' },
]

const BANDS: Label[] = ['Excellent', 'Good', 'Marginal', 'Unacceptable']

const fmt = (v: number | null) =>
  v === null ? 'undefined' : v.toLocaleString(undefined, { maximumFractionDigits: 4 })

type SortKey = 'category' | 'name' | 'value' | 'score'

/** All inputs and the final rating on one page. */
export default function Summary() {
  const navigate = useNavigate()
  const toast = useToast()
  const { user, statements, stale, result, reset } = useAppStore()
  const [band, setBand] = useState<Label | 'all'>('all')
  const [sort, setSort] = useState<{ key: SortKey; dir: 1 | -1 }>({ key: 'category', dir: 1 })
  const [confirming, setConfirming] = useState(false)

  // Stable identity, otherwise the memos below recompute on every render.
  const ratios = useMemo(() => result?.ratios ?? [], [result])

  // Band counts drive the filter chips, so they stay honest even when a filter
  // is active.
  const counts = useMemo(() => {
    const map = new Map<Label, number>(BANDS.map((b) => [b, 0]))
    ratios.forEach((r) => map.set(r.label, (map.get(r.label) ?? 0) + 1))
    return map
  }, [ratios])

  const shown = useMemo(() => {
    const filtered = band === 'all' ? ratios : ratios.filter((r) => r.label === band)
    const by = (r: RatioResult) => {
      switch (sort.key) {
        case 'name': return r.name
        case 'category': return r.category
        case 'value': return r.value ?? Number.NEGATIVE_INFINITY
        case 'score': return r.max_score ? r.score / r.max_score : 0
      }
    }
    return [...filtered].sort((a, b) => {
      const x = by(a), y = by(b)
      if (x === y) return a.name.localeCompare(b.name)
      return (typeof x === 'string' ? x.localeCompare(y as string) : x < (y as number) ? -1 : 1) * sort.dir
    })
  }, [ratios, band, sort])

  if (!result) {
    return (
      <section className="page">
        <Notice>
          No rating yet. Calculate it on the <Link to="/formulas">indicators step</Link> first.
        </Notice>
      </section>
    )
  }

  const staleSheets = SHEETS.filter((s) => stale[s.key])

  const toggleSort = (key: SortKey) =>
    setSort((s) => ({ key, dir: s.key === key && s.dir === 1 ? -1 : 1 }))
  const ariaSort = (key: SortKey) =>
    sort.key === key ? (sort.dir === 1 ? 'ascending' : 'descending') : 'none'

  const exportCsv = () => {
    const rows = [
      ['Category', 'Indicator', 'Value', 'Score', 'Max score', 'Band', 'Preference'],
      ...ratios.map((r) => [r.category, r.name, r.value === null ? '' : String(r.value),
        String(r.score), String(r.max_score), r.label, r.preference]),
      [],
      ['Quantitative total', String(result.quantitative_total), 'of', String(result.quantitative_max),
        `${result.quantitative_percentage.toFixed(2)}%`, result.quantitative_label],
    ]
    const csv = rows.map((r) => r.map((c) => (/[",\n]/.test(c) ? `"${c.replace(/"/g, '""')}"` : c)).join(',')).join('\n')
    const url = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `credit-rating-${result.score_id ?? 'unsaved'}.csv`
    a.click()
    URL.revokeObjectURL(url)
    toast.push('ok', 'Ratio table exported as CSV.')
  }

  const startOver = () => {
    reset()
    navigate('/')
  }

  return (
    <section className="page">
      <div className="page-head">
        <h1>Rating summary</h1>
        <p className="lede">
          The final rating for {user.name || 'this applicant'} and every input behind it.
        </p>
      </div>

      <FlowFooter>
        <button type="button" className="ghost" onClick={exportCsv}>Export CSV</button>
        <button type="button" className="ghost" onClick={() => window.print()}>Print</button>
        {confirming ? (
          <>
            <p className="flow-note">Clear this rating and start again?</p>
            <button type="button" className="ghost" onClick={() => setConfirming(false)}>Cancel</button>
            <button type="button" className="danger" onClick={startOver}>Discard and restart</button>
          </>
        ) : (
          <button type="button" className="secondary" onClick={() => setConfirming(true)}>Start over</button>
        )}
      </FlowFooter>

      {staleSheets.length > 0 && (
        <div className="alert warn" role="status">
          Edited after this rating was calculated:{' '}
          {staleSheets.map((s, i) => (
            <span key={s.key}>{i > 0 && ', '}<Link to={s.path}>{s.label}</Link></span>
          ))}
          . Recalculate them, then calculate the rating again on the{' '}
          <Link to="/formulas">indicators step</Link>.
        </div>
      )}

      <Reveal className="headline">
        <RadialGauge
          value={result.quantitative_max ? result.quantitative_total / result.quantitative_max : 0}
          caption={`${result.quantitative_total}/${result.quantitative_max}`}
          band={result.quantitative_label}
          label="Final rating"
          size={168}
        />
        <div className="headline-facts">
          <div className={`stat stat-accent band-${result.quantitative_label.toLowerCase()}`}>
            <span>Rating</span>
            <strong>{result.quantitative_label}</strong>
            <em><AnimatedNumber value={result.quantitative_percentage} decimals={1} suffix="% of available points" /></em>
          </div>
          <div className="stat">
            <span>Points</span>
            <strong><AnimatedNumber value={result.quantitative_total} decimals={1} /> / {result.quantitative_max}</strong>
            <em>{ratios.length} indicators</em>
          </div>
          <div className="stat">
            <span>Record</span>
            <strong>{result.score_id ? `#${result.score_id}` : 'not saved'}</strong>
            {!result.score_id && <em>storage was unreachable</em>}
          </div>
        </div>
      </Reveal>

      <Reveal delay={0.08} className="card">
        <StackedBars
          title="Points earned by category"
          data={result.categories.map((c) => ({ name: c.name, score: c.score, max: c.max_score }))}
        />
      </Reveal>

      <Reveal delay={0.16} className="card tight">
        <div className="card-head">
          <h2>Indicators</h2>
          <div className="chips" role="group" aria-label="Filter by band">
            <button
              type="button" className={`chip${band === 'all' ? ' active' : ''}`}
              aria-pressed={band === 'all'} onClick={() => setBand('all')}
            >
              All <small>{ratios.length}</small>
            </button>
            {BANDS.map((b) => (
              <button
                key={b} type="button"
                className={`chip band-${b.toLowerCase()}${band === b ? ' active' : ''}`}
                aria-pressed={band === b}
                disabled={!counts.get(b)}
                onClick={() => setBand(b)}
              >
                {b} <small>{counts.get(b) ?? 0}</small>
              </button>
            ))}
          </div>
        </div>

        <div className="scroll">
          <table className="data sticky">
            <thead>
              <tr>
                <th aria-sort={ariaSort('category')}>
                  <button type="button" className="th-sort" onClick={() => toggleSort('category')}>Category</button>
                </th>
                <th aria-sort={ariaSort('name')}>
                  <button type="button" className="th-sort" onClick={() => toggleSort('name')}>Indicator</button>
                </th>
                <th className="num" aria-sort={ariaSort('value')}>
                  <button type="button" className="th-sort" onClick={() => toggleSort('value')}>Value</button>
                </th>
                <th className="num" aria-sort={ariaSort('score')}>
                  <button type="button" className="th-sort" onClick={() => toggleSort('score')}>Score</button>
                </th>
                <th>Band</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((r) => (
                <tr key={r.key}>
                  <td className="cat">{r.category}</td>
                  <td>
                    {r.name}
                    <small className="row-meta">{r.preference}</small>
                  </td>
                  <td className="num tabular">{fmt(r.value)}</td>
                  <td className="num">
                    <span className="score-cell">
                      <span className="tabular">{r.score} / {r.max_score}</span>
                      <span className="score-bar" aria-hidden="true">
                        <span
                          className={`score-bar-fill band-${r.label.toLowerCase()}`}
                          style={{ width: `${r.max_score ? (r.score / r.max_score) * 100 : 0}%` }}
                        />
                      </span>
                    </span>
                  </td>
                  <td><span className={`pill band-${r.label.toLowerCase()}`}>{r.label}</span></td>
                </tr>
              ))}
              {shown.length === 0 && (
                <tr><td colSpan={5} className="empty-cell">No indicators in this band.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </Reveal>

      <div className="split">
        <div className="split-main">
          <div className="card tight">
            <div className="card-head"><h2>Category totals</h2></div>
            <table className="data">
              <thead><tr><th>Category</th><th className="num">Score</th><th className="num">Share</th></tr></thead>
              <tbody>
                {result.categories.map((c) => (
                  <tr key={c.name}>
                    <td>{c.name}</td>
                    <td className="num tabular">{c.score} / {c.max_score}</td>
                    <td className="num tabular">{c.max_score ? ((c.score / c.max_score) * 100).toFixed(0) : 0}%</td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr>
                  <th>Total</th>
                  <th className="num tabular">{result.quantitative_total} / {result.quantitative_max}</th>
                  <th className="num tabular">{result.quantitative_percentage.toFixed(1)}%</th>
                </tr>
              </tfoot>
            </table>
          </div>

          <div className="card tight">
            <div className="card-head"><h2>Statement values</h2></div>
            <div className="value-columns">
              {SHEETS.filter((s) => statements[s.key]).map(({ key, label }) => (
                <div key={key}>
                  <h3>{label} <small>{statements[key]!.year_column}</small></h3>
                  <table className="data">
                    <tbody>
                      {Object.entries(statements[key]!.values).map(([item, v]) => (
                        <tr key={item} className={statements[key]!.missing.includes(item) ? 'missing' : ''}>
                          <td>{item}</td>
                          <td className="num tabular">{fmt(v)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ))}
            </div>
          </div>
        </div>

        <aside className="split-side">
          <div className="card tight">
            <div className="card-head"><h2>Applicant</h2></div>
            <dl className="detail">
              <dt>Name</dt><dd>{user.name || '—'}</dd>
              <dt>Phone</dt><dd>{user.phone || '—'}</dd>
              <dt>Email</dt><dd>{user.email || '—'}</dd>
              <dt>Address</dt><dd>{user.address || '—'}</dd>
            </dl>
          </div>

          {result.qualitative && (
            <div className="card tight">
              <div className="card-head"><h2>Qualitative answers</h2></div>
              <table className="data">
                <thead><tr><th>Question</th><th className="num">Score</th></tr></thead>
                <tbody>
                  {result.qualitative.answers.map((a) => (
                    <tr key={a.index}>
                      <td>{a.question}<small className="row-meta">{a.answer}</small></td>
                      <td className="num tabular">{a.score} / {a.max_score}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </aside>
      </div>
    </section>
  )
}
