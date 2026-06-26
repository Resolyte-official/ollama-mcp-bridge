FROM python:3.10.15-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    g++ \
    gcc \
    python3-dev \
    libproj-dev \
    proj-data \
    proj-bin \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv
ARG VERSION=0.1.0
ENV SETUPTOOLS_SCM_PRETEND_VERSION=${VERSION}

COPY . ./

RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "ollama-mcp-bridge"]
