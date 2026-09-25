import polars as pl
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.analysis.quarterly import quarterly_unemployment
from app.data.registry import REGISTRY
from app.data.states import STATES, TERRITORIES
from app.api import labour

@pytest.fixture
def raw():
    return pl.DataFrame([
        {'state': state, 'date': date, 'u_rate': float(index + adjustment)}
        for index, state in enumerate(STATES + TERRITORIES)
        for date, adjustment in [('2024-10-01', 2), ('2025-01-01', 3), ('2025-04-01', 4)]
    ])

def test_latest_and_previous_quarter(raw):
    result = quarterly_unemployment(raw, REGISTRY['lfs_qtr_state'])
    assert result['period'] == '2025-Q2'
    assert result['metric']['previous']['period'] == '2025-Q1'
    assert result['metric']['change']['absolute'] == 1
    assert result['metric']['change']['unit'] == 'percentage points'
    assert len(result['states']) == 13
    assert result['states'][0]['state'] == 'Johor'
    assert len(result['observations']) == 3  # Multiple quarters in one year survive.

def test_exact_quarter_missing_and_territories(raw):
    result = quarterly_unemployment(raw, REGISTRY['lfs_qtr_state'], period='2024-Q4', include=True)
    assert len(result['states']) == 16
    assert {r['period'] for r in result['states']} == {'2024-Q4'}
    missing = quarterly_unemployment(raw, REGISTRY['lfs_qtr_state'], period='2024-Q3')
    assert missing['metric']['value'] is None
    assert missing['comparison_count'] == 0
    assert all(r['value'] is None for r in missing['states'])

def test_duplicate_quarter_rejected(raw):
    with pytest.raises(ValueError, match='Duplicate'):
        quarterly_unemployment(pl.concat([raw, raw.head(1)]), REGISTRY['lfs_qtr_state'])

def test_api_period_validation(raw, monkeypatch):
    monkeypatch.setattr(labour, 'load_dataset', lambda _: raw)
    monkeypatch.setattr(labour, 'get_dataset_metadata', lambda _: REGISTRY['lfs_qtr_state'])
    client = TestClient(app)
    assert client.get('/api/labour/unemployment-quarterly?period=2024-Q4').json()['period'] == '2024-Q4'
    assert client.get('/api/labour/unemployment-quarterly?period=2024-Q5').status_code == 422
    assert client.get('/api/labour/unemployment-quarterly?state=Malacca').json()['state'] == 'Melaka'
