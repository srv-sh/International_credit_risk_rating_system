import { errorMessage } from '../api/client'

export function ErrorBox({ error }: { error: unknown }) {
  if (!error) return null
  return <div className="alert error">{errorMessage(error)}</div>
}

export function Notice({ children }: { children: React.ReactNode }) {
  return <div className="alert">{children}</div>
}
