# syntax=docker/dockerfile:1
FROM python:3.14-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libc6-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=docker.io/astral/uv:0.10.2 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_PYTHON=python3.14 \
    UV_PROJECT_ENVIRONMENT=/app/.venv

COPY uv.lock pyproject.toml ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


FROM python:3.14-slim AS runtime

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -M -d /app -s /usr/sbin/nologin appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appgroup /app

WORKDIR /app

COPY --from=build --chown=appuser:appgroup /app .

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]