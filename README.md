# RNABridge

RNABridge is a professional tool for analyzing RNA structural motifs, identifying complex super-helices, and generating rich 2D/3D visualizations. It streamlines the workflow from raw PDB data to a searchable structural database.

## Key Features

- **Centralized Core**: All logic (geometry, stacking, visualization) is powered by the `rnabridge.py` library.
- **Optimized Pipeline**: A high-performance, single-pass analysis script (`analyze.py`) replaces redundant intermediate steps.
- **Automated Configuration**: Centralized `config.py` handles environment variables and automatic database switching (PostgreSQL/SQLite).
- **Rich Visualizations**: Automatically generates SVG diagrams and high-quality PML scripts for PyMOL.
- **Full Stack Solution**: Includes a FastAPI backend and a modern React frontend for data exploration.

## Requirements

| Tool | Purpose | Note |
| :--- | :--- | :--- |
| **Python 3.12+** | Main Logic | Required |
| **X3DNA (v2.4)** | Helix Analysis | **User must provide manually** in `x3dna-v2.4/` directory |
| **Docker** | Visualizations | Required for `cli2rest-bio` (VARNA) |
| **Node.js** | Frontend | Required to run the web interface |
| **PyMOL** | 3D Processing | Recommended (installed via Conda or system) |

## Installation

### 1. Backend Setup
The easiest way to set up the backend is using Conda:
```bash
# Create and activate the environment
conda env create -f environment.yml
conda activate rnabridge
```
Alternatively, use pip: `pip install -r requirements.txt`

### 2. Frontend Setup
```bash
cd frontend
npm install
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

- **RCSB PDB**: Structural data is fetched from the [RCSB Protein Data Bank](https://www.rcsb.org/). Use of this data must comply with their terms.
- **X3DNA**: This project requires X3DNA for geometric calculations. Users are responsible for obtaining a valid license from [x3dna.org](http://x3dna.org/) before use.
- **Disclaimer**: This tool is for research and educational purposes. The authors are not responsible for the licensing of third-party tools required to run the software.
