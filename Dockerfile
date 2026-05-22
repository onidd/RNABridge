# --- STAGE 1: Build Frontend ---
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- STAGE 2: Build Backend & Final Image ---
FROM python:3.12-slim
WORKDIR /app

# Install system dependencies (including Docker CLI for VARNA if needed, 
# though running Docker-in-Docker is complex, we assume host docker access 
# or use internal tools if possible. For simplicity, we install common libs).
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Copy built frontend from Stage 1 to backend's dist folder
# api.py is already configured to serve from "dist" folder
RUN mkdir -p dist
COPY --from=frontend-builder /app/frontend/dist ./dist

# Environment variables
ENV PORT=8000
ENV DATABASE_URL=sqlite:///rnabridge.db

# Expose the API port
EXPOSE 8000

# Start the application
CMD ["python", "api.py"]
