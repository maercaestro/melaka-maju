# Melaka Maju

Understanding Melaka through official data. A transparent evidence explorer for economic output, household welfare and labour-market indicators. Built on the existing Vite/React/TypeScript scaffold, with Tailwind, TanStack Query, Recharts and FastAPI. No AI services, accounts or database server.

## Local setup

Use Node.js 22.12+ and Python 3.14 (the pinned environment verified for this project).

```sh
npm install
npm run dev
```

In another terminal:

```sh
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.data.refresh
uvicorn app.main:app --reload --port 8000
```

Open the Vite URL (normally http://localhost:5173). The initial overview is **Same Year → 2024**, comparing the 13 states. The navigation shows the result of `/api/health`. Vite proxies `/api` to FastAPI. The first analytical request also downloads missing sources; the explicit refresh command is recommended so progress is visible.

Environment variables are read from the process environment. Vite automatically reads a root `.env.local`; the Python process does not automatically load `.env` (export variables before starting it).

| Variable | Purpose |
|---|---|
| `VITE_API_URL` | Optional local override, e.g. `http://localhost:8000`; required production backend origin. Empty uses the same-origin Vite proxy. |
| `FRONTEND_ORIGIN` | Comma-separated allowed frontend origins. Default `http://localhost:5173`. Production: `https://melaka-maju.vercel.app`. |
| `DATA_CACHE_DIR` | Absolute cache directory; defaults to `backend/data/raw`. Use persistent storage in production. |
| `DATA_REFRESH_TOKEN` | Optional bearer token for refresh. Set on public deployments to restrict this expensive operation. |

## Architecture

React requests completed results, formats values, renders charts and manages selections. Python owns year selection, state normalization, validation, rankings, growth, shares and changes. Chart alignment in React only places returned observations on a common axis.

- `backend/app/data/`: the only external-data access layer, curated registry, cache, workbook adapters and provenance.
- `backend/app/analysis/`: deterministic Polars transformations and ranking engine. No HTTP calls.
- `backend/app/api/`: API routes; Pydantic metric, ranking and trend response models.
- `src/api/` and `src/hooks/`: configurable API client and TanStack Query hooks.
- `src/pages/`: overview, rankings, trends, comparison and raw data.
- `reports/verification.md` and `.json`: generated results, sources, retrieval timestamps and hashes.

Parquet files and source XLSX workbooks are cached on disk; metadata includes SHA-256, retrieval time and observed years. Source rows are validated before replacing the cache. Failed downloads preserve the last cached file. Ordinary requests do not redownload existing files. Derived frames are memoized until refresh or process restart. Run one Uvicorn worker: cache locking and memoization are process-local. DuckDB and PyArrow are installed for future multi-file queries; current small transformations use Polars directly.

## Sources

The exact URLs and caveats are in `backend/app/config/datasets.yaml`.

| Source | Use |
|---|---|
| [gdp_state_real_supply](https://open.dosm.gov.my/data-catalogue/gdp_state_real_supply) | Real GDP at constant 2015 prices; calculated annual growth and sector shares |
| [hies_state](https://open.dosm.gov.my/data-catalogue/hies_state) | Household income, expenditure, Gini and poverty |
| [hh_income_state](https://open.dosm.gov.my/data-catalogue/hh_income_state) | Historical household survey income |
| [hh_inequality_state](https://open.dosm.gov.my/data-catalogue/hh_inequality_state) | Historical Gini |
| [lfs_state_sex](https://open.dosm.gov.my/data-catalogue/lfs_state_sex) | Annual unemployment, participation and employment; both sexes |
| [population_state](https://open.dosm.gov.my/data-catalogue/population_state) | Population; both sexes, all ages, all ethnicities |
| [DOSM GDP workbook, document 19977](https://www.dosm.gov.my/portal-main/release-document-log?release_document_id=19977) | Published nominal GDP per capita, Table A23 |
| [DOSM productivity workbook, document 18690](https://www.dosm.gov.my/portal-main/release-document-log?release_document_id=18690) | Published state value added per employed person, Table 1 |

`dosm_publication_19977` and `dosm_publication_18690` are explicitly **local registry keys for official publication documents**, not invented OpenDOSM dataset IDs. Workbook sheet/cell coordinates and year flags are preserved in extracted rows. The raw-data page links to the original workbook. The registered workbooks are fixed publication vintages; adding future releases requires a registry/adapter review, while latest observation years always come from the source contents. Parquet retrieval falls back to paginated data.gov.my API retrieval for catalogue sources; XLSX sources do not have an API fallback.

Land area and population-density official publications are recorded under `discovery` in the registry. Complete comparable state-level land-area extraction, density and output per km² remain **Phase 2**. Constituency or district densities are not used as state densities.

## Methodology and limits

- Rankings default to the 13 states; optional Federal Territories exclude the Malaysia aggregate and Supranational output. The denominator is the count with an observation; eligible count and missing states are separate. Ties use competition ranks (1, 1, 3).
- Latest Available means latest within the registered **annual/survey** sources. Each metric keeps its year; mixed years are explicitly flagged. Comparison rows use a single shared year per metric. Same Year never substitutes another year, even if every state is unavailable.
- Source coverage at this verification: GDP through 2025, HIES through 2024, annual labour-force data through 2023, productivity through 2024. These are documentation observations, not application constants. Quarterly labour data are not silently substituted for annual data.
- Real GDP growth is calculated only when the immediately previous calendar year exists. It may differ slightly from the source's rounded published growth. Sector shares use total GDP at purchasers' prices; import duties and rounding mean displayed sectors need not sum to 100%.
- GDP per capita is nominal RM/person, while real GDP is at constant 2015 prices. The current GDP per-capita workbook supplies 2023–2025 only; earlier years are unavailable in that registered source.
- Household income/expenditure are nominal monthly household measures. No inflation adjustment is implied. HIES wins overlapping observations; historical income/Gini sources extend the series. Modelled 2020 income estimates are excluded so survey trends use actual survey observations. There is no interpolation.
- Income changes are changes since the previous survey, not annualised growth. Percentage-rate changes use percentage points. Gini changes use coefficient units. Previous observations are explicitly dated and can precede the selected same-year snapshot.
- Productivity uses DOSM's published series, not a GDP/LFS employment shortcut. Kuala Lumpur productivity includes Putrajaya; no separate Putrajaya estimate is invented. GDP territorial coverage can differ across vintages.
- GDP is not household income. Changes in poverty methodology and source revisions can affect historical comparisons. Ranks are descriptive, not statements of overall quality.
- The optional 31 March 2023 government-transition marker is context only. Annual observations cannot identify within-year policy effects. No causality is inferred.
- Cached-source overlap discrepancies are available at `/api/data/audit` and in the verification JSON. No numbers from the project brief are inputs. Source changes supersede example claims.
- Source availability errors return HTTP 503 rather than fabricated values. A missing observation in valid data returns `null`. The raw page exports the **current filtered page**, up to 100 rows in the UI; API pagination supports up to 1,000.

## API

Interactive schemas: http://localhost:8000/docs

```text
GET  /api/health
GET  /api/catalogue
GET  /api/state/Melaka/overview?mode=same-year&year=2024
GET  /api/rankings/median_household_income?year=2024&include_federal_territories=false
GET  /api/trends/gini?state=Melaka&start_year=2015
GET  /api/compare?metric=gdp_per_capita&year=2024&states=Melaka,Johor
GET  /api/datasets
GET  /api/datasets/hies_state/raw?state=Melaka&year=2024&limit=100&offset=0
GET  /api/data/audit
POST /api/data/refresh
```

Refresh accepts optional JSON `{"dataset":"hies_state"}`; omitted means all registered sources. When configured, send `Authorization: Bearer <DATA_REFRESH_TOKEN>`. Each source returns success/failure; successfully refreshed sources become available immediately. Refresh may take a while and should be run as a controlled operation. For scheduling, use `python -m app.data.refresh` and restart the API to invalidate its in-memory view.

## Verification

```sh
npm run build
npm run lint
cd backend
python -m pytest -q
python -m app.verify
```

The report generator writes four requested outputs: Melaka latest, Melaka 2024, all 13 states' 2024 rankings for all implemented metrics, and Melaka trends from 2015 where available. JSON preserves full precision; Markdown rounds only for readability. Tests use synthetic fixtures, not hardcoded economic values in application logic.

## Deployment

Frontend: import this repository into Vercel. Build `npm run build`, output `dist`, set `VITE_API_URL` to the deployed backend origin (without `/api`). `vercel.json` enables SPA routes. Rebuild after changing the frontend environment.

Backend: deploy `backend/Dockerfile` on Render or Railway, with the service root set to `backend`. Set `FRONTEND_ORIGIN=https://melaka-maju.vercel.app`, `DATA_CACHE_DIR=/data/raw`, and a `DATA_REFRESH_TOKEN`. Attach a persistent disk at `/data`; expose the platform's `PORT` (Docker command handles it). Health check: `/api/health`. Populate data with the refresh command or authorized endpoint. The health endpoint checks process/connectivity; analytical endpoints require the datasets to be available. Use one worker for consistent cache invalidation. The Vite development proxy is not a production backend.

No deployment is performed by the local build. Phase 1 contains no authentication/accounts, LLM, chatbot, MCP, RAG, embeddings, forecasts or political scoring.

Browser acceptance tests (start both servers first):

```sh
npx playwright install chromium
TEST_BASE_URL=http://localhost:5173 npx playwright test
```

The browser tests cover mode switching, 13/16-state rankings, charts, comparison, raw-data filtering, CSV download and mobile layout. Screenshots are saved in `reports/desktop.png` and `reports/mobile.png`.

## Quarterly unemployment

Open `/unemployment` for the dedicated quarterly view using the official [`lfs_qtr_state`](https://open.dosm.gov.my/data-catalogue/lfs_qtr_state) dataset. It includes a latest-quarter snapshot, exact quarter selection, state selection, 13-state/16-area rankings, percentage-point changes and all available quarterly observations. Latest quarter is read from the downloaded data; no observation year or rate is hardcoded.

`GET /api/labour/unemployment-quarterly?state=Melaka&period=2024-Q4&include_federal_territories=false`

Omitting `period` selects the latest source quarter. An unavailable quarter returns null, never another quarter. Previous observations carry their exact quarter labels. The annual dashboard remains annual; Q4 is not substituted for an annual rate, and quarterly rates are not averaged into an annual estimate. The quarterly source is also available in Raw data and the existing refresh endpoint. Its download is independent of annual-dashboard loading.
