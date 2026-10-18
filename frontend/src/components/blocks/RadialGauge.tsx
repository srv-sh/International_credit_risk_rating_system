import { motion, useReducedMotion } from 'framer-motion'

/**
 * The headline rating as a radial sweep.
 *
 * Ported from bencho.dev/blocks/radial (MIT): one arc, driven by a single
 * number, that grows into place on a spring rather than appearing finished.
 * The band name is printed as well as coloured, so the rating never depends
 * on colour alone.
 */

interface Props {
  /** 0 to 1. */
  value: number
  label: string
  caption: string
  band: string
  size?: number
}

const R = 54
const CIRC = 2 * Math.PI * R

export default function RadialGauge({ value, label, caption, band, size = 148 }: Props) {
  const still = useReducedMotion()
  const clamped = Math.max(0, Math.min(1, value))
  const slug = band.toLowerCase().replace(/[^a-z]+/g, '-')

  return (
    <figure className={`gauge band-${slug}`} style={{ width: size }}>
      <svg viewBox="0 0 128 128" width={size} height={size} role="img"
        aria-label={`${label}: ${caption}, rated ${band}`}>
        {/* track */}
        <circle cx="64" cy="64" r={R} className="gauge-track" fill="none" strokeWidth="11" />
        {/* sweep, starting at 12 o'clock */}
        <motion.circle
          cx="64" cy="64" r={R} className="gauge-sweep" fill="none" strokeWidth="11"
          strokeLinecap="round"
          transform="rotate(-90 64 64)"
          strokeDasharray={CIRC}
          initial={still ? { strokeDashoffset: CIRC * (1 - clamped) } : { strokeDashoffset: CIRC }}
          animate={{ strokeDashoffset: CIRC * (1 - clamped) }}
          transition={still ? { duration: 0 } : { type: 'spring', stiffness: 60, damping: 18 }}
        />
      </svg>
      <div className="gauge-centre">
        <strong className="gauge-value">{caption}</strong>
        <span className="gauge-band">{band}</span>
      </div>
      <figcaption>{label}</figcaption>
    </figure>
  )
}
