FROM noir-core

COPY src/noir /src/src/noir
COPY requirements.txt pyproject.toml /src/
RUN --mount=type=cache,target=/root/.cache \
    uv pip install /src --no-deps

WORKDIR /src
