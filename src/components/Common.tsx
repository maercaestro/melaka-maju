import type { ReactNode } from 'react'
import { ArrowUpRight, Database, Info } from 'lucide-react'
import type { Metric, Selection, Source } from '../types/api'
import { useCatalogue } from '../hooks/queries'
import { changeText, formatValue } from '../utils/format'

export function Status({ pending, error }: { pending: boolean; error: Error | null }) {
  if (error) return <div role="alert" className="notice error"><strong>Data could not be loaded.</strong><p>{error.message}</p><p>Check that the backend is running and the official data cache is available.</p></div>
  if (pending) return <div role="status" className="loading"><span className="pulse" /> Loading official observations…</div>
  return null
}
export function PageTitle({ eyebrow, title, children }: { eyebrow: string; title: string; children: ReactNode }) {
  return <header className="page-heading"><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>{children}</p></header>
}
export function ModeControl({ selection, onChange }: { selection: Selection; onChange: (s: Selection) => void }) {
  const {data} = useCatalogue()
  return <div className="controlbar"><div className="segmented" aria-label="Data mode"><button aria-pressed={selection.mode==='latest'} className={selection.mode==='latest'?'selected':''} onClick={()=>onChange({...selection,mode:'latest'})}>Latest available</button><button aria-pressed={selection.mode==='same-year'} className={selection.mode==='same-year'?'selected':''} onClick={()=>onChange({...selection,mode:'same-year'})}>Same year</button></div>
  {selection.mode==='same-year' && <label className="inline-label">Year<select value={selection.year} onChange={e=>onChange({...selection,year:Number(e.target.value)})}>{[...new Set([selection.year,...(data?.years??[])])].sort((a,b)=>b-a).map(y=><option key={y}>{y}</option>)}</select></label>}
  <label className="universe"><span>Comparison universe</span><select value={String(selection.include)} onChange={e=>onChange({...selection,include:e.target.value==='true'})}><option value="false">States only</option><option value="true">States + Federal Territories</option></select></label></div>
}
export function SourceDetails({ source, year }: { source: Source; year: number | null }) {
  return <details className="source"><summary><Database size={12}/> Source</summary><div className="source-body"><strong>{source.title}</strong><p>{source.provider} · {source.dataset}</p><p>Observation: {year ?? 'Unavailable'}</p><p>Retrieved: {source.retrieved_at ? new Date(source.retrieved_at).toLocaleString('en-MY') : 'Not cached'}</p>{source.calculated && <p><strong>Calculated from official data</strong><br/>{source.calculation}</p>}{source.note && <p>{source.note}</p>}<a href={source.url} target="_blank" rel="noreferrer">Official source <ArrowUpRight size={13}/></a></div></details>
}
export function MetricCard({metric:m}: {metric:Metric}) {
  return <article className={`metric-card ${m.value===null?'unavailable':''}`}><div className="card-top"><h3>{m.label}</h3><span className="year">{m.year??'—'}</span></div><div className="metric-value">{formatValue(m.value,m.unit)}</div><div className="metric-unit">{m.unit}</div><p className="rank">{m.rank_label ?? (m.value===null?'No observation available':'Outside selected ranking universe')}</p>{m.comparison_count<m.eligible_count && m.value!==null && <small>{m.comparison_count} of {m.eligible_count} eligible areas have data.</small>}<div className="card-bottom"><span className="change">{m.value===null?'No other year substituted':changeText(m)}</span><SourceDetails source={m.source} year={m.year}/></div></article>
}
export function MetricSelect({value,onChange}:{value:string;onChange:(v:string)=>void}) {
 const {data}=useCatalogue()
 return <label>Indicator<select value={value} onChange={e=>onChange(e.target.value)}>{data?.metrics.map(m=><option key={m.id} value={m.id}>{m.label}</option>)}</select></label>
}
export function Note({children}:{children:ReactNode}) {return <div className="notice"><Info size={17}/><div>{children}</div></div>}
