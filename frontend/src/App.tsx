import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import BalanceSheet from './pages/BalanceSheet'
import CashflowSheet from './pages/CashflowSheet'
import Home from './pages/Home'
import IncomeSheet from './pages/IncomeSheet'
import Ocr from './pages/Ocr'
import Parameters from './pages/Parameters'
import Summary from './pages/Summary'

// Plotly and KaTeX are large; load them only on the pages that use them
const Formulas = lazy(() => import('./pages/Formulas'))
const Graphs = lazy(() => import('./pages/Graphs'))

export default function App() {
  return (
    <>
      <NavBar />
      <main>
        <Suspense fallback={<p className="hint">Loading…</p>}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/ocr" element={<Ocr />} />
            <Route path="/balance-sheet" element={<BalanceSheet />} />
            <Route path="/income-sheet" element={<IncomeSheet />} />
            <Route path="/cashflow-sheet" element={<CashflowSheet />} />
            <Route path="/formulas" element={<Formulas />} />
            <Route path="/parameters" element={<Parameters />} />
            <Route path="/graphs" element={<Graphs />} />
            <Route path="/summary" element={<Summary />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </main>
    </>
  )
}
