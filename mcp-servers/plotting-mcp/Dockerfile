FROM python:3.13-slim AS builder

# Install system dependencies required for Cartopy and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    gcc \
    libproj-dev \
    proj-data \
    proj-bin \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory and change ownership
WORKDIR /app
RUN chown app:app /app

# Switch to non-root user
USER app

# Copy project metadata, source code, and download script
COPY --chown=app:app uv.lock pyproject.toml README.md ./
COPY --chown=app:app src/ ./src/
COPY --chown=app:app scripts/download_cartopy_data.py ./

# Ensure the app can write to its cache directories for uv and Rust builds
RUN mkdir -p /home/app/.cache/uv && chown -R app:app /home/app/.cache
ENV XDG_CACHE_HOME=/home/app/.cache
ENV UV_CACHE_DIR=/home/app/.cache/uv

# Sync the project
RUN --mount=type=cache,target=/home/app/.cache/uv,uid=1000,gid=1000 \
    uv sync --no-dev --locked --no-editable

# Pre-download Cartopy map data to avoid runtime downloads
RUN /app/.venv/bin/python download_cartopy_data.py

FROM python:3.13-slim AS runner

# Install runtime dependencies for Cartopy
RUN apt-get update && apt-get install -y \
    libproj25 \
    libgeos-c1v5 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (same as builder stage)
RUN groupadd --gid 1000 app && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app

# Create app directory and set ownership
WORKDIR /app
RUN chown app:app /app

# Copy the environment, but not the source code
COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Copy Cartopy data cache from builder stage
ENV CARTOPY_DATA_DIR=/app/cartopy-data
RUN mkdir -p ${CARTOPY_DATA_DIR} && chown app:app ${CARTOPY_DATA_DIR}
COPY --from=builder --chown=app:app /home/app/.local/share/cartopy ${CARTOPY_DATA_DIR}

# Create matplotlib config directory
RUN mkdir -p /tmp/matplotlib && chown app:app /tmp/matplotlib
ENV MPLCONFIGDIR=/tmp/matplotlib

# Switch to non-root user
USER app

# Expose port
EXPOSE 9090

# Run the application
CMD ["/app/.venv/bin/plotting-mcp"]
