FROM noire-core

COPY src/noire /src/src/noire
COPY requirements.txt pyproject.toml /src/
RUN --mount=type=cache,target=/root/.cache \
    uv pip install /src --no-deps

WORKDIR /src
