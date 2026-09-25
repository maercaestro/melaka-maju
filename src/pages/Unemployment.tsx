import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useCatalogue, useQuarterlyUnemployment } from '../hooks/queries'
import { Note, PageTitle, SourceDetails, Status } from '../components/Common'
import { formatValue } from '../utils/format'
import type { QuarterSnapshot } from '../types/api'

function changeText(m: QuarterSnapshot) {
  if (!m.change || !m.previous) return 'No previous observation'
  return `${m.change.absolute > 0 ? '+' : ''}${m.change.absolute.toFixed(1)} pp from ${m.previous.period}`
}

export default function Unemployment() {
  const [state, setState] = useState('Melaka')
  const [period, setPeriod] = useState('')
  const [include, setInclude] = useState(false)
  const catalogue = useCatalogue()
  const q = useQuarterlyUnemployment(state, period, include)
  const data = q.data
  return <>
    <PageTitle eyebrow="QUARTERLY LABOUR MARKET" title="Unemployment, quarter by quarter.">Published unemployment rates from the DOSM Labour Force Survey. Select a quarter to compare states on the same basis.</PageTitle>
    <div className="filters">
      <label>State<select value={state} onChange={e => setState(e.target.value)}>{[...(catalogue.data?.states ?? ['Melaka']), ...(catalogue.data?.territories ?? [])].map(s => <option key={s}>{s}</option>)}</select></label>
      <label>Quarter<select value={period} onChange={e => setPeriod(e.target.value)}><option value="">Latest available quarter</option>{data?.periods.map(p => <option key={p}>{p}</option>)}</select></label>
      <label>Comparison universe<select value={String(include)} onChange={e => setInclude(e.target.value === 'true')}><option value="false">States only</option><option value="true">States + Federal Territories</option></select></label>
    </div>
    <Note>Quarterly observations are distinct from annual rates. Selecting 2024-Q4 shows that quarter, not a 2024 annual estimate. Changes below are in percentage points.</Note>
    <Status pending={q.isPending} error={q.error}/>
    {data && <>
      <article className="metric-card" style={{maxWidth:420}}>
        <div className="card-top"><h3>{state} · unemployment rate</h3><span className="year">{data.period}</span></div>
        <div className="metric-value">{formatValue(data.metric.value, '%')}{data.metric.value !== null && '%'}</div>
        <p className="rank">{data.metric.rank_label ?? (data.metric.value === null ? 'No observation available' : 'Outside selected ranking universe')}</p>
        <div className="card-bottom"><span className="change">{changeText(data.metric)}</span><SourceDetails source={data.source} year={data.metric.year}/></div>
      </article>
      <div className="chart-panel"><div className="table-heading"><h2>{state} unemployment trend</h2><span>% · actual quarterly observations</span></div>
        {data.observations.length ? <ResponsiveContainer width="100%" height={340}><LineChart data={data.observations} margin={{top:15,right:25,left:5,bottom:20}}><CartesianGrid strokeDasharray="3 4" vertical={false}/><XAxis dataKey="period" minTickGap={35}/><YAxis unit="%"/><Tooltip formatter={v => [`${formatValue(Number(v), '%')}%`, 'Unemployment']} labelFormatter={v => `Quarter: ${v}`}/><Line dataKey="value" name="Unemployment" type="linear" stroke="#16765c" strokeWidth={2} dot={{r:3}}/></LineChart></ResponsiveContainer> : <p>No observations available.</p>}
      </div>
      <div className="table-heading"><h2>State rankings · {data.period}</h2><span>{data.comparison_count} of {data.eligible_count} areas with observations</span></div>
      <Note>Rank 1 is the lowest unemployment rate. Ties share a rank. All rows refer to {data.period}; missing observations are not substituted.</Note>
      <div className="table-wrap"><table><thead><tr><th>Rank</th><th>State</th><th>Unemployment</th><th>Quarter</th><th>Previous observation</th><th>Change</th></tr></thead><tbody>{data.states.map(m => <tr key={m.state} className={m.state === 'Melaka' ? 'highlight' : ''}><td>{m.rank ?? '—'}</td><td>{m.state}</td><td>{m.value === null ? 'No observation available' : `${formatValue(m.value, '%')}%`}</td><td>{m.period}</td><td>{m.previous ? `${formatValue(m.previous.value, '%')}% (${m.previous.period})` : '—'}</td><td>{changeText(m)}</td></tr>)}</tbody></table></div>
      <details className="observation-table"><summary>Inspect {state} quarterly observations</summary><div className="table-wrap"><table><thead><tr><th>Quarter</th><th>Unemployment rate</th></tr></thead><tbody>{data.observations.map(o => <tr key={o.period}><td>{o.period}</td><td>{formatValue(o.value, '%')}%</td></tr>)}</tbody></table></div></details>
      <SourceDetails source={data.source} year={data.metric.year}/>
    </>}
  </>
}
