# Dockerfile for KisanMind backend (FastAPI)
# Uses a slim Python image for minimal size and fast start‑up

FROM python:3.12-slim AS builder
WORKDIR /app

# Install build deps (only needed for compiled packages)
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ .

# ---------- Runtime stage ----------
FROM python:3.12-slim
WORKDIR /app

# Copy only the installed packages from builder (much smaller)
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

# Expose the port FastAPI runs on (default 8000)
EXPOSE 8000

# Use Uvicorn to launch the app. Cloud Run injects $PORT env var.
ENV PORT 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "${PORT}", "--workers", "2"]
