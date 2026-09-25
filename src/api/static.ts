import type {
  Catalogue,
  Comparison,
  DatasetList,
  Metric,
  Overview,
  QuarterlyUnemployment,
  Rankings,
  RawData,
  Trend,
} from '../types/api'

type Scope = 'states' | 'all'
type Variants<T> = {
  latest: Record<Scope, T>
  years: Record<string, Record<Scope, T>>
}
type QuarterlyFile = {
  periods: string[]
  source: QuarterlyUnemployment['source']
  observations: Record<string, QuarterlyUnemployment['observations']>
  snapshots: Record<string, Record<Scope, QuarterlyUnemployment>>
}

const cache = new Map<string, Promise<unknown>>()

function load<T>(file: string): Promise<T> {
  const url = `${import.meta.env.BASE_URL}static-api/${file}`
  if (!cache.has(url)) {
    cache.set(url, fetch(url).then(response => {
      if (!response.ok) throw new Error(`Static data unavailable (${response.status})`)
      return response.json()
    }))
  }
  return cache.get(url) as Promise<T>
}

function scope(params: URLSearchParams): Scope {
  return params.get('include_federal_territories') === 'true' ? 'all' : 'states'
}

function select<T>(data: Variants<T>, params: URLSearchParams): T {
  const year = params.get('year')
  const variant = year ? data.years[year] : data.latest
  if (!variant) throw new Error(`No static data for year ${year}`)
  return variant[scope(params)]
}

function stateMetric(ranking: Rankings, allRanking: Rankings, state: string): Metric {
  const metric = ranking.states.find(item => item.state === state)
  if (metric) return metric
  const fallback = allRanking.states.find(item => item.state === state)
  if (!fallback) throw new Error(`Unknown state: ${state}`)
  return {
    ...fallback,
    rank: null,
    rank_label: null,
    comparison_count: ranking.comparison_count,
    eligible_count: ranking.eligible_count,
  }
}

function normalizeState(value: string): string {
  const aliases: Record<string, string> = {
    Malacca: 'Melaka',
    Penang: 'Pulau Pinang',
    'Kuala Lumpur': 'W.P. Kuala Lumpur',
    Putrajaya: 'W.P. Putrajaya',
    Labuan: 'W.P. Labuan',
  }
  return aliases[value.trim()] ?? value.trim()
}

async function rawData(dataset: string, params: URLSearchParams): Promise<RawData> {
  const data = await load<RawData>(`raw/${dataset}.json`)
  const state = params.get('state')
  const year = params.get('year')
  const sector = params.get('sector')
  const series = params.get('series')
  const offset = Number(params.get('offset') ?? 0)
  const limit = Number(params.get('limit') ?? 100)
  const filtered = data.rows.filter(row => {
    if (state && normalizeState(String(row.state ?? '')) !== normalizeState(state)) return false
    if (year && !String(row.date ?? '').startsWith(year)) return false
    if (sector && row.sector !== sector) return false
    if (series && row.series !== series) return false
    return true
  })
  return {...data, total: filtered.length, offset, limit, rows: filtered.slice(offset, offset + limit)}
}

async function comparison(params: URLSearchParams): Promise<Comparison> {
  const metric = params.get('metric') ?? ''
  const data = await load<Variants<Rankings>>(`rankings/${metric}.json`)
  const ranking = select(data, params)
  const allParams = new URLSearchParams(params)
  allParams.set('include_federal_territories', 'true')
  const allRanking = select(data, allParams)
  const states = (params.get('states') ?? '').split(',').filter(Boolean)
  return {
    metric,
    year: ranking.year,
    mixed_years: false,
    states: states.map(state => stateMetric(ranking, allRanking, state)),
  }
}

async function quarterly(params: URLSearchParams): Promise<QuarterlyUnemployment> {
  const data = await load<QuarterlyFile>('quarterly.json')
  const period = params.get('period') || data.periods[0]
  const state = params.get('state') ?? 'Melaka'
  const snapshots = data.snapshots[period]
  if (!snapshots) throw new Error(`No static data for period ${period}`)
  const selected = snapshots[scope(params)]
  const allMetric = snapshots.all.states.find(item => item.state === state)
  const metric = selected.states.find(item => item.state === state) ?? (allMetric && {
    ...allMetric,
    rank: null,
    rank_label: null,
    comparison_count: selected.comparison_count,
  })
  if (!metric) throw new Error(`Unknown state: ${state}`)
  return {...selected, state, metric, observations: data.observations[state] ?? []}
}

export async function getStatic<T>(path: string): Promise<T> {
  const url = new URL(path, 'https://static.local')
  if (url.pathname === '/health') return {status: 'ok'} as T
  if (url.pathname === '/catalogue') return load<Catalogue>('catalogue.json') as Promise<T>
  if (url.pathname === '/datasets') return load<DatasetList>('datasets.json') as Promise<T>
  if (url.pathname === '/compare') return comparison(url.searchParams) as Promise<T>
  if (url.pathname === '/labour/unemployment-quarterly') return quarterly(url.searchParams) as Promise<T>

  const overviewMatch = url.pathname.match(/^\/state\/(.+)\/overview$/)
  if (overviewMatch) {
    const state = decodeURIComponent(overviewMatch[1])
    const data = await load<Variants<Overview>>(`overviews/${encodeURIComponent(state)}.json`)
    return select(data, url.searchParams) as T
  }

  const rankingsMatch = url.pathname.match(/^\/rankings\/(.+)$/)
  if (rankingsMatch) {
    const metric = decodeURIComponent(rankingsMatch[1])
    const data = await load<Variants<Rankings>>(`rankings/${encodeURIComponent(metric)}.json`)
    return select(data, url.searchParams) as T
  }

  const trendsMatch = url.pathname.match(/^\/trends\/(.+)$/)
  if (trendsMatch) {
    const metric = decodeURIComponent(trendsMatch[1])
    const data = await load<Record<string, Trend>>(`trends/${encodeURIComponent(metric)}.json`)
    const state = url.searchParams.get('state') ?? 'Melaka'
    if (!data[state]) throw new Error(`Unknown state: ${state}`)
    return data[state] as T
  }

  const rawMatch = url.pathname.match(/^\/datasets\/([^/]+)\/raw$/)
  if (rawMatch) return rawData(decodeURIComponent(rawMatch[1]), url.searchParams) as Promise<T>
  throw new Error(`Unsupported static API path: ${url.pathname}`)
}