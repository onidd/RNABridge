# --- STAGE 1: Build Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: Backend & Final Image ---
FROM continuumio/miniconda3
WORKDIR /app

# Install system dependencies for PyMOL, PostgreSQL and basic tools
RUN apt-get update && apt-get install -y \
    libglu1-mesa \
    libgl1 \
    libxrender1 \
    libxcursor1 \
    libxft2 \
    libxinerama1 \
    libxi6 \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy environment file first to leverage Docker cache
COPY environment.yml .

# Create Conda environment
RUN conda env create -f environment.yml && conda clean -afy

# Set environment path so we don't have to use 'conda run'
ENV PATH /opt/conda/envs/rnabridge/bin:$PATH

# Copy the rest of the project
COPY . .

# Copy built frontend from Stage 1 to the 'dist' folder (FastAPI will serve it)
COPY --from=frontend-builder /app/frontend/dist /app/dist

# Expose FastAPI port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
