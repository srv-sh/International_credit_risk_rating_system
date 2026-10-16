import { motion, useReducedMotion } from 'framer-motion'
import { useState } from 'react'

/**
 * Score against the points available, one bar per category.
 *
 * Ported from bencho.dev/blocks/stacked-bars (MIT). The behaviour that makes
 * that block worth copying is the hover: the bar you are on is ringed and a
 * tooltip glides along the row to meet it instead of popping in and out at
 * each bar. Switching the mode regrows the bars rather than snapping them.
 */

export interface BarDatum {
  name: string
  score: number
  max: number
}

type Mode = 'points' | 'share'

const SPRING = { type: 'spring' as const, stiffness: 320, damping: 30 }

export default function StackedBars({ data, title }: { data: BarDatum[]; title: string }) {
  const still = useReducedMotion()
  const [mode, setMode] = useState<Mode>('points')
  const [at, setAt] = useState<number | null>(null)

  const ceiling = Math.max(...data.map((d) => d.max), 1)
  // "points" compares categories on one scale; "share" asks how much of each
  // category's own points were earned.
  const fill = (d: BarDatum) => (mode === 'points' ? d.score / ceiling : d.max ? d.score / d.max : 0)
  const rest = (d: BarDatum) => (mode === 'points' ? (d.max - d.score) / ceiling : d.max ? (d.max - d.score) / d.max : 0)

  const active = at === null ? null : data[at]

  return (
    <section className="bars" aria-labelledby="bars-title">
      <header className="bars-head">
        <h3 id="bars-title">{title}</h3>
        <div className="segmented" role="group" aria-label="Bar scale">
          {(['points', 'share'] as Mode[]).map((m) => (
            <button key={m} type="button" className={m === mode ? 'active' : ''}
              aria-pressed={m === mode} onClick={() => setMode(m)}>
              {m === 'points' ? 'Points' : 'Share'}
            </button>
          ))}
        </div>
      </header>

      {/* Tooltip rail and bars scroll together, so the tooltip stays over its
          bar on a narrow screen instead of drifting off it. */}
      <div className="bars-plot">
        <div className="bars-tooltip-rail">
        <motion.div
          className="bars-tooltip" role="status" aria-live="polite"
          animate={{
            opacity: active ? 1 : 0,
            left: `${((at ?? 0) + 0.5) * (100 / data.length)}%`,
          }}
          transition={still ? { duration: 0 } : SPRING}
        >
          {active && (
            <>
              <strong>{active.name}</strong>
              <span>{active.score} of {active.max} points</span>
              <span>{active.max ? ((active.score / active.max) * 100).toFixed(0) : 0}% earned</span>
            </>
          )}
        </motion.div>
      </div>

      <ul className="bars-row" onMouseLeave={() => setAt(null)}>
        {data.map((d, i) => (
          <li key={d.name}
            className={`bars-item${at === i ? ' is-on' : ''}`}
            onMouseEnter={() => setAt(i)}
            onFocus={() => setAt(i)}
            onBlur={() => setAt(null)}
            tabIndex={0}
            aria-label={`${d.name}: ${d.score} of ${d.max} points`}
          >
            <div className="bars-stack">
              <motion.span
                className="bars-rest"
                animate={{ height: `${rest(d) * 100}%` }}
                transition={still ? { duration: 0 } : SPRING}
              />
              <motion.span
                className="bars-fill"
                animate={{ height: `${fill(d) * 100}%` }}
                transition={still ? { duration: 0 } : { ...SPRING, delay: still ? 0 : i * 0.035 }}
              />
            </div>
            <span className="bars-name">{d.name}</span>
            <span className="bars-figure">{d.score}<small>/{d.max}</small></span>
          </li>
        ))}
        </ul>
      </div>
    </section>
  )
}
