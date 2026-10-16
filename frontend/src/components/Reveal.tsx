import { motion, useReducedMotion } from 'framer-motion'

/**
 * Lifts a block into place once, slightly after the one before it.
 *
 * Used for the stat rows and the headline so a results page assembles itself
 * rather than appearing all at once. Deliberately small: 10px and a third of
 * a second, enough to give the page a sense of depth without making anyone
 * wait to read a number.
 */
export default function Reveal({
  children,
  delay = 0,
  className,
}: {
  children: React.ReactNode
  delay?: number
  className?: string
}) {
  const still = useReducedMotion()
  if (still) return <div className={className}>{children}</div>

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.36, delay, ease: [0.22, 0.61, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}
