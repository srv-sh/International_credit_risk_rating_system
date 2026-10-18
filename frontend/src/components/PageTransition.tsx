import { motion, useReducedMotion } from 'framer-motion'
import { useLocation, useNavigationType } from 'react-router-dom'

/**
 * Moves a step in from the side you are travelling towards, so going back
 * feels different from going on. Content fades and lifts rather than just
 * appearing, which is what stops each step from looking like a page reload.
 *
 * Direction is told to us rather than guessed: FlowFooter's Back button sets
 * `state.dir`, and the browser's own back button shows up as a POP. Anything
 * else counts as moving forward. Deriving it by remembering the last step
 * instead would mean writing to a ref or a module variable during render,
 * which misbehaves under StrictMode's double render.
 */
export default function PageTransition({ children }: { children: React.ReactNode }) {
  const location = useLocation()
  const navigationType = useNavigationType()
  const still = useReducedMotion()

  if (still) return <>{children}</>

  const back = (location.state as { dir?: string } | null)?.dir === 'back' || navigationType === 'POP'
  const offset = back ? -18 : 18

  return (
    <motion.div
      key={location.pathname}
      initial={{ opacity: 0, x: offset, y: 4 }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{ duration: 0.34, ease: [0.22, 0.61, 0.36, 1] }}
    >
      {children}
    </motion.div>
  )
}
