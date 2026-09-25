import { useQuery } from '@tanstack/react-query'
import { get, query } from '../api/client'
import type { QuarterlyUnemployment, Catalogue, Comparison, DatasetList, Overview, Rankings, RawData, Selection, Trend } from '../types/api'
export const useHealth = () => useQuery({queryKey:['health'],queryFn:()=>get<{status:string}>('/health'),retry:1})
export const useCatalogue = () => useQuery({queryKey:['catalogue'],queryFn:()=>get<Catalogue>('/catalogue')})
export const useDatasets = () => useQuery({queryKey:['datasets'],queryFn:()=>get<DatasetList>('/datasets')})
export const useStateOverview = (state: string, s: Selection) => useQuery({queryKey:['overview',state,s],queryFn:()=>get<Overview>(`/state/${encodeURIComponent(state)}/overview${query({mode:s.mode,year:s.mode==='same-year'?s.year:undefined,include_federal_territories:s.include})}`)})
export const useRankings = (metric: string, year: number | undefined, include: boolean) => useQuery({queryKey:['rankings',metric,year,include],queryFn:()=>get<Rankings>(`/rankings/${metric}${query({year,include_federal_territories:include})}`)})
export const useTrend = (metric: string, state: string) => useQuery({queryKey:['trend',metric,state],queryFn:()=>get<Trend>(`/trends/${metric}${query({state})}`),enabled:!!state})
export const useComparison = (metric: string, states: string[], s: Selection) => useQuery({queryKey:['compare',metric,states,s],queryFn:()=>get<Comparison>(`/compare${query({metric,states:states.join(','),mode:s.mode,year:s.mode==='same-year'?s.year:undefined,include_federal_territories:s.include})}`),enabled:states.length>0})
export const useRawData = (dataset: string, params: Record<string,string|number>) => useQuery({queryKey:['raw',dataset,params],queryFn:()=>get<RawData>(`/datasets/${dataset}/raw${query(params)}`),enabled:!!dataset})

export const useQuarterlyUnemployment = (state: string, period: string, include: boolean) => useQuery({queryKey:['quarterly-unemployment',state,period,include],queryFn:()=>get<QuarterlyUnemployment>(`/labour/unemployment-quarterly${query({state,period,include_federal_territories:include})}`)})
