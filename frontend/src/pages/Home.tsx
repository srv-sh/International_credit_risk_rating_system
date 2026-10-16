import { useMutation } from '@tanstack/react-query'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { runOcr } from '../api/endpoints'
import type { SheetKey } from '../api/types'
import { ErrorBox } from '../components/Status'
import { useAppStore, type UserInfo } from '../store/useAppStore'

const UPLOADS: { key: SheetKey; label: string }[] = [
  { key: 'bs', label: 'Balance Sheet image' },
  { key: 'is', label: 'Profit & Loss (Income) Sheet image' },
  { key: 'cfs', label: 'Cash Flow Sheet image' },
]

export default function Home() {
  const navigate = useNavigate()
  const { user, setUser, setOcr } = useAppStore()
  const [form, setForm] = useState<UserInfo>(user)
  const [files, setFiles] = useState<Partial<Record<SheetKey, File>>>({})
  const [useSaved, setUseSaved] = useState(false)

  const ocr = useMutation({
    mutationFn: () => runOcr(useSaved && !allFiles ? null : (files as Record<SheetKey, File>), useSaved),
    onSuccess: (data) => {
      setUser(form)
      setOcr(data)
      navigate('/balance-sheet')
    },
  })

  const allFiles = UPLOADS.every((u) => files[u.key])
  const userComplete = Object.values(form).every((v) => v.trim())
  const canSubmit = userComplete && (allFiles || useSaved) && !ocr.isPending

  return (
    <section className="page narrow">
      <h1>Home</h1>

      <h2>User information</h2>
      <div className="form-grid">
        {(['name', 'phone', 'email'] as const).map((field) => (
          <label key={field}>
            {field === 'name' ? 'Full name' : field[0].toUpperCase() + field.slice(1)}
            <input
              type={field === 'email' ? 'email' : 'text'}
              value={form[field]}
              onChange={(e) => setForm({ ...form, [field]: e.target.value })}
            />
          </label>
        ))}
        <label className="full">
          Address
          <textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        </label>
      </div>

      <h2>Statement images</h2>
      <div className="form-grid">
        {UPLOADS.map((u) => (
          <label key={u.key} className="full">
            {u.label}
            <input
              type="file"
              accept="image/png,image/jpeg"
              onChange={(e) => setFiles({ ...files, [u.key]: e.target.files?.[0] })}
            />
          </label>
        ))}
        <label className="checkbox full">
          <input type="checkbox" checked={useSaved} onChange={(e) => setUseSaved(e.target.checked)} />
          Use the saved OCR response (skips the OCR backend and LLM)
        </label>
      </div>

      <ErrorBox error={ocr.error} />
      <button className="primary" disabled={!canSubmit} onClick={() => ocr.mutate()}>
        {ocr.isPending ? 'Processing files…' : 'Next'}
      </button>
      {!userComplete && <p className="hint">Fill in all user details to continue.</p>}
    </section>
  )
}
