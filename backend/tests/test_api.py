import polars as pl
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.data.registry import REGISTRY
from app.data.states import STATES,TERRITORIES
from app.api import dependencies

@pytest.fixture
def client(monkeypatch):
    rows=[{'state':state,'year':year,'metric':'poverty','value':float(i+1),'dataset':'hies_state'} for i,state in enumerate(STATES+TERRITORIES) for year in [2022,2024,2025]]
    monkeypatch.setattr(dependencies,'analytical_data',lambda:(pl.DataFrame(rows),[]))
    monkeypatch.setattr(dependencies,'get_dataset_metadata',lambda k:REGISTRY[k])
    return TestClient(app)

def test_health(client):assert client.get('/api/health').json()=={'status':'ok'}
def test_overview(client):
    data=client.get('/api/state/Malacca/overview?mode=same-year&year=2024').json()
    assert data['state']=='Melaka'
    assert all(m['year']==2024 for m in data['metrics'])
    assert next(m for m in data['metrics'] if m['id']=='real_gdp')['value'] is None
    assert client.get('/api/state/Melaka/overview?mode=same-year').status_code==422
    assert client.get('/api/state/Unknown/overview').status_code==422

def test_ranks(client):
    response=client.get('/api/rankings/poverty?year=2024').json()
    assert len(response['states'])==13 and response['comparison_count']==13
    assert len(client.get('/api/rankings/poverty?year=2024&include_federal_territories=true').json()['states'])==16
    assert client.get('/api/rankings/not_real').status_code==404

def test_compare(client):
    response=client.get('/api/compare?metric=poverty&year=2024&states=Melaka,Penang').json()
    assert [m['state'] for m in response['states']]==['Melaka','Pulau Pinang']
    assert all(m['year']==2024 for m in response['states'])
    assert client.get('/api/compare?metric=poverty&states=Melaka,Malacca').status_code==422

def test_trend_no_interpolation(client):
    response=client.get('/api/trends/poverty?state=Melaka').json()
    assert [o['year'] for o in response['observations']]==[2022,2024,2025]

def test_refresh_guard(client,monkeypatch):
    monkeypatch.setenv('DATA_REFRESH_TOKEN','test-secret')
    assert client.post('/api/data/refresh').status_code==403
    assert client.post('/api/data/refresh',headers={'Authorization':'Bearer test-secret'},json={'dataset':'unknown'}).status_code==404
