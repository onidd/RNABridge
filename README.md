# RNABridge

RNABridge is a professional tool for analyzing RNA structural motifs, identifying complex super-helices, and generating rich 2D/3D visualizations. It streamlines the workflow from raw PDB data to a searchable structural database.

## Key Features

- **Centralized Core**: All logic (geometry, stacking, visualization) is powered by the `rnabridge.py` library.
- **Optimized Pipeline**: A high-performance, single-pass analysis script (`analyze.py`) replaces redundant intermediate steps.
- **Automated Configuration**: Centralized `config.py` handles environment variables, database switching (PostgreSQL/SQLite), and automatic X3DNA path detection.
- **Rich Visualizations**: Automatically generates SVG diagrams via VARNA and high-quality PML scripts for PyMOL.
- **API Ready**: Built-in FastAPI server for searching and serving structural data to front-end applications.

## Prerequisites

- **Python 3.12+**
- **Conda** (strongly recommended for PyMOL management)
- **Java** (required for VARNA/cli2rest-bio SVG generation)
- **X3DNA (v2.4)** (should be placed in the `x3dna-v2.4/` directory within the project root)

## Installation

The easiest way to set up RNABridge is using the provided Conda environment file:

```bash
# Create and activate the environment
conda env create -f environment.yml
conda activate rnabridge
```

Alternatively, using `pip` (requires manual PyMOL installation):
```bash
pip install -r requirements.txt
```

## Usage

### 1. Full Pipeline
To run the entire analysis process (downloading, annotation, analysis, and visualization):
```bash
./pipeline.sh
```

### 2. Manual Steps
You can also run individual components:
```bash
# Synchronize local data with RCSB PDB
python fetch_pdb.py

# Analyze a specific RNA structure
python analyze.py json/XXXX.json analyze2/XXXX.json cif/XXXX.cif

# Generate visualizations
python categorize.py

# Update the database
python database.py

# Start the API server
python api.py
```

## API Documentation

Once the API server is running (`python api.py`), you can access the interactive API documentation at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) – interactive playground to test the endpoints.
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) – clean, structured documentation.

## Configuration

All system parameters, including directory paths and geometric thresholds (e.g., `MAX_BEND_ANGLE`), are managed in `config.py`. 

### Production Environment (PostgreSQL)
To use PostgreSQL instead of the default SQLite, set the `DATABASE_URL` environment variable:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/rnabridge"
```

## Project Structure

- `rnabridge.py`: The heart of the system (Classes: Utils, Core, Stacking, Geometry, Visualizer).
- `analyze.py`: Combined motif classification and super-helix building.
- `categorize.py`: Logic for grouping results and triggering 2D/3D exports.
- `api.py`: FastAPI server for data access.
- `config.py`: Centralized settings and environment management.
- `cif/`, `json/`, `analyze/`, `result/`: Automated data storage directories.

## License

This project is intended for research and educational purposes. Ensure compliance with RCSB PDB and X3DNA license agreements.
