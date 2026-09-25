import type { Metric } from '../types/api'
export function formatValue(value: number | null, unit: string) {
  if (value === null) return '—'
  const digits = unit === 'coefficient' ? 3 : unit === '%' || unit === 'RM million' || unit === 'thousand people' ? 1 : 0
  return value.toLocaleString('en-MY', { minimumFractionDigits: digits, maximumFractionDigits: digits })
}
export function changeText(m: Metric) {
  if (!m.change || !m.previous) return 'No previous observation'
  const c = m.change
  const value = c.percent ?? c.absolute
  const suffix = c.percent !== null ? '%' : c.unit === 'percentage points' ? ' pp' : c.unit === 'coefficient' ? '' : ` ${c.unit}`
  const digits = c.unit === 'coefficient' ? 3 : 1
  return `${value > 0 ? '+' : ''}${value.toFixed(digits)}${suffix} from ${m.previous.year}`
}
