import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { calculateStatement, storeOcrData } from '../api/endpoints'
import type { RecordIds, SheetKey } from '../api/types'
import EditableTable from '../components/EditableTable'
import FlowFooter from '../components/FlowFooter'
import { ErrorBox, Notice } from '../components/Status'
import { useToast } from '../components/blocks/ToastStack'
import { useAppStore } from '../store/useAppStore'

const RECORD_KEY: Record<SheetKey, keyof RecordIds> = { bs: 'bs_id', is: 'is_id', cfs: 'cfs_id' }

interface Props {
  sheet: SheetKey
  title: string
}

/** Shared page for the three statements (was pages/bs.py, is.py, cfs.py). */
export default function StatementPage({ sheet, title }: Props) {
  const { ocr, tables, statements, stale, setTable, setStatement, setRecord } = useAppStore()
  const toast = useToast()
  const table = tables[sheet]
  const result = statements[sheet]
  const [yearColumn, setYearColumn] = useState<string>('')

  const calculate = useMutation({
    mutationFn: async () => {
      const res = await calculateStatement(sheet, { table: table!, year_column: yearColumn || undefined })
      setStatement(sheet, res)
      try {
        const stored = await storeOcrData({ sheet, page_number: 1, response: res.markdown })
        setRecord(RECORD_KEY[sheet], stored.id)
      } catch {
        toast.push('warn', 'Calculated, but the storage service is unreachable so this was not saved.')
      }
      return res
    },
    onSuccess: (res) => {
      const found = Object.keys(res.values).length - res.missing.length
      toast.push(res.missing.length ? 'warn' : 'ok',
        res.missing.length
          ? `Calculated. ${found} of ${Object.keys(res.values).length} items found; ${res.missing.length} counted as zero.`
          : `Calculated. All ${found} items found.`)
    },
    onError: () => toast.push('error', `${title} could not be calculated.`),
  })

  /** Re-point one item at a single line, straight from the FROM column. */
  const remap = useMutation({
    mutationFn: async ({ item, line }: { item: string; line: string }) => {
      const mapping = { ...result!.mapping, [item]: line ? [line] : [] }
      return calculateStatement(sheet, { table: table!, mapping, year_column: result!.year_column })
    },
    onSuccess: (res) => setStatement(sheet, res),
    onError: () => toast.push('error', 'Could not re-map that item.'),
  })

  if (!table) {
    return (
      <section className="page">
        <Notice>No {title.toLowerCase()} data yet. <Link to="/">Start from the applicant step</Link>.</Notice>
      </section>
    )
  }

  const valueColumns = Object.keys(table).slice(1)
  const items = result ? Object.entries(result.values) : []
  const missingCount = result?.missing.length ?? 0

  // Lines available for the FROM dropdowns
  const particularsCol = result?.particulars_column ?? Object.keys(table)[0]
  const particulars = [...new Set(table[particularsCol].map((p) => String(p ?? '').trim()).filter(Boolean))]

  /*
   * A statement where nearly everything is missing still produces a rating,
   * just one built on zeros, and nothing else in the app says so. The cause is
   * almost always one of two columns, and the fix differs, so tell them apart.
   *
   * Matched but no number: the line names were found, so the particulars
   * column is right and the year column is pointing at something that is not
   * money, typically a note-reference column.
   *
   * Nothing matched at all: the line names themselves were not found, so the
   * particulars column is wrong. The backend picks it by position (first
   * column, unless one is named "particulars"), so an index column sitting in
   * front of the real one silently breaks the whole statement.
   */
  const nearlyAllMissing = !!result && items.length > 0 && missingCount >= items.length - 1
  const mappedButEmpty = !!result &&
    result.missing.every((item) => (result.mapping[item]?.length ?? 0) > 0)

  const columnWarning = !result || !nearlyAllMissing
    ? null
    : mappedButEmpty
      ? {
        title: 'Check the year column.',
        body: `The line names were found, but none of them has a number in the "${result.year_column}" column, `
          + `so all ${missingCount} items count as zero. Pick the column holding the figures for the year `
          + 'you are rating, then calculate again.',
      }
      : {
        title: 'Check the particulars column.',
        body: `The line names are being read from "${result.particulars_column}" and ${missingCount} of `
          + `${items.length} items could not be matched, so they count as zero. If that column is not the `
          + 'one holding the line names, rename the correct column to Particulars above, then calculate again.',
      }

  return (
    <section className="page">
      <div className="page-head">
        <h1>{title}</h1>
        <p className="lede">
          Correct anything the extraction got wrong, pick the column holding the year you are rating,
          then calculate.
        </p>
      </div>

      <FlowFooter blockedBy={result ? null : `Calculate the ${title.toLowerCase()} to continue`} />

      {columnWarning && (
        <div className="alert warn" role="status">
          <strong>{columnWarning.title}</strong> {columnWarning.body}
        </div>
      )}

      {stale[sheet] && (
        <div className="alert warn" role="status">
          The table changed since the last calculation. Calculate again so the values match what you see.
        </div>
      )}

      <div className="split">
        <div className="split-main">
          <div className="card tight">
            <div className="card-head">
              <h2>Extracted table</h2>
              <div className="inline-controls">
                <label className="field inline">
                  <span>Year column</span>
                  <select value={yearColumn} onChange={(e) => setYearColumn(e.target.value)}>
                    <option value="">{valueColumns[0] ?? 'none'} (default)</option>
                    {valueColumns.slice(1).map((c) => <option key={c} value={c}>{c}</option>)}
                  </select>
                </label>
                <button
                  type="button"
                  className={result ? 'secondary' : 'primary'}
                  disabled={calculate.isPending}
                  onClick={() => calculate.mutate()}
                >
                  {calculate.isPending ? 'Calculating…' : result ? 'Recalculate' : 'Calculate'}
                </button>
              </div>
            </div>
            <EditableTable table={table} onChange={(t) => setTable(sheet, t)} height={520} />
          </div>
          <ErrorBox error={calculate.error} />
        </div>

        <aside className="split-side">
          <div className="card tight">
            <div className="card-head">
              <h2>Source image</h2>
            </div>
            {ocr?.[sheet].image
              ? <img className="statement" src={ocr[sheet].image!} alt={`${title} as uploaded`} />
              : <p className="hint">The image is not kept after a refresh. The table below is what counts.</p>}
          </div>

          {result && (
            <div className="card tight">
              <div className="card-head">
                <h2>Values used <small>names from "{result.particulars_column}", figures from "{result.year_column}"</small></h2>
                {missingCount > 0 && <span className="pill pill-warn">{missingCount} missing</span>}
              </div>
              <div className="scroll scroll-tall">
                <table className="data">
                  <thead><tr><th>Item</th><th className="num">Value</th><th>From</th></tr></thead>
                  <tbody>
                    {items.map(([item, value]) => {
                      const absent = result.missing.includes(item)
                      const from = result.mapping[item]
                      const single = from?.length === 1 ? from[0] : null
                      return (
                        <tr key={item} className={absent ? 'missing' : ''}>
                          <td>{item}</td>
                          <td className="num">{value.toLocaleString()}</td>
                          <td className="from">
                            <select
                              className="from-select"
                              aria-label={`Line ${item} is read from`}
                              disabled={remap.isPending}
                              value={from && from.length > 1 ? '__multi__' : single ?? ''}
                              onChange={(e) => {
                                if (e.target.value !== '__multi__') remap.mutate({ item, line: e.target.value })
                              }}
                            >
                              {from && from.length > 1 && <option value="__multi__">{from.join(' + ')}</option>}
                              <option value="">not mapped</option>
                              {single && !particulars.includes(single) && <option value={single}>{single}</option>}
                              {particulars.map((p) => <option key={p} value={p}>{p}</option>)}
                            </select>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              {missingCount > 0 && (
                <p className="hint">
                  Items shown as missing count as zero. You can point them at the right line on the
                  Indicators step.
                </p>
              )}
            </div>
          )}
        </aside>
      </div>

    </section>
  )
}
