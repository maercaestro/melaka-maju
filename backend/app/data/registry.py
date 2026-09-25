from pathlib import Path
import yaml
CONFIG = yaml.safe_load((Path(__file__).parents[1] / 'config/datasets.yaml').read_text())
REGISTRY = {key: {'id': key, 'provider': 'DOSM', 'format': 'parquet', 'source_url': f'https://open.dosm.gov.my/data-catalogue/{key}', **value} for key, value in CONFIG['datasets'].items()}
def dataset_info(dataset):
    if dataset not in REGISTRY:
        raise KeyError(f'Unknown dataset: {dataset}')
    return REGISTRY[dataset]
