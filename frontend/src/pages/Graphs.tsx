import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { buildGraph, getGraph } from '../api/endpoints'
import Chart from '../components/Chart'
import AnimatedNumber from '../components/AnimatedNumber'
import FlowFooter from '../components/FlowFooter'
import Reveal from '../components/Reveal'
import { ErrorBox, Notice } from '../components/Status'
import RadialGauge from '../components/blocks/RadialGauge'
import { useAppStore } from '../store/useAppStore'

const GRAPHS = [
  { id: 'summary', label: 'Overview' },
  { id: 'ratios', label: 'By ratio' },
  { id: 'categories', label: 'By category' },
  // Only rendered when a qualitative result exists, which it does not in the
  // quantitative-only flow. Kept so an older saved score still charts.
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
    return (
      <section className="page">
        <Notice>
          No rating yet. Calculate it on the <Link to="/formulas">indicators step</Link> first.
        </Notice>
      </section>
    )
  }

  const tabs = GRAPHS.filter((g) => g.id !== 'qualitative' || result.qualitative)

  return (
    <section className="page">
      <div className="page-head">
        <h1>Analysis</h1>
        <p className="lede">The calculated rating, broken down by ratio and by category.</p>
      </div>

      <FlowFooter />

      <Reveal className="headline">
        <RadialGauge
          value={result.quantitative_max ? result.quantitative_total / result.quantitative_max : 0}
          caption={`${result.quantitative_total}/${result.quantitative_max}`}
          band={result.quantitative_label}
          label="Quantitative rating"
        />
        <div className="headline-facts">
          <div className="stat">
            <span>Score</span>
            <strong><AnimatedNumber value={result.quantitative_percentage} decimals={1} suffix="%" /></strong>
            <em>{result.quantitative_total} of {result.quantitative_max} points</em>
          </div>
          <div className="stat">
            <span>Indicators scored</span>
            <strong>{result.ratios.length}</strong>
            <em>across {result.categories.length} categories</em>
          </div>
          <div className="stat">
            <span>Saved as</span>
            <strong>{result.score_id ? `#${result.score_id}` : 'not saved'}</strong>
            {!result.score_id && <em>storage was unreachable</em>}
          </div>
        </div>
      </Reveal>

      <Reveal delay={0.08} className="card tight">
        <div className="card-head">
          <div className="segmented" role="tablist" aria-label="Chart">
            {tabs.map((g) => (
              <button
                key={g.id} type="button" role="tab" aria-selected={g.id === graphId}
                className={g.id === graphId ? 'active' : ''} onClick={() => setGraphId(g.id)}
              >
                {g.label}
              </button>
            ))}
          </div>
        </div>
        <ErrorBox error={figure.error} />
        {figure.isLoading && <div className="chart-skeleton" aria-hidden="true" />}
        {figure.data && <Chart figure={figure.data} />}
      </Reveal>

    </section>
  )
}
