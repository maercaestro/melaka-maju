"""Run with: python -m app.data.refresh"""
from .registry import REGISTRY
from .opendosm import refresh_dataset
if __name__ == '__main__':
    for dataset in REGISTRY:
        metadata=refresh_dataset(dataset)
        print(dataset,metadata['rows'],metadata['max_year'],flush=True)
