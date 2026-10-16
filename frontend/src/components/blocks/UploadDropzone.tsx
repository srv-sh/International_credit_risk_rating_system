import { AnimatePresence, motion, useReducedMotion } from 'framer-motion'
import { useRef, useState } from 'react'

/**
 * Drop target for one statement image.
 *
 * Ported from bencho.dev/blocks/upload-dropzone (MIT). Keeps the three things
 * that block actually does: the file is drawn into the box, it fills a
 * progress bar and ticks, and a file it will not take is refused with a shake
 * that gets harder each time you try the same thing.
 */

const SPRING = { type: 'spring' as const, stiffness: 520, damping: 32 }
const MAX_BYTES = 10 * 1024 * 1024

interface Props {
  label: string
  file: File | undefined
  onFile: (file: File | undefined) => void
  accept?: string
}

const kb = (n: number) => (n < 1024 * 1024 ? `${Math.round(n / 1024)} KB` : `${(n / (1024 * 1024)).toFixed(1)} MB`)

export default function UploadDropzone({ label, file, onFile, accept = 'image/png,image/jpeg' }: Props) {
  const still = useReducedMotion()
  const input = useRef<HTMLInputElement>(null)
  const [over, setOver] = useState(false)
  const [refusals, setRefusals] = useState(0)
  const [refusal, setRefusal] = useState<string | null>(null)
  const [progress, setProgress] = useState(0)

  // The block's progress bar. Reading a local file is instant, so this is the
  // decode, not a network upload: it ends when the preview is actually ready.
  const accept_ = (next: File) => {
    if (!next.type.startsWith('image/')) return refuse(`${next.name} is not an image`)
    if (next.size > MAX_BYTES) return refuse(`${next.name} is ${kb(next.size)}, over the 10 MB limit`)
    setRefusal(null)
    setRefusals(0)
    setProgress(0.15)
    const reader = new FileReader()
    reader.onprogress = (e) => e.lengthComputable && setProgress(0.15 + 0.85 * (e.loaded / e.total))
    reader.onloadend = () => {
      setProgress(1)
      onFile(next)
    }
    reader.readAsArrayBuffer(next)
  }

  const refuse = (why: string) => {
    setRefusal(why)
    setRefusals((n) => n + 1)
    setProgress(0)
  }

  const clear = () => {
    onFile(undefined)
    setProgress(0)
    setRefusal(null)
    if (input.current) input.current.value = ''
  }

  // Each refusal of the same box shakes a little further, to a ceiling.
  const shake = Math.min(refusals, 4)

  return (
    <div className="dropzone-field">
      <span className="dropzone-label">{label}</span>
      <motion.div
        className={`dropzone${over ? ' is-over' : ''}${file ? ' is-filled' : ''}${refusal ? ' is-refused' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setOver(true) }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setOver(false)
          const dropped = e.dataTransfer.files?.[0]
          if (dropped) accept_(dropped)
        }}
        onClick={() => input.current?.click()}
        onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); input.current?.click() } }}
        role="button"
        tabIndex={0}
        aria-label={`${label}. Choose an image or drop one here.`}
        animate={still ? {} : { scale: over ? 1.015 : 1, x: refusal ? [0, -5 * shake, 5 * shake, -3 * shake, 0] : 0 }}
        transition={SPRING}
        key={`${refusals}`}
      >
        <input
          ref={input}
          type="file"
          accept={accept}
          hidden
          onChange={(e) => { const f = e.target.files?.[0]; if (f) accept_(f) }}
        />

        <AnimatePresence mode="wait" initial={false}>
          {file ? (
            <motion.div
              key="filled"
              className="dropzone-file"
              initial={still ? false : { opacity: 0, y: 8, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={still ? undefined : { opacity: 0, y: -6 }}
              transition={SPRING}
            >
              <motion.svg
                className="dropzone-tick" viewBox="0 0 24 24" aria-hidden="true"
                initial={still ? false : { scale: 0.4 }} animate={{ scale: 1 }} transition={{ ...SPRING, damping: 14 }}
              >
                <motion.path
                  d="M20 6 9 17l-5-5" fill="none" stroke="currentColor" strokeWidth="2.5"
                  strokeLinecap="round" strokeLinejoin="round"
                  initial={still ? false : { pathLength: 0 }} animate={{ pathLength: 1 }}
                  transition={{ duration: still ? 0 : 0.28, ease: 'easeOut' }}
                />
              </motion.svg>
              <span className="dropzone-name" title={file.name}>{file.name}</span>
              <span className="dropzone-size">{kb(file.size)}</span>
              <button type="button" className="ghost sm" onClick={(e) => { e.stopPropagation(); clear() }}>Replace</button>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              className="dropzone-empty"
              initial={still ? false : { opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={still ? undefined : { opacity: 0 }}
            >
              <svg viewBox="0 0 24 24" aria-hidden="true" className="dropzone-icon">
                <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
              </svg>
              <span><strong>Choose an image</strong> or drop it here</span>
              <span className="dropzone-meta">PNG or JPEG, up to 10 MB</span>
            </motion.div>
          )}
        </AnimatePresence>

        {progress > 0 && progress < 1 && (
          <motion.div className="dropzone-progress" initial={{ scaleX: 0 }} animate={{ scaleX: progress }} transition={{ ease: 'easeOut' }} />
        )}
      </motion.div>

      <AnimatePresence>
        {refusal && (
          <motion.p
            className="dropzone-refusal" role="alert"
            initial={still ? false : { opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={still ? undefined : { opacity: 0, height: 0 }}
          >
            {refusal}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  )
}
