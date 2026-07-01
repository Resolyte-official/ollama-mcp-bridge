FROM python:3.10-slim

# Set up the working directory
WORKDIR /app

# Install system dependencies (Chromium, git, curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install --no-cache-dir uv

# Copy your project files (uv.lock, pyproject.toml, source code, etc.)
COPY . ./ 

# Sync dependencies using uv
RUN uv sync --no-dev

# Install Playwright's chromium browser binaries
RUN uv run playwright install chromium

# Set environment variables, expose port, and define entry point
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium
EXPOSE 8091

CMD ["uv", "run", "python", "main.py"]