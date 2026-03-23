# CO2 Pipeline Routing Tool — Project Context

## Project Overview

The CO2 Pipeline Routing Tool (CO2PRT) is a full-stack desktop and web application developed by NETL (National Energy Technology Laboratory) that uses a **Monte Carlo Tree Search (MCTS) machine learning algorithm** to generate optimal CO2 pipeline routes across the contiguous USA and Alaska. Users provide start and end coordinates via an interactive map interface; the ML backend processes these against a geographic cost surface raster, then returns a route as a shapefile and a downloadable PDF report. The tool is distributed both as a packaged **Electron desktop app** (`.exe`) and as a **cloud-hosted web tool** (deployable via Docker to Google Cloud Run).

---

## Tech Stack

- **Frontend:** React 18 (Create React App), React Router v6, MUI v6, React-Leaflet / MapLibre GL / Esri-Leaflet (interactive map), Bootstrap 5, Axios, Electron 31 (desktop shell)
- **Backend:** Python 3.11+, Flask 3.x, Flask-APScheduler (session cleanup), GDAL/OGR/OSR (geospatial transforms), Rasterio, Fiona, Shapely, NumPy, OpenCV, fpdf2 (PDF generation), Gymnasium (RL environment wrappers), PyTorch (dev dependency for model training)
- **ML Core:** Custom Monte Carlo Tree Search implementation (`mc_agent.py`) operating on cost-surface GeoTIFF rasters
- **Storage/Data:** GeoTIFF cost raster (`Flask/raster/cost_10km_aea.tif`), session-scoped file I/O (shapefiles, zips, PDFs in `Flask/sessions/<uid>/`)
- **Tooling:**
  - `uv` for Python dependency management (`pyproject.toml` / `uv.lock`)
  - `npm` / `react-scripts` for frontend build
  - `PyInstaller` for bundling the Flask backend into a standalone `.exe`
  - `electron-builder` for packaging the complete Electron app (NSIS installer)
  - Prettier + Husky + lint-staged for JS formatting
  - Jest + `@testing-library/react` for frontend unit tests
  - Python `unittest` for backend tests
  - Selenium for end-to-end testing

---

## Architecture & Directory Structure

```
CO2-Pipeline-Routing-Tool/
├── src/                        # React frontend source
│   ├── App.js                  # Root React component, map + routing logic
│   ├── components/             # UI components (IdMode, EvalMode, Modals, etc.)
│   ├── App.test.js             # Frontend Jest tests
│   └── index.js                # React entry point
├── public/                     # Static assets + Electron shell
│   └── electron.js             # Electron main process
├── Flask/                      # Python Flask backend (Python package)
│   ├── base.py                 # Flask app factory, ALL API endpoints
│   ├── controller.py           # PipelineController - bridges API ↔ ML
│   ├── mc_agent.py             # MCTS ML engine (CostSurface, Node, MCTree, MCAgent)
│   ├── rout.py                 # Legacy least-cost path implementation
│   ├── line_builder.py         # Shapefile construction from route coordinates
│   ├── report_builder/         # PDF report generation (fpdf2)
│   ├── raster/                 # GeoTIFF cost surface rasters (large, via EDX)
│   ├── sessions/               # Per-session output folders (runtime, git-ignored)
│   ├── cost_surfaces/          # Additional cost surface data
│   ├── config.py               # Flask Config class (secret key, session settings)
│   ├── extra_utils.py          # resource_path() helper (PyInstaller compatibility)
│   └── tests/                  # Backend unit tests
├── CO2PRT.py                   # PyInstaller entry point (starts Flask for .exe build)
├── packCO2PRT.spec             # PyInstaller spec file
├── pyproject.toml              # Python dependencies (managed by uv)
├── package.json                # JS dependencies + npm scripts
├── Dockerfile                  # Docker image for Cloud Run deployment
├── makefile                    # Build convenience targets
├── install_edx_assets.py       # Script to pull large raster assets from EDX
└── documentation/              # Sphinx docs source
```

---

## Key Files & Entry Points

| File | Purpose |
|---|---|
| [`Flask/base.py`](Flask/base.py) | Flask app object (`api`), all REST endpoints (`/token`, `/check`, `/download_report`, `/uploads`, `/gen_uid`, etc.), logging setup (JSON for Cloud Run / plain text for desktop), session management, APScheduler job |
| [`Flask/mc_agent.py`](Flask/mc_agent.py) | The ML core — `CostSurface` (raster processing), `Node` (UCB, expand, backpropagate), `MCTree`, `MCAgent` (parallel MCTS forest), and the top-level `least_cost_path_ml()` entry point |
| [`Flask/controller.py`](Flask/controller.py) | `PipelineController` — thin adapter: converts API inputs into `least_cost_path_ml()` calls |
| [`src/App.js`](src/App.js) | Root React component: map rendering (Leaflet/MapLibre), user input handling, API calls via Axios, result display |
| [`public/electron.js`](public/electron.js) | Electron main process — creates `BrowserWindow`, spawns the Flask `.exe` subprocess, handles app lifecycle |

---

## Setup & Execution

### 1. Install Large Raster Assets (EDX members only)
```bash
python install_edx_assets.py --api-key <edx_api_key>
```

### 2. Backend (Python / Flask)
```bash
# Install Python dependencies
uv sync --locked

# Activate virtual environment
source .venv/bin/activate          # Linux/Mac
# OR
source .venv/Scripts/activate      # Windows

# Create Flask secret key
python -c 'import secrets; print(secrets.token_urlsafe(32))'
# → Add SECRET_KEY=<result> to Flask/.env

# Run Flask dev server (from Flask/ directory)
cd Flask
flask --app base.py run
```

### 3. Frontend (React / Node)
```bash
# Install JS dependencies (from project root)
npm install --legacy-peer-deps

# Start React dev server
npm start
```

### 4. Desktop Electron App (development)
```bash
npm run electron:start    # Launches Electron + React concurrently
```

### 5. Package for Distribution
```bash
# Bundle Flask backend → dist/CO2PRT_Flask.exe
python -m PyInstaller packCO2PRT.spec

# Build React + package Electron installer (Windows NSIS)
npm run electron:package:win
```

### 6. Docker / Cloud Run
```bash
docker build -t co2prt .
docker run -p 5000:5000 co2prt
```

---

## Core Conventions

- **Dual-mode awareness:** The app explicitly branches on `getattr(sys, 'frozen', False)` throughout to distinguish PyInstaller-bundled (desktop `.exe`) mode from development/Cloud Run mode. `resource_path()` in `extra_utils.py` abstracts asset path resolution for both modes.
- **Session isolation:** Each browser session gets a UUID (`/gen_uid` endpoint, stored in Flask `session`). All output files are written to `Flask/sessions/<uid>/` and cleaned up on window close or by a 24-hour APScheduler job.
- **Async ML execution:** The routing ML job is submitted to a `ThreadPoolExecutor`. The frontend polls `/check` until the zip output file appears, then fetches the result — decoupling the long-running ML computation from the HTTP request cycle.
- **Coordinate system pipeline:** User inputs are WGS84 (lat/lon) → converted to North America Albers Equal Area Conic (ESRI:102008) for ML raster indexing → result translated back to WGS84 for map display.
- **Structured logging:** In Cloud Run mode, logs are emitted as structured JSON with GCP trace IDs. In desktop mode, human-readable text format is used. Both handled via `TraceFilter` and `JsonFormatter` classes in `base.py`.
- **RESTful API:** Flask endpoints follow REST conventions. The frontend proxies all API calls to `http://127.0.0.1:5000/` (configured in `package.json`).
- **Code formatting:** Prettier is enforced on staged JS/JSX/CSS/MD files via Husky pre-commit hooks.
