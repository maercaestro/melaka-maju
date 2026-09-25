import { lazy, Suspense, useState } from 'react'
import { NavLink, Route, Routes, Link } from 'react-router-dom'
import { ArrowUpRight, BarChart3, Database, GitCompareArrows, LayoutDashboard, TrendingUp } from 'lucide-react'
import { useHealth } from './hooks/queries'
import type { Selection } from './types/api'
import Home from './pages/Home'
import Rankings from './pages/Rankings'
const Unemployment = lazy(() => import('./pages/Unemployment'))
const Trends = lazy(() => import('./pages/Trends'))
import Compare from './pages/Compare'
import Data from './pages/Data'
const navigation=[['/','Overview',LayoutDashboard],['/rankings','Rankings',BarChart3],['/trends','Trends',TrendingUp],['/compare','Compare',GitCompareArrows],['/unemployment','Unemployment',TrendingUp],['/data','Raw data',Database]] as const
export default function App() {
 const health=useHealth()
 const [selection,setSelection]=useState<Selection>({mode:'same-year',year:2024,include:false})
 return <div className="app-shell"><header className="site-header"><div className="header-inner"><Link to="/" className="brand"><span className="brand-symbol">m<span>m</span></span><span>Melaka Maju<small>OFFICIAL DATA. OPEN PERSPECTIVE.</small></span></Link><a className="official-link" href="https://open.dosm.gov.my" target="_blank" rel="noreferrer">Powered by official data <ArrowUpRight size={15}/></a></div><nav className="navigation" aria-label="Main navigation">{navigation.map(([path,label,Icon])=><NavLink key={path} end={path==='/'} to={path}><Icon size={17}/>{label}</NavLink>)}<span className={`api-status ${health.data?'connected':''}`} title={health.error?.message??'Vite ↔ FastAPI health'}><span/>{health.data?'API connected':health.error?'API unavailable':'Connecting'}</span></nav></header><main className="main-content"><Routes><Route path="/" element={<Home selection={selection} onChange={setSelection}/>}/><Route path="/rankings" element={<Rankings selection={selection} onChange={setSelection}/>}/><Route path="/trends" element={<Suspense fallback={<p>Loading chart…</p>}><Trends/></Suspense>}/><Route path="/compare" element={<Compare selection={selection} onChange={setSelection}/>}/><Route path="/unemployment" element={<Suspense fallback={<p>Loading quarterly observations…</p>}><Unemployment/></Suspense>}/><Route path="/data" element={<Data/>}/><Route path="*" element={<div className="empty"><h1>Page not found</h1><Link to="/">Return to the overview</Link></div>}/></Routes></main><footer><div><strong>Melaka Maju</strong><p>Understanding Melaka through official data.</p></div><p>An independent evidence explorer.<br/>Sources: Department of Statistics Malaysia · OpenDOSM</p><Link to="/data">Sources & methodology <ArrowUpRight size={14}/></Link></footer></div>
}
