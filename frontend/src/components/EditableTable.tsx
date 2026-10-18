import { AllCommunityModule, ModuleRegistry, themeQuartz, type ColDef } from 'ag-grid-community'
import { AgGridReact } from 'ag-grid-react'
import { useMemo, useState } from 'react'
import type { Table } from '../api/types'

ModuleRegistry.registerModules([AllCommunityModule])

/**
 * The grid shipped with its stock theme, which read as a grey slab bolted onto
 * the page. These are the same tokens index.css uses, so it now sits in the
 * design rather than next to it.
 */
const gridTheme = themeQuartz.withParams({
  accentColor: '#1d4ed8',
  backgroundColor: '#ffffff',
  foregroundColor: '#0c1427',
  borderColor: '#e0e7f3',
  chromeBackgroundColor: '#f6f8fd',
  headerBackgroundColor: '#f6f8fd',
  headerTextColor: '#6b7890',
  headerFontWeight: 600,
  headerFontSize: 11,
  oddRowBackgroundColor: '#fcfdff',
  rowHoverColor: '#f1f6ff',
  selectedRowBackgroundColor: '#eef4ff',
  rangeSelectionBorderColor: '#1d4ed8',
  fontFamily: "'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif",
  fontSize: 13,
  rowHeight: 38,
  headerHeight: 40,
  borderRadius: 0,
  wrapperBorder: false,
  cellHorizontalPadding: 12,
})

type Cell = string | number | null
type Row = Record<string, Cell>

function toRows(table: Table): Row[] {
  const cols = Object.keys(table)
  const n = cols.length ? table[cols[0]].length : 0
  return Array.from({ length: n }, (_, i) => Object.fromEntries(cols.map((c) => [c, table[c][i] ?? ''])))
}

function toTable(columns: string[], rows: Row[]): Table {
  return Object.fromEntries(columns.map((c) => [c, rows.map((r) => r[c] ?? '')]))
}

interface Props {
  table: Table
  onChange: (table: Table) => void
  height?: number
}

/** Spreadsheet-style editor for a {column: values[]} statement, with row/column operations from the old pages. */
export default function EditableTable({ table, onChange, height = 600 }: Props) {
  const columns = Object.keys(table)
  const rows = useMemo(() => toRows(table), [table])
  const [newColumn, setNewColumn] = useState('')
  const [selectedRow, setSelectedRow] = useState<number | null>(null)
  const [renameFrom, setRenameFrom] = useState('')
  const [renameTo, setRenameTo] = useState('')

  const colDefs = useMemo<ColDef<Row>[]>(
    () => columns.map((c, i) => ({
      field: c,
      headerName: c,
      editable: true,
      pinned: i === 0 ? 'left' : undefined,
      flex: i === 0 ? 2 : 1,
      // Cells that are numbers read as figures: right-aligned, tabular,
      // negatives in red. Strings (line names, notes, headers) stay left.
      cellClassRules: {
        'cell-figure': (p) => typeof p.value === 'number',
        'cell-negative': (p) => typeof p.value === 'number' && p.value < 0,
      },
    })),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [columns.join('\u0000')],
  )

  const emit = (nextColumns: string[], nextRows: Row[]) => onChange(toTable(nextColumns, nextRows))

  const insertRow = () => {
    const at = selectedRow === null ? rows.length : selectedRow + 1
    const empty = Object.fromEntries(columns.map((c) => [c, '']))
    emit(columns, [...rows.slice(0, at), empty, ...rows.slice(at)])
  }
  const deleteRow = () => {
    if (selectedRow === null) return
    emit(columns, rows.filter((_, i) => i !== selectedRow))
    setSelectedRow(null)
  }
  const addColumn = () => {
    const name = newColumn.trim()
    if (!name || columns.includes(name)) return
    emit([...columns, name], rows.map((r) => ({ ...r, [name]: '' })))
    setNewColumn('')
  }
  const deleteColumn = (name: string) => emit(columns.filter((c) => c !== name), rows)
  const renameColumn = () => {
    const name = renameTo.trim()
    if (!renameFrom || !name || columns.includes(name)) return
    const nextColumns = columns.map((c) => (c === renameFrom ? name : c))
    const nextRows = rows.map((r) => {
      const { [renameFrom]: value, ...rest } = r
      return { ...rest, [name]: value }
    })
    emit(nextColumns, nextRows)
    setRenameFrom('')
    setRenameTo('')
  }

  return (
    <div className="editable-table">
      <div className="toolbar">
        <div className="toolbar-group" role="group" aria-label="Rows">
          <button onClick={insertRow}>{selectedRow === null ? 'Add row' : `Insert row after ${selectedRow}`}</button>
          <button onClick={deleteRow} disabled={selectedRow === null}>Delete row</button>
        </div>
        <div className="toolbar-group" role="group" aria-label="Add or delete columns">
          <input placeholder="New column name" value={newColumn} maxLength={30} onChange={(e) => setNewColumn(e.target.value)} />
          <button onClick={addColumn} disabled={!newColumn.trim()}>Add column</button>
          <select value="" onChange={(e) => e.target.value && deleteColumn(e.target.value)}>
            <option value="">Delete column…</option>
            {columns.slice(1).map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div className="toolbar-group" role="group" aria-label="Rename a column">
          <select value={renameFrom} onChange={(e) => setRenameFrom(e.target.value)}>
            <option value="">Rename column…</option>
            {columns.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <input placeholder="New name" value={renameTo} maxLength={30} onChange={(e) => setRenameTo(e.target.value)} />
          <button onClick={renameColumn} disabled={!renameFrom || !renameTo.trim() || columns.includes(renameTo.trim())}>Rename</button>
        </div>
      </div>
      <div style={{ height }}>
        <AgGridReact<Row>
          theme={gridTheme}
          rowData={rows}
          columnDefs={colDefs}
          suppressFieldDotNotation
          rowSelection={{ mode: 'singleRow', checkboxes: false, enableClickSelection: true }}
          onRowSelected={(e) => e.node.isSelected() && setSelectedRow(e.node.rowIndex)}
          onCellValueChanged={(e) => {
            const next = rows.map((r, i) => (i === e.rowIndex ? { ...e.data } : r))
            emit(columns, next)
          }}
        />
      </div>
    </div>
  )
}
