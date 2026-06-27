FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	git \
	curl \
	&& rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

# Copy project metadata and source
COPY pyproject.toml uv.lock ./
COPY main.py ./

# Install dependencies declared in pyproject.toml using uv
RUN uv sync --no-dev --locked

CMD ["uv", "run", "python", "main.py"]
