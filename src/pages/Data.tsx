import { useState } from 'react'
import { Download, ArrowUpRight } from 'lucide-react'
import { useDatasets, useRawData } from '../hooks/queries'
import { Note, PageTitle, Status } from '../components/Common'
function csvCell(value: unknown) {
 const text=String(value??'')
 // Neutralize spreadsheet formula interpretation in text cells.
 const safe=/^[=+@-]/.test(text)&&typeof value==='string'?`'${text}`:text
 return `"${safe.replaceAll('"','""')}"`
}
export default function Data() {
 const datasets=useDatasets()
 const [dataset,setDataset]=useState('hies_state'),[filters,setFilters]=useState<Record<string,string>>({}),[offset,setOffset]=useState(0)
 const q=useRawData(dataset,{...filters,offset,limit:100})
 function exportPage() {
  if(!q.data)return
  const {columns,rows}=q.data
  const text=[columns.map(csvCell).join(','),...rows.map(row=>columns.map(c=>csvCell(row[c])).join(','))].join('\r\n')
  const url=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8;'}))
  const a=document.createElement('a');a.href=url;a.download=`${dataset}-rows-${offset}.csv`;a.click();URL.revokeObjectURL(url)
 }
 const d=q.data?.dataset
 return <><PageTitle eyebrow="SOURCE EXPLORER" title="See the evidence for yourself.">Inspect the source rows behind every indicator. Download a page of results for your own analysis.</PageTitle><Status pending={datasets.isPending} error={datasets.error}/><div className="filters"><label className="dataset-select">Dataset<select value={dataset} onChange={e=>{setDataset(e.target.value);setFilters({});setOffset(0)}}>{datasets.data?.datasets.map(d=><option value={d.id} key={d.id}>{d.title}</option>)}</select></label>{['state','year','sector','series'].map(field=><label key={field}>{field.charAt(0).toUpperCase()+field.slice(1)}<select disabled={!q.data?.filters[field]} value={filters[field]??''} onChange={e=>{setFilters({...filters,[field]:e.target.value});setOffset(0)}}><option value="">All</option>{q.data?.filters[field]?.map(v=><option key={v}>{v}</option>)}</select></label>)}</div><Status pending={q.isPending} error={q.error}/>{d&&<div className="dataset-info"><div><span className="eyebrow">{d.provider} · {d.frequency}</span><h2>{d.title}</h2><p>Latest observation: {d.max_year??'—'} · Retrieved: {d.retrieved_at?new Date(d.retrieved_at).toLocaleString('en-MY'):'—'}</p><code>{d.id}</code><p>{d.note}</p></div><a className="text-link" href={d.source_url} target="_blank" rel="noreferrer">Official source <ArrowUpRight size={16}/></a></div>}{d?.format==='xlsx'&&<Note>Rows are a deterministic extraction from the official Excel table. Sheet and cell coordinates are preserved. <a href={d.url}>Download the original workbook.</a></Note>}{q.data&&<><div className="table-heading"><span>{q.data.total.toLocaleString()} matching source rows</span><button className="button" onClick={exportPage} disabled={!q.data.rows.length}><Download size={15}/> Export this page as CSV</button></div><div className="table-wrap"><table><thead><tr>{q.data.columns.map(c=><th key={c}>{c}</th>)}</tr></thead><tbody>{q.data.rows.map((row,i)=><tr key={i}>{q.data.columns.map(c=><td key={c}>{row[c]===null?'—':String(row[c])}</td>)}</tr>)}</tbody></table>{q.data.rows.length===0&&<p className="empty">No source rows match these filters.</p>}</div><div className="pagination"><button className="button" disabled={offset===0} onClick={()=>setOffset(offset-100)}>Previous</button><span>Rows {q.data.rows.length?offset+1:0}–{offset+q.data.rows.length} of {q.data.total}</span><button className="button" disabled={offset+100>=q.data.total} onClick={()=>setOffset(offset+100)}>Next</button></div></>}<section className="methodology"><h2>Coverage & methodology</h2><p>GDP is output, not household income. Monetary household indicators are nominal. Survey gaps remain gaps. Rankings use the selected universe and count only available observations. Published revisions can change historical ranks.</p>{Object.entries(datasets.data?.discovery??{}).map(([key,item])=><p key={key}><strong>{key.replaceAll('_',' ')} · Phase 2:</strong> {item.note} <a href={item.source_url} target="_blank" rel="noreferrer">Source identified ↗</a></p>)}</section></>
}
