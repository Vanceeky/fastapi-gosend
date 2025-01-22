FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

COPY uv.lock pyproject.toml /app/
RUN uv sync --frozen --no-install-project

COPY . /app
RUN uv sync --frozen

CMD ["uv", "run", "fastapi", "run", "src/main.py"]
