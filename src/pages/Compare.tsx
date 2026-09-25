import { useState } from 'react'
import type { Selection } from '../types/api'
import { useCatalogue, useComparison } from '../hooks/queries'
import { ModeControl, Note, PageTitle, SourceDetails, Status } from '../components/Common'
import { formatValue } from '../utils/format'
const metrics=['gdp_per_capita','gdp_growth','median_household_income','gini','poverty','labour_productivity','manufacturing_share','unemployment']
function ComparisonRow({metric,states,selection}:{metric:string;states:string[];selection:Selection}) {
 const q=useComparison(metric,states,selection)
 if(q.error) return <tr><td colSpan={states.length+1}><Status pending={false} error={q.error}/></td></tr>
 if(!q.data) return <tr><td colSpan={states.length+1}>{states.length?'Loading indicator…':'Select at least one state.'}</td></tr>
 return <tr><th>{q.data.states[0]?.label}<small>{q.data.states[0]?.unit}</small></th>{q.data.states.map(m=><td className={m.state==='Melaka'?'highlight':''} key={m.state}><strong className="compare-number">{formatValue(m.value,m.unit)}</strong><span className="compare-year">{m.year} · {m.value===null?'No observation available':m.rank_label}</span><SourceDetails source={m.source} year={m.year}/></td>)}</tr>
}
export default function Compare({selection,onChange}:{selection:Selection;onChange:(s:Selection)=>void}) {
 const [states,setStates]=useState(['Melaka','Johor','Negeri Sembilan','Pulau Pinang','Selangor'])
 const catalogue=useCatalogue()
 return <><PageTitle eyebrow="SIDE BY SIDE" title="Put the numbers in perspective.">Select states to compare economic output and household welfare.</PageTitle><ModeControl selection={selection} onChange={onChange}/><fieldset className="state-picker"><legend>Comparison states</legend>{[...(catalogue.data?.states??[]),...(catalogue.data?.territories??[])].map(s=><label className={states.includes(s)?'active':''} key={s}><input type="checkbox" checked={states.includes(s)} onChange={e=>setStates(e.target.checked?[...states,s]:states.filter(v=>v!==s))}/>{s}</label>)}</fieldset><Note>{selection.mode==='latest'?'Each indicator uses its latest shared year across the selected states. Years can differ between indicators.':`All indicators use ${selection.year}.`} Missing values remain unavailable.</Note><div className="table-wrap"><table className="compare-table"><thead><tr><th>Indicator</th>{states.map(s=><th key={s} className={s==='Melaka'?'highlight':''}>{s}</th>)}</tr></thead><tbody>{metrics.map(metric=><ComparisonRow key={metric} metric={metric} states={states} selection={selection}/>)}</tbody></table></div></>
}
