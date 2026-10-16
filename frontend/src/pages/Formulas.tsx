import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { getFormulas } from '../api/endpoints'
import Latex from '../components/Latex'
import { ErrorBox } from '../components/Status'
import { useAppStore } from '../store/useAppStore'

export default function Formulas() {
  const formulas = useQuery({ queryKey: ['formulas'], queryFn: getFormulas, staleTime: Infinity })
  const statements = useAppStore((s) => s.statements)
  const values = Object.assign({}, ...Object.values(statements).map((s) => s.values)) as Record<string, number>
  const sheetsDone = Object.keys(statements).length

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
              {formulas.data!.filter((f) => f.category === cat).map((f) => (
                <div key={f.key} className="formula">
                  <h4>{f.name} <small>{f.preference} · max {f.max_score}</small></h4>
                  {f.latex.map((tex) => <Latex key={tex} math={tex} />)}
                </div>
              ))}
            </div>
          ))}
        </div>
        <div>
          <h2>Input values</h2>
          {sheetsDone < 3 && <p className="hint">{sheetsDone}/3 statements calculated. Missing items count as 0.</p>}
          <table className="data">
            <tbody>
              {Object.entries(values).map(([item, v]) => (
                <tr key={item}><td>{item}</td><td className="num">{v.toLocaleString()}</td></tr>
              ))}
            </tbody>
          </table>
          <Link className="button primary" to="/parameters">Next</Link>
        </div>
      </div>
    </section>
  )
}
