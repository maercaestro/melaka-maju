import os
from pathlib import Path
from threading import RLock
LOCK = RLock()
def cache_dir():
    path = Path(os.getenv('DATA_CACHE_DIR', Path(__file__).parents[2] / 'data/raw')).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path
