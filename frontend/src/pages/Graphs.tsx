import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { buildGraph, getGraph } from '../api/endpoints'
import Chart from '../components/Chart'
import { ErrorBox, Notice } from '../components/Status'
import { useAppStore } from '../store/useAppStore'

const GRAPHS = [
  { id: 'summary', label: 'Summary' },
  { id: 'ratios', label: 'Ratios' },
  { id: 'categories', label: 'Categories' },
  { id: 'qualitative', label: 'Qualitative' },
]

export default function Graphs() {
  const result = useAppStore((s) => s.result)
  const [graphId, setGraphId] = useState('summary')

  const figure = useQuery({
    queryKey: ['graph', graphId, result?.score_id ?? result],
    // Saved scores are loaded by id; unsaved ones are sent in full
    queryFn: () => (result!.score_id ? getGraph(graphId, result!.score_id) : buildGraph(graphId, result!)),
    enabled: !!result,
  })

  if (!result) {
    return <section className="page"><Notice>No rating yet. Complete the <Link to="/parameters">parameters</Link> first.</Notice></section>
  }

  return (
    <section className="page">
      <h1>Quantitative Analysis</h1>
      <div className="score-cards">
        <div><span>Quantitative</span><strong>{result.quantitative_total}/{result.quantitative_max}</strong><em>{result.quantitative_label}</em></div>
        {result.qualitative && (
          <div><span>Qualitative</span><strong>{result.qualitative.total}/{result.qualitative.max_score}</strong></div>
        )}
        <div><span>Overall</span><strong>{result.overall_percentage.toFixed(1)}%</strong><em>{result.overall_label}</em></div>
      </div>
      <div className="tabs">
        {GRAPHS.filter((g) => g.id !== 'qualitative' || result.qualitative).map((g) => (
          <button key={g.id} className={g.id === graphId ? 'active' : ''} onClick={() => setGraphId(g.id)}>{g.label}</button>
        ))}
      </div>
      <ErrorBox error={figure.error} />
      {figure.isLoading && <p className="hint">Loading chart…</p>}
      {figure.data && <Chart figure={figure.data} />}
      <Link className="button primary" to="/summary">Next</Link>
    </section>
  )
}
