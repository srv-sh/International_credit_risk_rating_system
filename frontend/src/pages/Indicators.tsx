import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useMemo, useState } from 'react'
import { getIndicators, saveIndicators } from '../api/endpoints'
import type { Band, Indicator } from '../api/types'
import FlowFooter from '../components/FlowFooter'
import { ErrorBox } from '../components/Status'
import { useToast } from '../components/blocks/ToastStack'

const BANDS: Band[] = ['Excellent', 'Good', 'Marginal', 'Unacceptable']

/** Edit each quantitative indicator's weight and points per band (was pages/parameters.py). */
export default function Indicators() {
  const queryClient = useQueryClient()
  const toast = useToast()
  const query = useQuery({ queryKey: ['indicators'], queryFn: getIndicators })
  const [rows, setRows] = useState<Indicator[]>([])
  useEffect(() => { if (query.data) setRows(query.data) }, [query.data])

  const save = useMutation({
    mutationFn: saveIndicators,
    onSuccess: (data) => {
      setRows(data)
      queryClient.setQueryData(['indicators'], data)
      // weights feed max scores and every rating
      queryClient.invalidateQueries({ queryKey: ['formulas'] })
      queryClient.invalidateQueries({ queryKey: ['score-preview'] })
      toast.push('ok', 'Weights saved. Every rating from here on uses them.')
    },
    onError: () => toast.push('error', 'Weights could not be saved.'),
  })

  const update = (i: number, patch: (row: Indicator) => Indicator) =>
    setRows(rows.map((r, j) => (j === i ? patch(r) : r)))
  const num = (v: string) => (v === '' ? 0 : Number(v))

  const total = rows.reduce((sum, r) => sum + r.scale, 0)
  const dirty = JSON.stringify(rows) !== JSON.stringify(query.data)

  // A band worth more than the indicator's own weight can never be reached.
  const overflow = useMemo(
    () => rows.filter((r) => BANDS.some((b) => r.scoring[b] > r.scale)).map((r) => r.name),
    [rows],
  )

  const byCategory = useMemo(() => {
    const groups = new Map<string, Indicator[]>()
    rows.forEach((r) => groups.set(r.category, [...(groups.get(r.category) ?? []), r]))
    return [...groups.entries()]
  }, [rows])

  return (
    <section className="page">
      <div className="page-head">
        <h1>Indicator weights</h1>
        <p className="lede">
          Weight is the most points an indicator can earn. The band columns are the points awarded
          when a ratio lands in that band. Saved changes apply to every rating calculated afterwards.
        </p>
      </div>

      <FlowFooter>
        {dirty && <p className="flow-note">Unsaved changes</p>}
        <button type="button" className="ghost" disabled={!dirty} onClick={() => query.data && setRows(query.data)}>
          Discard
        </button>
        <button type="button" className="secondary" disabled={!dirty || save.isPending} onClick={() => save.mutate(rows)}>
          {save.isPending ? 'Saving…' : 'Save weights'}
        </button>
      </FlowFooter>

      <div className="stat-row">
        <div className="stat">
          <span>Total points available</span>
          <strong>{total}</strong>
          <em>{rows.length} indicators</em>
        </div>
        <div className="stat">
          <span>Categories</span>
          <strong>{byCategory.length}</strong>
          <em>{byCategory.map(([c]) => c).join(', ')}</em>
        </div>
      </div>

      {overflow.length > 0 && (
        <div className="alert warn" role="status">
          These indicators award more points in a band than their own weight allows, so that band can
          never be reached: {overflow.join(', ')}.
        </div>
      )}

      <ErrorBox error={query.error} />
      <ErrorBox error={save.error} />

      <div className="card tight">
        <div className="scroll scroll-tall">
          <table className="data sticky">
            <thead>
              <tr>
                <th>Category</th><th>Indicator</th><th className="num">Weight</th>
                {BANDS.map((b) => <th key={b} className="num">{b}</th>)}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={r.key}>
                  <td className="cat">{r.category}</td>
                  <td>{r.name}</td>
                  <td className="num">
                    <input
                      type="number" min={0} step={0.5} value={r.scale} aria-label={`${r.name} weight`}
                      onChange={(e) => update(i, (row) => ({ ...row, scale: num(e.target.value) }))}
                    />
                  </td>
                  {BANDS.map((b) => (
                    <td key={b} className="num">
                      <input
                        type="number" min={0} step={0.5} value={r.scoring[b]}
                        aria-label={`${r.name} points when ${b}`}
                        aria-invalid={r.scoring[b] > r.scale || undefined}
                        onChange={(e) => update(i, (row) => ({ ...row, scoring: { ...row.scoring, [b]: num(e.target.value) } }))}
                      />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <th colSpan={2}>Total weight</th>
                <th className="num">{total}</th>
                <td colSpan={BANDS.length} />
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

    </section>
  )
}
