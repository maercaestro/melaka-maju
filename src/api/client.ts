const base = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')
export async function get<T>(path: string): Promise<T> {
  const response = await fetch(`${base}/api${path}`)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(typeof body.detail === 'string' ? body.detail : `Request failed (${response.status})`)
  }
  return response.json()
}
export function query(params: Record<string, string | number | boolean | undefined>) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => { if (value !== undefined && value !== '') search.set(key, String(value)) })
  return `?${search}`
}
