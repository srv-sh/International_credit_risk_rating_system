import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { createContext, useCallback, useContext, useMemo, useState } from 'react'

/**
 * Transient feedback: saved, calculated, storage unreachable.
 *
 * Ported from bencho.dev/blocks/toast-stack (MIT). The point of that block is
 * the resting state: the newest toast sits in front with the older ones
 * peeking out behind it, and pointing at the pile springs them apart into a
 * readable list. Errors stay until dismissed; everything else times out.
 */

export type ToastKind = 'ok' | 'warn' | 'error'

interface Toast {
  id: number
  kind: ToastKind
  text: string
}

interface Api {
  push: (kind: ToastKind, text: string) => void
}

const ToastContext = createContext<Api>({ push: () => {} })
export const useToast = () => useContext(ToastContext)

const SPRING = { type: 'spring' as const, stiffness: 420, damping: 34 }
const LIFETIME = 4500
const SHOWN = 3

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const [open, setOpen] = useState(false)
  const still = useReducedMotion()

  const drop = useCallback((id: number) => setToasts((t) => t.filter((x) => x.id !== id)), [])

  const push = useCallback((kind: ToastKind, text: string) => {
    const id = Date.now() + Math.random()
    setToasts((t) => [...t, { id, kind, text }])
    if (kind !== 'error') setTimeout(() => drop(id), LIFETIME)
  }, [drop])

  const api = useMemo(() => ({ push }), [push])

  // Newest in front. Only the last few are rendered; the rest are dropped
  // rather than left to pile up off-screen.
  const visible = toasts.slice(-SHOWN).reverse()

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div
        className={`toast-stack${open ? ' is-open' : ''}`}
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        aria-live="polite"
        aria-relevant="additions"
      >
        <AnimatePresence initial={false}>
          {visible.map((t, depth) => (
            <motion.div
              key={t.id}
              className={`toast toast-${t.kind}`}
              initial={still ? false : { opacity: 0, y: 14, scale: 0.95 }}
              animate={still ? { opacity: 1 } : {
                opacity: 1,
                // Fanned out into a list on hover, stacked when at rest.
                y: open ? depth * 62 : depth * -7,
                scale: open ? 1 : 1 - depth * 0.04,
                zIndex: SHOWN - depth,
              }}
              exit={still ? undefined : { opacity: 0, scale: 0.95, transition: { duration: 0.14 } }}
              transition={SPRING}
              style={{ position: 'absolute', right: 0, bottom: 0, width: '100%' }}
            >
              <span className="toast-dot" aria-hidden="true" />
              <p>{t.text}</p>
              <button type="button" className="toast-close" aria-label="Dismiss" onClick={() => drop(t.id)}>
                <svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" fill="none" /></svg>
              </button>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}
