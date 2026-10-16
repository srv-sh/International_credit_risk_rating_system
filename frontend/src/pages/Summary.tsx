import { Link, useNavigate } from 'react-router-dom'
import type { SheetKey } from '../api/types'
import { Notice } from '../components/Status'
import { useAppStore } from '../store/useAppStore'

const SHEETS: { key: SheetKey; label: string; path: string }[] = [
  { key: 'bs', label: 'Balance Sheet', path: '/balance-sheet' },
  { key: 'is', label: 'Income Sheet', path: '/income-sheet' },
  { key: 'cfs', label: 'Cashflow Sheet', path: '/cashflow-sheet' },
]

const fmt = (v: number | null) => (v === null ? '—' : v.toLocaleString(undefined, { maximumFractionDigits: 4 }))

/** All inputs and the final rating on one page. */
export default function Summary() {
  const navigate = useNavigate()
  const { user, statements, stale, result, reset } = useAppStore()

  if (!result) {
    return <section className="page"><Notice>No rating yet. Complete the <Link to="/parameters">parameters</Link> first.</Notice></section>
  }

  const staleSheets = SHEETS.filter((s) => stale[s.key])
  const startOver = () => {
    reset()
    navigate('/')
  }

  return (
    <section className="page">
      <h1>Summary</h1>
      {staleSheets.length > 0 && (
        <div className="alert">
          Edited since the rating was calculated: {staleSheets.map((s, i) => (
            <span key={s.key}>{i > 0 && ', '}<Link to={s.path}>{s.label}</Link></span>
          ))}. Recalculate them, then re-run the <Link to="/parameters">rating</Link>.
        </div>
      )}

      <div className="score-cards">
        <div><span>Quantitative</span><strong>{result.quantitative_total}/{result.quantitative_max}</strong><em>{result.quantitative_label}</em></div>
        {result.qualitative && (
          <div><span>Qualitative</span><strong>{result.qualitative.total}/{result.qualitative.max_score}</strong></div>
        )}
        <div><span>Overall</span><strong>{result.overall_percentage.toFixed(1)}%</strong><em>{result.overall_label}</em></div>
        {result.score_id && <div><span>Saved as</span><strong>#{result.score_id}</strong></div>}
      </div>

      <h2>Applicant</h2>
      <table className="data">
        <tbody>
          <tr><td>Name</td><td>{user.name}</td></tr>
          <tr><td>Phone</td><td>{user.phone}</td></tr>
          <tr><td>Email</td><td>{user.email}</td></tr>
          <tr><td>Address</td><td>{user.address}</td></tr>
        </tbody>
      </table>

      <h2>Ratios</h2>
      <table className="data">
        <thead><tr><th>Category</th><th>Ratio</th><th>Value</th><th>Score</th><th>Label</th></tr></thead>
        <tbody>
          {result.ratios.map((r) => (
            <tr key={r.key}>
              <td>{r.category}</td><td>{r.name}</td><td className="num">{fmt(r.value)}</td>
              <td className="num">{r.score}/{r.max_score}</td><td>{r.label}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Category scores</h2>
      <table className="data">
        <thead><tr><th>Category</th><th>Score</th></tr></thead>
        <tbody>
          {result.categories.map((c) => (
            <tr key={c.name}><td>{c.name}</td><td className="num">{c.score}/{c.max_score}</td></tr>
          ))}
        </tbody>
      </table>

      {result.qualitative && (
        <>
          <h2>Qualitative answers</h2>
          <table className="data">
            <thead><tr><th>Category</th><th>Question</th><th>Answer</th><th>Score</th></tr></thead>
            <tbody>
              {result.qualitative.answers.map((a) => (
                <tr key={a.index}>
                  <td>{a.category}</td><td>{a.question}</td><td>{a.answer}</td>
                  <td className="num">{a.score}/{a.max_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      <h2>Statement values</h2>
      <div className="two-col">
        {SHEETS.filter((s) => statements[s.key]).map(({ key, label }) => (
          <div key={key}>
            <h3>{label} <small>({statements[key]!.year_column})</small></h3>
            <table className="data">
              <tbody>
                {Object.entries(statements[key]!.values).map(([item, v]) => (
                  <tr key={item} className={statements[key]!.missing.includes(item) ? 'missing' : ''}>
                    <td>{item}</td><td className="num">{fmt(v)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ))}
      </div>

      <div className="actions">
        <button onClick={() => window.print()}>Print</button>
        <button onClick={startOver}>Start over</button>
      </div>
    </section>
  )
}
