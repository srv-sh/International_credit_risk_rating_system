import { motion, useReducedMotion } from 'framer-motion'
import { NavLink, useLocation } from 'react-router-dom'
import { useFlow } from '../flow'

/**
 * The one navigation surface in the app.
 *
 * It replaces the old flat NavBar, which listed every tab from the start even
 * though each tab after Home reads data that only Home can produce. Here a
 * step that has nothing to show yet is disabled and says why, and the whole
 * rail stays hidden on Home until the statements have been extracted.
 */
export default function StepNav() {
  const { pathname } = useLocation()
  const { steps, current, showRail } = useFlow(pathname)
  const still = useReducedMotion()

  if (!showRail) {
    return (
      <header className="topbar is-bare">
        <span className="brand">
          <img className="brand-logo" src="/logo.jpg" alt="ONNESHX logo" />
          <span className="brand-text">
            <strong>ONNESHX</strong>
            <small>Credit Risk Rating</small>
          </span>
        </span>
      </header>
    )
  }

  const reached = steps.filter((s) => s.done).length

  return (
    <header className="topbar">
      <div className="topbar-row">
        <span className="brand">
          <img className="brand-logo" src="/logo.jpg" alt="ONNESHX logo" />
          <span className="brand-text">
            <strong>ONNESHX</strong>
            <small>Credit Risk Rating</small>
          </span>
        </span>
        <p className="topbar-hint">{current.hint}</p>
      </div>

      <nav className="rail" aria-label="Rating steps">
        <div className="rail-track" aria-hidden="true">
          <motion.div
            className="rail-track-fill"
            animate={{ scaleX: Math.max(current.index, reached ? reached - 1 : 0) / (steps.length - 1) }}
            transition={still ? { duration: 0 } : { type: 'spring', stiffness: 160, damping: 26 }}
          />
        </div>
        <ol>
          {steps.map((s) => {
            const state = s.id === current.id ? 'current' : s.done ? 'done' : s.blocker ? 'locked' : 'ahead'
            const content = (
              <>
                <span className="rail-dot" aria-hidden="true">
                  {s.done && s.id !== current.id ? (
                    <svg viewBox="0 0 24 24"><path d="M20 6 9 17l-5-5" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  ) : (
                    s.index + 1
                  )}
                </span>
                <span className="rail-label">{s.label}</span>
              </>
            )
            return (
              <li key={s.id} className={`rail-step is-${state}`}>
                {s.blocker ? (
                  <span className="rail-link" aria-disabled="true" title={s.blocker}>{content}</span>
                ) : (
                  <NavLink
                    to={s.path}
                    end={s.path === '/'}
                    className="rail-link"
                    aria-current={s.id === current.id ? 'step' : undefined}
                  >
                    {content}
                  </NavLink>
                )}
              </li>
            )
          })}
        </ol>
      </nav>
    </header>
  )
}
