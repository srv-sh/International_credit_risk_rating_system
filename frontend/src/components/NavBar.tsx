import { NavLink } from 'react-router-dom'

// Replaces main.py's option_menu
const NAV_ITEMS = [
  { to: '/', label: 'Home' },
  { to: '/ocr', label: 'OCR' },
  { to: '/balance-sheet', label: 'Balance Sheet' },
  { to: '/income-sheet', label: 'Income Sheet' },
  { to: '/cashflow-sheet', label: 'Cashflow Sheet' },
  { to: '/formulas', label: 'Formulas' },
  { to: '/parameters', label: 'Parameters' },
  { to: '/graphs', label: 'Graphs' },
  { to: '/summary', label: 'Summary' },
]

export default function NavBar() {
  return (
    <header className="navbar">
      <span className="brand">Credit Risk Rating</span>
      <nav>
        {NAV_ITEMS.map((item) => (
          <NavLink key={item.to} to={item.to} end={item.to === '/'}>
            {item.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
