import { animate, useReducedMotion } from 'framer-motion'
import { useEffect, useRef, useState } from 'react'

/**
 * Counts a figure up to its value instead of snapping to it.
 *
 * The final rendered text is always the exact value, so a score is never left
 * mid-animation if the tab is backgrounded or motion is reduced.
 */
interface Props {
  value: number
  decimals?: number
  /** Rendered before and after the number, e.g. a percent sign. */
  suffix?: string
  duration?: number
}

export default function AnimatedNumber({ value, decimals = 0, suffix = '', duration = 0.9 }: Props) {
  const still = useReducedMotion()
  const [shown, setShown] = useState(still ? value : 0)
  const previous = useRef(still ? value : 0)

  useEffect(() => {
    if (still) {
      setShown(value)
      previous.current = value
      return
    }
    const controls = animate(previous.current, value, {
      duration,
      ease: [0.22, 0.61, 0.36, 1],
      onUpdate: (v) => setShown(v),
      onComplete: () => setShown(value),
    })
    previous.current = value
    return () => controls.stop()
  }, [value, duration, still])

  const text = shown.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })
  return <span className="tabular">{text}{suffix}</span>
}
