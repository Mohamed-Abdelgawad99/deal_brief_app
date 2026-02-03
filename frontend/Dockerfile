# frontend/Dockerfile
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files first (for caching layers)
COPY pyproject.toml uv.lock ./

# Install dependencies into the system python environment
# --no-dev excludes testing tools, keeping the image light
RUN uv sync --frozen --no-install-project --no-dev

# Copy the actual UI code
COPY . .

# Place the virtualenv in the path
ENV PATH="/app/.venv/bin:$PATH"

# Streamlit runs on port 8501 by default
EXPOSE 8501


ENTRYPOINT ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]