import polars as pl
from .catalogue import DEFINITIONS
from .rankings import rank_states
from .household import changes
from ..data.states import universe

def ordinal(n):
    return f'{n}'+('th' if 10<=n%100<=20 else {1:'st',2:'nd',3:'rd'}.get(n%10,'th'))

class Engine:
    def __init__(self,observations,metadata): self.df=observations; self.metadata=metadata
    def source(self,dataset,definition):
        meta=self.metadata[dataset]
        return {'provider':meta['provider'],'dataset':dataset,'title':meta['title'],'url':meta['source_url'],'retrieved_at':meta.get('retrieved_at'),'sha256':meta.get('sha256'),'calculated':definition.calculation is not None,'calculation':definition.calculation,'note':meta.get('note')}
    def latest_year(self,metric,state=None):
        df=self.df.filter(pl.col('metric')==metric)
        if state: df=df.filter(pl.col('state')==state)
        return df['year'].max()
    def metric(self,metric,state,year=None,include=False):
        definition=DEFINITIONS[metric]
        target=year if year is not None else self.latest_year(metric,state)
        series=self.df.filter((pl.col('metric')==metric)&(pl.col('state')==state))
        current=series.filter(pl.col('year')==target).to_dicts() if target is not None else []
        ranks=rank_states(self.df,metric,target,definition.direction,include) if target is not None else None
        rankrows=ranks.filter(pl.col('state')==state).to_dicts() if ranks is not None else []
        count=ranks.height if ranks is not None else 0
        rank=rankrows[0]['rank'] if rankrows else None
        row=current[0] if current else None
        value=row['value'] if row else None
        earlier=series.filter(pl.col('year')<target).sort('year',descending=True).head(1).to_dicts() if target is not None and row else []
        previous={'year':earlier[0]['year'],'value':earlier[0]['value']} if earlier else None
        rank_label=f"{ordinal(rank)}{'-lowest' if definition.direction=='ascending' else '-highest'} of {count} {'states and territories' if include else 'states'}" if rank else None
        return {'id':metric,'label':definition.label,'state':state,'value':value,'unit':definition.unit,'year':target,'rank':rank,'comparison_count':count,'eligible_count':len(universe(include)),'ranking_direction':definition.direction,'rank_label':rank_label,'previous':previous,'change':changes(value,previous['value'],definition.unit) if previous else None,'source':self.source(row['dataset'] if row else definition.dataset,definition),'status':'available' if row else 'unavailable'}
    def overview(self,state,mode,year,include):
        metrics=[self.metric(key,state,year if mode=='same-year' else None,include) for key in DEFINITIONS]
        return {'state':state,'mode':mode,'year':year if mode=='same-year' else None,'mixed_years':len({m['year'] for m in metrics if m['value'] is not None})>1,'include_federal_territories':include,'metrics':metrics}
    def rankings(self,metric,year,include):
        target=year if year is not None else self.latest_year(metric)
        rows=[self.metric(metric,state,target,include) for state in universe(include)]
        rows.sort(key=lambda r:(r['rank'] is None,r['rank'] or 0,r['state']))
        return {'metric':metric,'year':target,'comparison_count':sum(r['value'] is not None for r in rows),'eligible_count':len(rows),'missing_states':[r['state'] for r in rows if r['value'] is None],'states':rows}
    def trend(self,metric,state,start_year=2015):
        definition=DEFINITIONS[metric]
        df=self.df.filter((pl.col('metric')==metric)&(pl.col('state')==state)&(pl.col('year')>=start_year)).sort('year')
        return {'metric':metric,'label':definition.label,'unit':definition.unit,'state':state,'observations':[{'year':r['year'],'value':r['value'],'source':self.source(r['dataset'],definition)} for r in df.to_dicts()],'annotation':{'date':'2023-03-31','source_url':'https://www.melaka.gov.my/kerajaan/pentadbiran-kerajaan-negeri/ketua-menteri-melaka.html','label':'Ab Rauf Yusoh became Chief Minister','note':'Context only; chronology does not establish causality.'}}
