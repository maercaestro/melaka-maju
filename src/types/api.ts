export interface Source { provider: string; dataset: string; title: string; url: string; retrieved_at: string | null; sha256: string | null; calculated: boolean; calculation: string | null; note: string | null }
export interface Metric { id: string; label: string; state: string; value: number | null; unit: string; year: number | null; rank: number | null; comparison_count: number; eligible_count: number; ranking_direction: string; rank_label: string | null; previous: { year: number; value: number } | null; change: { absolute: number; percent: number | null; unit: string } | null; source: Source; status: string }
export interface Overview { state: string; mode: string; year: number | null; mixed_years: boolean; include_federal_territories: boolean; metrics: Metric[] }
export interface Definition { id: string; label: string; unit: string; group: string; direction: string; years: number[] }
export interface Catalogue { metrics: Definition[]; years: number[]; states: string[]; territories: string[] }
export interface Rankings { metric: string; year: number | null; comparison_count: number; eligible_count: number; missing_states: string[]; states: Metric[] }
export interface Trend { metric: string; label: string; unit: string; state: string; observations: { year: number; value: number; source: Source }[]; annotation: { source_url: string; date: string; label: string; note: string } }
export interface Comparison { metric: string; year: number | null; mixed_years: boolean; states: Metric[] }
export interface Dataset { id: string; title: string; provider: string; source_url: string; url: string; frequency: string; max_year?: number; years?: number[]; retrieved_at?: string; note?: string; format: string }
export interface DatasetList { datasets: Dataset[]; discovery: Record<string, { status: string; source_url: string; note: string }> }
export interface RawData { dataset: Dataset; columns: string[]; filters: Record<string, string[]>; total: number; offset: number; limit: number; rows: Record<string, string | number | null>[] }
export interface Selection { mode: 'latest' | 'same-year'; year: number; include: boolean }

export interface QuarterObservation { year: number; quarter: number; period: string; value: number | null }
export interface QuarterSnapshot extends QuarterObservation { state: string; rank: number | null; comparison_count: number; rank_label: string | null; previous: QuarterObservation | null; change: Metric['change'] }
export interface QuarterlyUnemployment { state: string; frequency: 'quarterly'; unit: string; period: string; periods: string[]; metric: QuarterSnapshot; states: QuarterSnapshot[]; eligible_count: number; comparison_count: number; observations: QuarterObservation[]; source: Source }
