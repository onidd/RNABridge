# RNABridge

RNABridge is a professional tool for analyzing RNA structural motifs, identifying complex super-helices, and generating rich 2D/3D visualizations. It streamlines the workflow from raw PDB data to a searchable structural database.

## Key Features

- **Centralized Core**: All logic (geometry, stacking, visualization) is powered by the `rnabridge.py` library.
- **Optimized Pipeline**: A high-performance, single-pass analysis script (`analyze.py`) replaces redundant intermediate steps.
- **Automated Configuration**: Centralized `config.py` handles environment variables and automatic database switching (PostgreSQL/SQLite).
- **Rich Visualizations**: Automatically generates SVG diagrams and high-quality PML scripts for PyMOL.
- **API Ready**: Built-in FastAPI server with Swagger UI and ReDoc documentation.
- **Frontend Included**: Modern React frontend for data exploration.

## Prerequisites

| Tool | Purpose | Note |
| :--- | :--- | :--- |
| **Python 3.12+** | Main Logic | Required |
| **X3DNA (v2.4)** | Helix Analysis | **User must provide manually** in `x3dna-v2.4/` directory |
| **Node.js** | Frontend | Required to build and run the web interface |
| **PyMOL** | 3D Processing | Recommended (installed via Conda or system) |
| **Java** | Visualizations | Required for VARNA/cli2rest-bio SVG generation |

## Installation Methods

You can set up RNABridge using one of the following three methods, depending on your environment and needs.

### Method A: Quick Start with Docker (Recommended)
This is the easiest way to run the full stack (Backend, Frontend, and PostgreSQL) in a single command.

1. **Prerequisites**: [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/).
2. **Setup**: Place your X3DNA distribution in `x3dna-v2.4/`.
3. **Launch**:
   ```bash
   docker-compose up --build
   ```
4. **Access**: Web Interface at `http://localhost:8000`.

---

### Method B: Conda Environment (Scientific Dev)
Recommended if you want to run the pipeline locally and use PyMOL without worrying about system dependencies.

1. **Setup**:
   ```bash
   conda env create -f environment.yml
   conda activate rnabridge
   ```
2. **Frontend**:
   ```bash
   cd frontend && npm install && npm run build
   ```
3. **Launch**: `python api.py`

---

### Method C: Pip + Manual Setup (Advanced)
For users who prefer a standard Python environment and manual database management.

1. **Setup**:
   ```bash
   pip install -r requirements.txt
   # Ensure PyMOL and Java are installed on your system
   ```
2. **Database**: The system defaults to **SQLite** (`rnabridge.db`). To use PostgreSQL, set the `DATABASE_URL` environment variable.
3. **Launch**: `uvicorn api:app --host 0.0.0.0 --port 8000`

---

## Usage

### 1. Run Analysis Pipeline
Place your `.cif` files in the `cif/` directory.

**Using Docker**:
```bash
docker-compose exec app bash pipeline.sh
```

**Using Local Python**:
```bash
chmod +x pipeline.sh
./pipeline.sh
```

### 3. External Tools
Place the X3DNA distribution in the root directory:
```text
RNABridge/
├── x3dna-v2.4/  <-- Place X3DNA here
├── analyze.py
└── ...
```

## Usage

### 1. Run Analysis Pipeline
Place your `.cif` files in the `cif/` directory and run:
```bash
chmod +x pipeline.sh
./pipeline.sh
```

### 2. Start the API Server
```bash
python api.py
```
Once the server is running, you can access the interactive API documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Launch Web Interface
```bash
cd frontend
npm run dev
```
The interface will be available at `http://localhost:5173`.

## Database Configuration

The system uses **SQLite** by default. It automatically switches to **PostgreSQL** if the `DATABASE_URL` environment variable is detected:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/rnabridge"
```

## Data Sources & Licensing

- **RCSB PDB**: Data is fetched from [RCSB PDB](https://www.rcsb.org/).
- **X3DNA**: Users must obtain their own license from [x3dna.org](http://x3dna.org/).
- **Disclaimer**: This tool is for research. Authors are not responsible for the licensing of third-party tools.
