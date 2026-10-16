import axios from 'axios'

export const api = axios.create({ baseURL: '/api' })
export const db = axios.create({ baseURL: '/db' })

/** Pull FastAPI's {"detail": ...} out of an axios error. */
export function errorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail) return JSON.stringify(detail)
    return err.message
  }
  return String(err)
}
