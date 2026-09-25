"""Quarterly unemployment, kept separate from annual observation frames."""
import polars as pl
from .rankings import rank_states
from .household import changes
from .engine import Engine, ordinal
from .catalogue import DEFINITIONS
from ..data.states import normalize_state, universe

DATASET = 'lfs_qtr_state'

def quarterly_unemployment(raw, metadata, state='Melaka', period=None, include=False):
    df = raw.with_columns(
        pl.col('date').cast(pl.String).str.slice(0, 10).str.to_date().alias('date'),
        pl.col('state').replace({s: normalize_state(s) for s in raw['state'].unique()})
    ).with_columns(
        pl.col('date').dt.year().alias('year'),
        pl.col('date').dt.quarter().alias('quarter'),
        pl.col('u_rate').cast(pl.Float64).alias('value'),
        pl.lit('unemployment').alias('metric')
    ).with_columns(
        (pl.col('year').cast(pl.String) + '-Q' + pl.col('quarter').cast(pl.String)).alias('period')
    )
    if df.select('state', 'period').is_duplicated().any():
        raise ValueError('Duplicate state/quarter observations')
    values = df['value'].drop_nulls()
    if (~values.is_finite() | (values < 0) | (values > 100)).any():
        raise ValueError('Invalid quarterly unemployment rate')
    periods = df['period'].unique().sort(descending=True).to_list()
    target = period or (periods[0] if periods else None)
    selected = df.filter(pl.col('period') == target)
    year = int(target[:4]) if target else None
    quarter = int(target[-1]) if target else None
    ranked = rank_states(selected, 'unemployment', year, 'ascending', include)
    ranks = {r['state']: r['rank'] for r in ranked.to_dicts()}
    source = Engine(df, {DATASET: metadata}).source(DATASET, DEFINITIONS['unemployment'])

    def observation(row):
        return {key: row[key] for key in ('year', 'quarter', 'period', 'value')}

    def snapshot(name):
        current = selected.filter(pl.col('state') == name).to_dicts()
        value = current[0]['value'] if current else None
        previous_rows = df.filter((pl.col('state') == name) & (pl.col('period') < target) & pl.col('value').is_not_null()).sort('date').tail(1).to_dicts() if target and value is not None else []
        previous = observation(previous_rows[0]) if previous_rows else None
        rank = ranks.get(name)
        return {'state': name, 'year': year, 'quarter': quarter, 'period': target,
                'value': value, 'rank': rank, 'comparison_count': ranked.height,
                'rank_label': f"{ordinal(rank)}-lowest of {ranked.height} {'states and territories' if include else 'states'}" if rank else None,
                'previous': previous, 'change': changes(value, previous['value'], '%') if previous else None}

    states = sorted([snapshot(s) for s in universe(include)], key=lambda r: (r['rank'] is None, r['rank'] or 0, r['state']))
    observations = [observation(r) for r in df.filter((pl.col('state') == state) & pl.col('value').is_not_null()).sort('date').to_dicts()]
    return {'state': state, 'frequency': 'quarterly', 'unit': '%', 'period': target,
            'periods': periods, 'metric': snapshot(state), 'states': states,
            'eligible_count': len(universe(include)), 'comparison_count': ranked.height,
            'observations': observations, 'source': source}
