import { lazy, Suspense } from 'react'
import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import PageTransition from './components/PageTransition'
import StepNav from './components/StepNav'
import { ToastProvider } from './components/blocks/ToastStack'
import { useFlow } from './flow'
import BalanceSheet from './pages/BalanceSheet'
import CashflowSheet from './pages/CashflowSheet'
import Home from './pages/Home'
import IncomeSheet from './pages/IncomeSheet'
import Indicators from './pages/Indicators'
import Ocr from './pages/Ocr'
import Parameters from './pages/Parameters'
import Summary from './pages/Summary'

// Plotly and KaTeX are large; load them only on the pages that use them
const Formulas = lazy(() => import('./pages/Formulas'))
const Graphs = lazy(() => import('./pages/Graphs'))

/**
 * Keeps a step that has no data from rendering a broken page. The pages still
 * carry their own empty states; this just gives one consistent way back.
 */
function StepGuard({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation()
  const { current, steps } = useFlow(pathname)
  const step = steps.find((s) => s.path === pathname)

  if (step?.blocker) {
    // Send them to the earliest step they can actually act on, rather than one
    // step back into another locked page.
    const resume = steps.find((s) => !s.blocker) ?? steps[0]
    return (
      <section className="page narrow">
        <div className="empty">
          <h2>{current.label} is not ready yet</h2>
          <p>{step.blocker}.</p>
          <Link className="button primary" to={resume.path}>Go to {resume.short}</Link>
        </div>
      </section>
    )
  }
  return <>{children}</>
}

export default function App() {
  return (
    <ToastProvider>
      <a className="skip-link" href="#main">Skip to content</a>
      <StepNav />
      <main id="main">
        <Suspense fallback={<div className="page"><p className="hint">Loading…</p></div>}>
          <PageTransition>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/balance-sheet" element={<StepGuard><BalanceSheet /></StepGuard>} />
            <Route path="/income-sheet" element={<StepGuard><IncomeSheet /></StepGuard>} />
            <Route path="/cashflow-sheet" element={<StepGuard><CashflowSheet /></StepGuard>} />
            <Route path="/weights" element={<StepGuard><Indicators /></StepGuard>} />
            <Route path="/formulas" element={<StepGuard><Formulas /></StepGuard>} />
            <Route path="/graphs" element={<StepGuard><Graphs /></StepGuard>} />
            <Route path="/summary" element={<StepGuard><Summary /></StepGuard>} />
            {/* Off the flow and out of the nav, but still reachable by URL. */}
            <Route path="/ocr" element={<Ocr />} />
            <Route path="/parameters" element={<Parameters />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
          </PageTransition>
        </Suspense>
      </main>
    </ToastProvider>
  )
}
