import hashlib
import json
from datetime import datetime, timezone
from io import BytesIO
import httpx
import polars as pl
from .cache import cache_dir, LOCK
from .registry import dataset_info
from .publications import parse_workbook
from .states import normalize_state, STATES, TERRITORIES

class DataUnavailable(RuntimeError): pass

def validate_source(df):
    if 'state' not in df.columns or 'date' not in df.columns: raise ValueError('Source missing state/date')
    if df['state'].null_count() or df['date'].null_count(): raise ValueError('Missing state/date')
    states={normalize_state(x) for x in df['state'].unique()}
    if states - set(STATES+TERRITORIES+['Malaysia','Supranational']): raise ValueError(f'Unexpected states: {states}')
    years=df['date'].cast(pl.String).str.slice(0,4).cast(pl.Int32)
    if years.null_count(): raise ValueError('Invalid year')
    if df.is_duplicated().any(): raise ValueError('Duplicate source rows')
    dimensions=[c for c in ('state','date','sector','series','sex','age','ethnicity') if c in df.columns]
    if df.select(dimensions).is_duplicated().any(): raise ValueError('Duplicate source dimension observations')
    for column,maximum in [('gini',1),('poverty',100),('u_rate',100),('p_rate',100)]:
        if column in df.columns:
            values=df[column].drop_nulls()
            if ((values<0)|(values>maximum)).any(): raise ValueError(f'Out-of-range {column}')
    for column,dtype in df.schema.items():
        if dtype.is_float() and df[column].drop_nulls().is_finite().not_().any(): raise ValueError(f'Non-finite {column}')
    return years

def _api_download(dataset, client):
    rows=[]; offset=0; size=1000
    while True:
        response=client.get('https://api.data.gov.my/data-catalogue',params={'id':dataset,'limit':size,'offset':offset});response.raise_for_status()
        page=response.json()
        if not isinstance(page,list): raise ValueError('Unexpected catalogue response')
        rows.extend(page)
        if len(page)<size: break
        offset+=size
    return pl.DataFrame(rows)

def download_dataset(dataset):
    info=dataset_info(dataset)
    with LOCK, httpx.Client(timeout=120,follow_redirects=True) as client:
        try:
            response=client.get(info['url']);response.raise_for_status();content=response.content
            df=parse_workbook(content,info['adapter']) if info['format']=='xlsx' else pl.read_parquet(BytesIO(content))
            transport=info['format']
        except httpx.HTTPError:
            if info['format']=='xlsx': raise
            df=_api_download(dataset,client);content=None;transport='api'
        years=validate_source(df)
        path=cache_dir()/f'{dataset}.parquet'
        temp=path.with_suffix('.tmp.parquet');df.write_parquet(temp)
        meta={**info,'dataset':dataset,'retrieved_at':datetime.now(timezone.utc).isoformat(),'max_year':years.max(),'years':sorted(years.unique().to_list(),reverse=True),'rows':df.height,'transport':transport,'sha256':hashlib.sha256(content if content else temp.read_bytes()).hexdigest()}
        if content and info['format']=='xlsx': (cache_dir()/f'{dataset}.xlsx').write_bytes(content)
        temp.replace(path)
        meta_path=cache_dir()/f'{dataset}.meta.json';tmp_meta=meta_path.with_suffix('.tmp');tmp_meta.write_text(json.dumps(meta,indent=2));tmp_meta.replace(meta_path)
        return df

def load_dataset(dataset):
    dataset_info(dataset)
    with LOCK:
        path=cache_dir()/f'{dataset}.parquet'
        try:
            return pl.read_parquet(path) if path.exists() else download_dataset(dataset)
        except (httpx.HTTPError, ValueError, pl.exceptions.PolarsError) as exc:
            raise DataUnavailable(f'{dataset}: {exc}') from exc

def get_dataset_metadata(dataset):
    info=dataset_info(dataset); path=cache_dir()/f'{dataset}.meta.json'
    return {**info,**(json.loads(path.read_text()) if path.exists() else {} )}

def refresh_dataset(dataset):
    try: download_dataset(dataset)
    except (httpx.HTTPError, ValueError, pl.exceptions.PolarsError) as exc: raise DataUnavailable(f'{dataset}: {exc}') from exc
    return get_dataset_metadata(dataset)
