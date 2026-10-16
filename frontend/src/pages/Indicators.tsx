import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { getIndicators, saveIndicators } from '../api/endpoints'
import type { Band, Indicator } from '../api/types'
import { ErrorBox, Notice } from '../components/Status'

const BANDS: Band[] = ['Excellent', 'Good', 'Marginal', 'Unacceptable']

/** Edit each quantitative indicator's weight and points per band (was pages/parameters.py). */
export default function Indicators() {
  const queryClient = useQueryClient()
  const query = useQuery({ queryKey: ['indicators'], queryFn: getIndicators })
  const [rows, setRows] = useState<Indicator[]>([])
  const [saved, setSaved] = useState(false)
  useEffect(() => { if (query.data) setRows(query.data) }, [query.data])

  const save = useMutation({
    mutationFn: saveIndicators,
    onSuccess: (data) => {
      setRows(data)
      setSaved(true)
      queryClient.setQueryData(['indicators'], data)
      // weights feed max scores and every rating
      queryClient.invalidateQueries({ queryKey: ['formulas'] })
      queryClient.invalidateQueries({ queryKey: ['score-preview'] })
    },
  })

  const update = (i: number, patch: (row: Indicator) => Indicator) => {
    setSaved(false)
    setRows(rows.map((r, j) => (j === i ? patch(r) : r)))
  }
  const num = (v: string) => (v === '' ? 0 : Number(v))

  const total = rows.reduce((sum, r) => sum + r.scale, 0)
  const dirty = JSON.stringify(rows) !== JSON.stringify(query.data)

  return (
    <section className="page">
      <h1>Quantitative Indicator Weights</h1>
      <p className="hint">
        Weight is the most points an indicator can earn; the band columns are the points awarded at each band.
        Saved changes apply to every rating calculated afterwards.
      </p>
      <ErrorBox error={query.error} />
      <div className="scroll">
        <table>
          <thead>
            <tr><th>Category</th><th>Indicator</th><th>Weight</th>{BANDS.map((b) => <th key={b}>{b}</th>)}</tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={r.key}>
                <td>{r.category}</td>
                <td>{r.name}</td>
                <td>
                  <input type="number" min={0} step={0.5} value={r.scale}
                    onChange={(e) => update(i, (row) => ({ ...row, scale: num(e.target.value) }))} />
                </td>
                {BANDS.map((b) => (
                  <td key={b}>
                    <input type="number" min={0} max={r.scale} step={0.5} value={r.scoring[b]}
                      onChange={(e) => update(i, (row) => ({ ...row, scoring: { ...row.scoring, [b]: num(e.target.value) } }))} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr><th colSpan={2}>Total weight</th><th>{total}</th><td colSpan={BANDS.length} /></tr>
          </tfoot>
        </table>
      </div>
      <ErrorBox error={save.error} />
      {saved && !dirty && <Notice>Weights saved.</Notice>}
      <div className="actions">
        <button className="primary" disabled={!dirty || save.isPending} onClick={() => save.mutate(rows)}>
          {save.isPending ? 'Saving…' : 'Save changes'}
        </button>
        <button disabled={!dirty} onClick={() => query.data && setRows(query.data)}>Discard</button>
      </div>
    </section>
  )
}
