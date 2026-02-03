# backend/Dockerfile
FROM ghcr.io/astral-sh/uv:python3.10-bookworm-slim

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# copting the dependency files first
COPY pyproject.toml uv.lock ./

# using uv to install dependencies into a virtualenv
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application
COPY . .

# Place the virtualenv in the path
ENV PATH="/app/.venv/bin:$PATH"

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]