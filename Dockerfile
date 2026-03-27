FROM python:3.12-slim AS builder

WORKDIR /build

COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/

RUN pip install --no-cache-dir hatchling build && \
    python -m build --wheel

FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /build/dist/*.whl ./

RUN pip install --no-cache-dir *.whl && \
    rm -f *.whl

EXPOSE 8000

CMD ["mcp-fiscal-brasil"]
