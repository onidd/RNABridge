# RNABridge

RNABridge is a professional tool for analyzing RNA structural motifs, identifying complex super-helices, and generating rich 2D/3D visualizations. It streamlines the workflow from raw PDB data to a searchable structural database.

## Key Features

- **Centralized Core**: All logic (geometry, stacking, visualization) is powered by the `rnabridge.py` library.
- **Optimized Pipeline**: High-performance analysis script (`analyze.py`) replaces redundant intermediate steps.
- **Full Stack Solution**: Includes a FastAPI backend and a modern React frontend.
- **Interactive Documentation**: Built-in Swagger UI and ReDoc for API exploration.

---

## Prerequisites

| Tool | Purpose | Note |
| :--- | :--- | :--- |
| **X3DNA (v2.4)** | Helix Analysis | **User must provide manually** in `x3dna-v2.4/` directory |
| **Docker** | Containerization | Required for Option 1 (and for VARNA visualizations) |
| **Node.js** | Frontend | Required for Option 2/3 (Local development) |
| **Python 3.12+** | Backend | Required for Option 2/3 (Local development) |

---

## Installation & Setup

Choose the method that best fits your needs:

### Option 1: Docker (Quick Start - Recommended)
The easiest way to run the entire stack (Backend + Frontend) without installing local dependencies.
1. Place your `x3dna-v2.4` folder in the project root.
2. Run:
```bash
docker-compose up --build
```
Access the application at `http://localhost:8000`.

### Option 2: Conda (Recommended for Developers)
Best if you plan to modify the code or run scripts manually.
1. Create environment: `conda env create -f environment.yml`
2. Activate: `conda activate rnabridge`
3. Install frontend: `cd frontend && npm install`
4. Run: `./pipeline.sh` and then `python api.py`

### Option 3: Manual Pip Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Install frontend: `cd frontend && npm install`
3. Run: `./pipeline.sh` and then `python api.py`

---

## Usage Guide

### 1. Analysis Pipeline
Place your `.cif` files in the `cif/` directory and run:
```bash
./pipeline.sh
```

### 2. API Documentation
Once the server is running (port 8000), access the interactive docs:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Frontend Development
If running locally (Option 2/3), start the dev server:
```bash
cd frontend
npm run dev
```
Accessible at `http://localhost:5173`.

## Configuration

- **Database**: Uses SQLite by default. Set `DATABASE_URL` environment variable for PostgreSQL.
- **X3DNA**: Ensure the distribution is in `x3dna-v2.4/` at the project root.

## Licensing

- **RCSB PDB**: Data is fetched from [RCSB PDB](https://www.rcsb.org/).
- **X3DNA**: Users must obtain their own license from [x3dna.org](http://x3dna.org/).
- **Disclaimer**: This tool is for research. Authors are not responsible for the licensing of third-party tools.
