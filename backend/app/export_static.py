import json
import shutil
from pathlib import Path

from fastapi.encoders import jsonable_encoder

from .analysis.quarterly import DATASET, quarterly_unemployment
from .api.datasets import catalogue, datasets, raw
from .api.overview import overview
from .api.rankings import rankings
from .api.trends import trends
from .data.opendosm import get_dataset_metadata, load_dataset
from .data.registry import REGISTRY
from .data.states import STATES, TERRITORIES


OUTPUT_DIR = Path(__file__).parents[2] / "public" / "static-api"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(jsonable_encoder(value), ensure_ascii=True, separators=(",", ":")),
        encoding="utf-8",
    )


def export() -> None:
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)

    catalogue_data = catalogue()
    dataset_data = datasets()
    states = [*STATES, *TERRITORIES]

    write_json(OUTPUT_DIR / "catalogue.json", catalogue_data)
    write_json(OUTPUT_DIR / "datasets.json", dataset_data)

    for definition in catalogue_data["metrics"]:
        metric = definition["id"]
        ranking_data = {
            "latest": {
                "states": rankings(metric, None, False),
                "all": rankings(metric, None, True),
            },
            "years": {
                str(year): {
                    "states": rankings(metric, year, False),
                    "all": rankings(metric, year, True),
                }
                for year in catalogue_data["years"]
            },
        }
        write_json(OUTPUT_DIR / "rankings" / f"{metric}.json", ranking_data)
        write_json(
            OUTPUT_DIR / "trends" / f"{metric}.json",
            {state: trends(metric, state, 2015) for state in states},
        )

    for state in ["Melaka"]:
        overview_data = {
            "latest": {
                "states": overview(state, "latest", None, False),
                "all": overview(state, "latest", None, True),
            },
            "years": {
                str(year): {
                    "states": overview(state, "same-year", year, False),
                    "all": overview(state, "same-year", year, True),
                }
                for year in catalogue_data["years"]
            },
        }
        write_json(OUTPUT_DIR / "overviews" / f"{state}.json", overview_data)

    quarterly_raw = load_dataset(DATASET)
    quarterly_metadata = get_dataset_metadata(DATASET)
    latest = quarterly_unemployment(
        quarterly_raw, quarterly_metadata, "Melaka", None, False
    )
    quarterly_data = {
        "periods": latest["periods"],
        "source": latest["source"],
        "observations": {
            state: quarterly_unemployment(
                quarterly_raw, quarterly_metadata, state, None, False
            )["observations"]
            for state in states
        },
        "snapshots": {
            period: {
                "states": quarterly_unemployment(
                    quarterly_raw, quarterly_metadata, "Melaka", period, False
                ),
                "all": quarterly_unemployment(
                    quarterly_raw, quarterly_metadata, "Melaka", period, True
                ),
            }
            for period in latest["periods"]
        },
    }
    write_json(OUTPUT_DIR / "quarterly.json", quarterly_data)

    for dataset_id in REGISTRY:
        write_json(
            OUTPUT_DIR / "raw" / f"{dataset_id}.json",
            raw(dataset_id, limit=2**31 - 1, offset=0),
        )


if __name__ == "__main__":
    export()