import polars as pl
from ..data.states import universe

def rank_states(df, metric, year, ranking_direction='descending', include_federal_territories=False):
    """Competition ranks (1,1,3). Denominator counts observed eligible states."""
    if ranking_direction not in ('ascending','descending'): raise ValueError('Invalid ranking direction')
    selected=df.filter((pl.col('metric')==metric)&(pl.col('year')==year)&pl.col('state').is_in(universe(include_federal_territories)))
    if selected.select('state').is_duplicated().any(): raise ValueError('Duplicate state/year/metric observations')
    selected=selected.filter(pl.col('value').is_not_null())
    count=selected.height
    return selected.with_columns(pl.col('value').rank(method='min',descending=ranking_direction=='descending').cast(pl.Int32).alias('rank'),pl.lit(count).alias('comparison_count')).sort('rank','state')
