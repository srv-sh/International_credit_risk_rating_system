import { useAppStore } from './store/useAppStore'

export type StepId = 'home' | 'bs' | 'is' | 'cfs' | 'weights' | 'formulas' | 'graphs' | 'summary'

export interface Step {
  id: StepId
  path: string
  /** Shown in the step rail. */
  label: string
  /** Shown in the breadcrumb and on the Back/Continue buttons. */
  short: string
  /** What the user is meant to do here. */
  hint: string
}

/**
 * The order of the wizard. Everything that needs to know "what comes next"
 * reads it from here, so the rail, the breadcrumb and the Continue buttons
 * can never disagree with each other the way the old NavBar did.
 *
 * Deliberately absent: /ocr and /parameters. Both routes still work if you
 * type them, they are just not part of the flow any more.
 */
export const STEPS: Step[] = [
  { id: 'home', path: '/', label: 'Applicant', short: 'Applicant', hint: 'Applicant details and the three statement images' },
  { id: 'bs', path: '/balance-sheet', label: 'Balance sheet', short: 'Balance sheet', hint: 'Check the extracted balance sheet, then calculate it' },
  { id: 'is', path: '/income-sheet', label: 'Income statement', short: 'Income statement', hint: 'Check the extracted income statement, then calculate it' },
  { id: 'cfs', path: '/cashflow-sheet', label: 'Cash flow', short: 'Cash flow', hint: 'Check the extracted cash flow statement, then calculate it' },
  { id: 'weights', path: '/weights', label: 'Weights', short: 'Weights', hint: 'Points each indicator can earn, and the points per band' },
  { id: 'formulas', path: '/formulas', label: 'Indicators', short: 'Indicators', hint: 'The values behind each ratio, and the scored formulas' },
  { id: 'graphs', path: '/graphs', label: 'Analysis', short: 'Analysis', hint: 'Charts for the calculated rating' },
  { id: 'summary', path: '/summary', label: 'Summary', short: 'Summary', hint: 'The complete rating and every input behind it' },
]

export const stepByPath = (path: string) => STEPS.find((s) => s.path === path)

/** Why a step cannot be opened yet, or null when it can. */
export type Blocker = string | null

export interface FlowStep extends Step {
  index: number
  blocker: Blocker
  /** Finished enough to move past it. */
  done: boolean
}

/**
 * The flow for the current session state.
 *
 * A step is locked when the data it reads does not exist yet. That is the
 * same reason the old navbar had to be hidden on Home: the later tabs are
 * all derived from what Home produces.
 */
export function useFlow(currentPath: string) {
  const tables = useAppStore((s) => s.tables)
  const statements = useAppStore((s) => s.statements)
  const result = useAppStore((s) => s.result)

  const extracted = Object.keys(tables).length > 0
  const calculated = (['bs', 'is', 'cfs'] as const).filter((k) => statements[k])

  const blockerFor = (id: StepId): Blocker => {
    if (id === 'home') return null
    if (!extracted) return 'Add the applicant details and statement images first'
    if (id === 'graphs' || id === 'summary') {
      return result ? null : 'Calculate the rating on the Indicators step first'
    }
    return null
  }

  const doneFor = (id: StepId): boolean => {
    switch (id) {
      case 'home': return extracted
      case 'bs': case 'is': case 'cfs': return !!statements[id]
      // Weights ship with defaults, so there is nothing to complete here.
      // It only counts as done once a rating has actually used them.
      case 'weights': return !!result
      case 'formulas': return !!result
      case 'graphs': case 'summary': return !!result
    }
  }

  const steps: FlowStep[] = STEPS.map((s, index) => ({
    ...s, index, blocker: blockerFor(s.id), done: doneFor(s.id),
  }))

  const current = steps.find((s) => s.path === currentPath) ?? steps[0]
  const prev = current.index > 0 ? steps[current.index - 1] : null
  const next = current.index < steps.length - 1 ? steps[current.index + 1] : null

  return {
    steps,
    current,
    prev,
    next,
    extracted,
    /** How many of the three statements have been calculated. */
    calculatedCount: calculated.length,
    /** The nav is pointless on Home because nothing downstream exists yet. */
    showRail: current.id !== 'home' || extracted,
  }
}
