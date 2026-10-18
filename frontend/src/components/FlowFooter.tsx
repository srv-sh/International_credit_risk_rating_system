import { useLocation, useNavigate } from 'react-router-dom'
import { useFlow } from '../flow'

/**
 * Back and Continue for a step. Every page uses this and only this, so there
 * is one pair of controls in one place instead of a Next link in whatever
 * corner each page happened to put it.
 */
interface Props {
  /** Runs instead of plain navigation; resolve to false to stay put. */
  onContinue?: () => boolean | Promise<boolean>
  /** Why Continue is unavailable. Shown next to the button. */
  blockedBy?: string | null
  continueLabel?: string
  busy?: boolean
  /** Extra controls that belong to the step itself, e.g. Calculate. */
  children?: React.ReactNode
}

export default function FlowFooter({ onContinue, blockedBy, continueLabel, busy, children }: Props) {
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const { prev, next } = useFlow(pathname)

  const go = async () => {
    if (onContinue && (await onContinue()) === false) return
    if (next) navigate(next.path)
  }

  return (
    <div className="flow-footer">
      <div className="flow-footer-left">
        {prev && (
          // dir tells PageTransition to slide backwards; see that file.
          <button type="button" className="ghost" onClick={() => navigate(prev.path, { state: { dir: 'back' } })}>
            <svg viewBox="0 0 24 24" aria-hidden="true" className="chev"><path d="M15 6l-6 6 6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            {prev.short}
          </button>
        )}
      </div>

      <div className="flow-footer-right">
        {children}
        {blockedBy && <p className="flow-blocked">{blockedBy}</p>}
        {next && (
          <button type="button" className="primary" onClick={go} disabled={!!blockedBy || busy}>
            {busy ? 'Working…' : continueLabel ?? next.short}
            {!busy && <svg viewBox="0 0 24 24" aria-hidden="true" className="chev"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>}
          </button>
        )}
      </div>
    </div>
  )
}
