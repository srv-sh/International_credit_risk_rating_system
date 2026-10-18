import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { runOcr } from '../api/endpoints'
import type { SheetKey } from '../api/types'
import FlowFooter from '../components/FlowFooter'
import { errorMessage } from '../api/client'
import { ErrorBox } from '../components/Status'
import UploadDropzone from '../components/blocks/UploadDropzone'
import { useToast } from '../components/blocks/ToastStack'
import { useAppStore, type UserInfo } from '../store/useAppStore'

const UPLOADS: { key: SheetKey; label: string }[] = [
  { key: 'bs', label: 'Balance sheet' },
  { key: 'is', label: 'Profit & loss (income statement)' },
  { key: 'cfs', label: 'Cash flow statement' },
]

const FIELDS: { key: keyof UserInfo; label: string; type: string; autoComplete: string }[] = [
  { key: 'name', label: 'Full name', type: 'text', autoComplete: 'name' },
  { key: 'phone', label: 'Phone', type: 'tel', autoComplete: 'tel' },
  { key: 'email', label: 'Email', type: 'email', autoComplete: 'email' },
]

export default function Home() {
  const { user, setUser, setOcr } = useAppStore()
  const toast = useToast()
  const [form, setForm] = useState<UserInfo>(user)
  const [files, setFiles] = useState<Partial<Record<SheetKey, File>>>({})
  const [useSaved, setUseSaved] = useState(false)
  const [touched, setTouched] = useState<Partial<Record<keyof UserInfo, boolean>>>({})

  const allFiles = UPLOADS.every((u) => files[u.key])

  const ocr = useMutation({
    mutationFn: () => runOcr(useSaved && !allFiles ? null : (files as Record<SheetKey, File>), useSaved),
    onSuccess: (data) => {
      setUser(form)
      setOcr(data)
      toast.push('ok', data.source === 'saved'
        ? 'Loaded the saved extraction. Check each statement before calculating.'
        : 'Statements extracted. Check each one before calculating.')
    },
    onError: () => toast.push('error', 'Extraction failed. Nothing was changed.'),
  })

  // The OCR service is a separate deployment, so an unreachable backend is a
  // setup problem rather than something the user did wrong. Say so plainly and
  // keep the raw message available for whoever has to fix it.
  const unreachable = !!ocr.error && /could not reach backend|connection refused|network error/i
    .test(errorMessage(ocr.error))

  const missingUser = FIELDS.filter((f) => !form[f.key].trim()).map((f) => f.label)
  const addressMissing = !form.address.trim()
  const userComplete = missingUser.length === 0 && !addressMissing

  const blockedBy = !userComplete
    ? 'Fill in the applicant details to continue'
    : !allFiles && !useSaved
      ? 'Add all three statement images, or use the saved extraction'
      : null

  const err = (key: keyof UserInfo) => touched[key] && !form[key].trim()

  return (
    <section className="page narrow">
      <div className="page-head">
        <h1>New credit rating</h1>
        <p className="lede">
          The rating is built from three financial statements. Everything after this step is derived
          from what you provide here.
        </p>
      </div>

      <FlowFooter
        blockedBy={blockedBy}
        busy={ocr.isPending}
        continueLabel={ocr.isPending ? 'Extracting…' : 'Extract statements'}
        onContinue={async () => {
          await ocr.mutateAsync()
          return true
        }}
      />

      <fieldset className="card">
        <legend>Applicant</legend>
        <div className="form-grid">
          {FIELDS.map((f) => (
            <label key={f.key} className="field">
              <span>{f.label} <abbr title="required" aria-label="required">*</abbr></span>
              <input
                type={f.type}
                autoComplete={f.autoComplete}
                value={form[f.key]}
                aria-invalid={err(f.key) || undefined}
                onBlur={() => setTouched({ ...touched, [f.key]: true })}
                onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
              />
              {err(f.key) && <small className="field-error">{f.label} is required</small>}
            </label>
          ))}
          <label className="field full">
            <span>Address <abbr title="required" aria-label="required">*</abbr></span>
            <textarea
              rows={2}
              autoComplete="street-address"
              value={form.address}
              aria-invalid={(touched.address && addressMissing) || undefined}
              onBlur={() => setTouched({ ...touched, address: true })}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
            />
            {touched.address && addressMissing && <small className="field-error">Address is required</small>}
          </label>
        </div>
      </fieldset>

      <fieldset className="card">
        <legend>Statement images</legend>
        <p className="hint">
          One image per statement. They are read in order, so check that each one is in the right slot.
        </p>
        <div className="dropzones">
          {UPLOADS.map((u) => (
            <UploadDropzone
              key={u.key}
              label={u.label}
              file={files[u.key]}
              onFile={(f) => setFiles({ ...files, [u.key]: f })}
            />
          ))}
        </div>
        <label className="checkbox">
          <input type="checkbox" checked={useSaved} onChange={(e) => setUseSaved(e.target.checked)} />
          <span>
            Use the saved extraction
            <small>Skips the OCR backend and the LLM. Useful for a dry run without uploading anything.</small>
          </span>
        </label>
      </fieldset>

      {ocr.error && (unreachable ? (
        <div className="alert error" role="alert">
          <strong>The OCR service is not responding.</strong> It runs separately from this app, so
          extraction cannot start until it is up. Nothing was changed and your files are still
          attached. To carry on without it, tick "Use the saved extraction" above.
          <details>
            <summary>Technical detail</summary>
            <code>{errorMessage(ocr.error)}</code>
          </details>
        </div>
      ) : <ErrorBox error={ocr.error} />)}

    </section>
  )
}
