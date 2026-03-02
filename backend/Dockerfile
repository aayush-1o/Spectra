# Spectra Backend — Multi-Stage Dockerfile
# Phase 5 optimisation: two stages reduce image size by ~40% by leaving
# gcc, libpq-dev, and pip cache out of the final runtime image.
#
# Stage 1 — builder: installs all Python dependencies into /install
# Stage 2 — runtime: copies only the installed packages + app code

# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

# Build dependencies (only needed to compile asyncpg, psycopg bindings, bcrypt)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy requirements first — Docker layer caching means pip only re-runs on changes
COPY requirements.txt .

# Install into a custom prefix so we can COPY just the packages to the runtime stage
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Runtime system dependency: libpq for asyncpg at runtime (not libpq-dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder stage
COPY --from=builder /install /usr/local

WORKDIR /app

# Copy application code (see .dockerignore for exclusions)
COPY . .

# Expose the API port
EXPOSE 8000

# Production entrypoint — use --workers 2 for multi-process in production
# In docker-compose the command is overridden with --reload for dev
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
