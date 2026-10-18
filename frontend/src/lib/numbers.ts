/**
 * Financial cell parsing, mirroring parse_number in api/services.py.
 *
 * OCR hands back accounting notation: thousands separated by commas, and
 * negatives wrapped in brackets, e.g. (107,404,701,258). The tables keep
 * those as strings, which is wrong twice over: the sign is invisible to
 * anyone editing the table, and a cell is text when it is really a number.
 *
 * A cell converts only when the WHOLE cell is an accounting number. Line
 * names, note references like "8 (a)" and date headers like "30 June 2023"
 * do not match and pass through untouched, so the particulars column can
 * never be mangled. The semantics match the backend parser exactly, which
 * is what guarantees conversion cannot change a single score.
 */

// Optional ( ... ) wrapper, digits with optional comma grouping, optional
// decimals, optional leading minus. Anchored to the full cell.
const ACCOUNTING = /^\(\s*-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*\)$|^-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?$/

export type Cell = string | number | null

export function parseFinancialCell(value: Cell): Cell {
  if (typeof value !== 'string') return value
  const text = value.trim()
  if (!text || !ACCOUNTING.test(text)) return value

  const negative = text.startsWith('(')
  const digits = text.replace(/[(),\s]/g, '')
  const n = Number(digits)
  if (!Number.isFinite(n)) return value
  return negative ? -Math.abs(n) : n
}

/** Run every cell of a {column: values[]} table through the parser. */
export function numerifyTable<T extends Record<string, Cell[]>>(table: T): T {
  return Object.fromEntries(
    Object.entries(table).map(([col, cells]) => [col, cells.map(parseFinancialCell)]),
  ) as T
}
