import { useMutation, useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { getQualitativeQuestions, score } from '../api/endpoints'
import { ErrorBox } from '../components/Status'
import { useAppStore } from '../store/useAppStore'

/**
 * Qualitative questionnaire and final rating.
 *
 * Retired: the rating is quantitative only now, scored out of 60, and is
 * calculated on the Indicators step. This page is off the flow and out of the
 * nav, but the route still resolves and the endpoints it calls are untouched,
 * so it is here if the qualitative half is ever brought back. Scoring from
 * here produces a rating out of 100, which will not match the rest of the app.
 */
export default function Parameters() {
  const navigate = useNavigate()
  const { statements, records, qualitativeAnswers, setQualitativeAnswers, setResult } = useAppStore()
  const questions = useQuery({ queryKey: ['qualitative-questions'], queryFn: getQualitativeQuestions, staleTime: Infinity })

  const answers = questions.data?.map((_, i) => qualitativeAnswers[i] ?? '') ?? []
  const complete = answers.length > 0 && answers.every(Boolean)

  const rate = useMutation({
    mutationFn: async () => {
      const values = Object.assign({}, ...Object.values(statements).map((s) => s.values))
      const body = { values, qualitative: { answers }, records }
      try {
        return await score({ ...body, save: true })
      } catch {
        return await score(body) // storage down: still show the rating, just unsaved
      }
    },
    onSuccess: (result) => {
      setResult(result)
      navigate('/graphs')
    },
  })

  const setAnswer = (i: number, label: string) => {
    const next = [...answers]
    next[i] = label
    setQualitativeAnswers(next)
  }

  let lastCategory = ''
  return (
    <section className="page narrow">
      <h1>Qualitative Parameters</h1>
      <div className="alert warn" role="status">
        This step is retired. The rating is quantitative only, out of 60, and is calculated on the{' '}
        <Link to="/formulas">indicators step</Link>. Scoring here produces a rating out of 100 that
        will not match the rest of the app.
      </div>
      <ErrorBox error={questions.error} />
      {questions.data?.map((q) => {
        const header = q.category !== lastCategory ? <h2>{(lastCategory = q.category)}</h2> : null
        return (
          <div key={q.index}>
            {header}
            <label className="question">
              <span>{q.question} <small>(max {q.max_score})</small></span>
              <select value={answers[q.index]} onChange={(e) => setAnswer(q.index, e.target.value)}>
                <option value="">Select…</option>
                {q.options.map((o) => <option key={o.label} value={o.label}>{o.label} ({o.score})</option>)}
              </select>
            </label>
          </div>
        )
      })}
      <ErrorBox error={rate.error} />
      <button className="primary" disabled={!complete || rate.isPending} onClick={() => rate.mutate()}>
        {rate.isPending ? 'Scoring…' : 'Calculate rating'}
      </button>
    </section>
  )
}
